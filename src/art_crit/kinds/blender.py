"""The `blender` kind: the agent models and renders in a Blender of its own, through the official Blender Lab
MCP server (https://projects.blender.org/lab/blender_mcp), and saves a .glb and/or renders in work/output/.
See SPEC.md "Kinds" and ADR-0025.

Each run gets its own windowless Blender (`blender -b --command blender_mcp --port N`, the add-on's background mode)
started in the run's work dir, so runs go in parallel and relative paths land in work/. The add-on is installed once
into an art-crit-owned Blender user dir (BLENDER_USER_RESOURCES), never into the user's own Blender."""

import contextlib
import hashlib
import json
import os
import shutil
import signal
import socket
import struct
import subprocess
import time
import urllib.request
from pathlib import Path

from ..util import CritError
from . import media
from .media import Media

MCP_VERSION = "1.0.3"
MCP_COMMIT = "2cea8d566dde07fbac28a61d698909d69724e853"  # tag v1.0.3
# The MCP server, run by uvx from the pinned commit. Not `uvx blender-mcp`: that name on PyPI is a different project.
MCP_SOURCE = f"git+https://projects.blender.org/lab/blender_mcp.git@{MCP_COMMIT}#subdirectory=mcp"
ADDON_URL = f"https://projects.blender.org/lab/blender_mcp/releases/download/v{MCP_VERSION}/mcp-{MCP_VERSION}.zip"
ADDON_SHA256 = "a7a9da816192502e5a0a202a396444e266b47d8fc4f74ad4698048bd43040707"
# The MCP server's tools at MCP_COMMIT (agy needs them by name to declare them up front; update with the pin).
TOOLS = (
    "execute_blender_code", "execute_blender_code_for_cli", "get_blendfile_summary_datablocks",
    "get_blendfile_summary_datablocks_for_cli", "get_blendfile_summary_missing_files",
    "get_blendfile_summary_missing_files_for_cli", "get_blendfile_summary_of_linked_libraries",
    "get_blendfile_summary_of_linked_libraries_for_cli", "get_blendfile_summary_path_info",
    "get_blendfile_summary_path_info_for_cli", "get_blendfile_summary_usage_guess",
    "get_blendfile_summary_usage_guess_for_cli", "get_object_detail_summary", "get_objects_summary",
    "get_python_api_docs", "get_screenshot_of_area_as_image", "get_screenshot_of_window_as_image",
    "get_screenshot_of_window_as_json", "jump_to_tab_by_name", "jump_to_tab_by_space_type",
    "jump_to_view3d_object_by_name", "jump_to_view3d_object_data_by_name", "render_thumbnail_to_path",
    "render_viewport_to_path", "search_api_docs", "search_manual_docs",
)
# Tools that need Blender's window; in background mode they only answer "not available", so the model never gets them.
HIDDEN_TOOLS = (
    "get_screenshot_of_area_as_image", "get_screenshot_of_window_as_image", "get_screenshot_of_window_as_json",
    "jump_to_tab_by_name", "jump_to_tab_by_space_type", "jump_to_view3d_object_by_name",
    "jump_to_view3d_object_data_by_name",
)
STARTUP_TIMEOUT_S = 60

MODEL_EXT = ".glb"
MAX_MODEL_BYTES = 15 * 1024 * 1024
GLB_MAGIC, GLB_JSON = 0x46546C67, 0x4E4F534A  # "glTF", "JSON"
# glTF extensions the viewer's three.js GLTFLoader can't read without decoders the site doesn't ship.
UNSUPPORTED_EXTENSIONS = {"KHR_draco_mesh_compression", "EXT_meshopt_compression", "KHR_texture_basisu"}


def blender_home():
    """The Blender user dir the add-on is installed into (BLENDER_USER_RESOURCES of every run)."""
    cache = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return cache / "art-crit" / f"blender-mcp-{MCP_VERSION}"


def read_glb(path):
    """A .glb's glTF JSON, or raises ValueError saying what's wrong with the container."""
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("not a glTF binary (.glb)")
    magic, version, length = struct.unpack_from("<III", data)
    if magic != GLB_MAGIC:
        raise ValueError("not a glTF binary (.glb)")
    if version != 2:
        raise ValueError(f"glTF binary version {version}, expected 2")
    if length != len(data):
        raise ValueError("truncated .glb")
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != GLB_JSON or 20 + chunk_length > len(data):
        raise ValueError(".glb without a JSON chunk")
    try:
        gltf = json.loads(data[20:20 + chunk_length])
    except ValueError:
        raise ValueError(".glb with unreadable JSON")
    if not str((gltf.get("asset") or {}).get("version", "")).startswith("2."):
        raise ValueError("not glTF 2.0")
    if not gltf.get("scenes"):
        raise ValueError(".glb without a scene to show")
    return gltf


def triangles(gltf):
    """Triangles drawn by the glTF's mesh primitives (mode 4 = TRIANGLES, the default), counted once per mesh."""
    accessors = gltf.get("accessors") or []
    total = 0
    for mesh in gltf.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            if prim.get("mode", 4) != 4:
                continue
            index = prim.get("indices", (prim.get("attributes") or {}).get("POSITION"))
            if isinstance(index, int) and 0 <= index < len(accessors):
                total += accessors[index].get("count", 0) // 3
    return total


def do_model(src, dest_dir, name):
    if src.stat().st_size > MAX_MODEL_BYTES:
        return None, f"{name}: larger than {MAX_MODEL_BYTES // (1024 * 1024)} MB"
    try:
        gltf = read_glb(src)
    except ValueError as e:
        return None, f"{name}: {e}"
    unsupported = sorted(UNSUPPORTED_EXTENSIONS & set(gltf.get("extensionsRequired") or ()))
    if unsupported:
        return None, f"{name}: needs {', '.join(unsupported)}, which the viewer can't decode"
    shutil.copy(src, dest_dir / name)
    return {"type": "model", "file": name, "bytes": src.stat().st_size, "meshes": len(gltf.get("meshes") or []),
            "triangles": triangles(gltf), "animations": len(gltf.get("animations") or [])}, None


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _kill(proc):
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    proc.wait()


class Blender(Media):
    name = "blender"
    tools = ("blender", "uvx", "ffmpeg", "ffprobe")
    tools_hint = "Blender 5.1+ (blender.org), uv (docs.astral.sh/uv), ffmpeg"
    needs_mcp = True
    handlers = {**media.HANDLERS, MODEL_EXT: do_model}
    what = "render or .glb"

    def __init__(self, home=None):
        self.home = Path(home) if home else blender_home()

    def prepare(self):
        """Once per batch: install the add-on into our Blender user dir (if it isn't yet) and fetch the MCP server
        into uv's cache, so no run waits on a download while its harness waits for the server to connect."""
        if not (self.home / "extensions" / "user_default" / "mcp" / "blender_manifest.toml").is_file():
            self.home.mkdir(parents=True, exist_ok=True)
            zip_path = self.home / f"mcp-{MCP_VERSION}.zip"
            try:
                req = urllib.request.Request(ADDON_URL, headers={"User-Agent": "art-crit"})
                data = urllib.request.urlopen(req, timeout=120).read()
            except OSError as e:
                raise CritError(f"cannot download the Blender MCP add-on from {ADDON_URL}: {e}")
            if hashlib.sha256(data).hexdigest() != ADDON_SHA256:
                raise CritError(f"the Blender MCP add-on at {ADDON_URL} doesn't match its pinned sha256")
            zip_path.write_bytes(data)
            r = subprocess.run(["blender", "-b", "--factory-startup", "--command", "extension", "install-file",
                                "-r", "user_default", "-e", str(zip_path)],
                               env=self.env(), capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                raise CritError(f"cannot install the Blender MCP add-on: {(r.stdout + r.stderr).strip()[-300:]}")
        r = subprocess.run(["uvx", "--from", MCP_SOURCE, "blender-mcp", "--help"], capture_output=True, text=True,
                           timeout=600)
        if r.returncode != 0:
            raise CritError(f"cannot fetch the Blender MCP server ({MCP_SOURCE}): {r.stderr.strip()[-300:]}")

    def env(self):
        return {**os.environ, "BLENDER_USER_RESOURCES": str(self.home)}

    @contextlib.contextmanager
    def agent_session(self, work_dir, harness_dir):
        """A windowless Blender for one run, listening on its own port; yields the run's MCP servers. Blender's log is
        harness/blender.log. Killed (with its process group) when the agent is done."""
        proc, port = None, None
        with open(Path(harness_dir) / "blender.log", "ab") as log:
            for _ in range(3):  # another run may grab the free port first; Blender then exits
                port = free_port()
                proc = subprocess.Popen(["blender", "-b", "--online-mode", "--command", "blender_mcp", "--port", str(port)],
                                        cwd=work_dir, env=self.env(), stdin=subprocess.DEVNULL, stdout=log,
                                        stderr=subprocess.STDOUT, start_new_session=True)
                deadline = time.monotonic() + STARTUP_TIMEOUT_S
                while proc.poll() is None and time.monotonic() < deadline and not port_open(port):
                    time.sleep(0.2)
                if proc.poll() is None and port_open(port):
                    break
                _kill(proc)
            else:
                raise CritError(f"Blender didn't start its MCP server (see {Path(harness_dir) / 'blender.log'})")
        try:
            yield {"blender": {"command": "uvx", "args": ["--from", MCP_SOURCE, "blender-mcp"],
                               "env": {"BLENDER_MCP_PORT": str(port)}, "hidden": list(HIDDEN_TOOLS),
                               "tools": [t for t in TOOLS if t not in HIDDEN_TOOLS]}}
        finally:
            _kill(proc)
