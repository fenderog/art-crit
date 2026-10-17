"""art-crit video: the layouts' geometry, the request checks, real videos made from a fixture site (ffmpeg + Chrome, no
model), recording a game, and the local-only API (`POST api/video`, polling, fetching a file)."""

import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from art_crit import video
from art_crit.cli import main
from art_crit.serve import serve_in_thread
from art_crit.site import rebuild
from art_crit.util import CritError
from test_web_kind import in_thread

REPO = Path(__file__).resolve().parents[1]
FIXTURE_DATA = REPO / "tests/fixtures/site/data"
HIGH = "model-x-high-20260102-000000"
OTHER = "model-y-high-20260102-000000"
GAME = "game-z-high-20260102-000000"

needs_tools = pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")

GAME_HTML = """<!doctype html><body style="margin:0;background:#123"><div id=b style="position:absolute;width:60px;height:60px;background:#f80"></div>
<script>let x=0;setInterval(()=>{x=(x+7)%300;document.getElementById('b').style.left=x+'px';document.getElementById('b').style.top=(x*0.7)+'px'},30)</script>"""


@pytest.fixture
def site(tmp_path):
    """A repo root whose docs/ has the viewer, the fixture pages, a second good run on `art` and a tiny "game"."""
    root = tmp_path / "site"
    docs = root / "docs"
    docs.mkdir(parents=True)
    for f in REPO.glob("docs/*.html"):
        shutil.copy(f, docs / f.name)
    shutil.copytree(REPO / "docs/assets", docs / "assets")
    shutil.copytree(FIXTURE_DATA, docs / "data")
    runs = docs / "data/art/runs"
    shutil.copytree(runs / HIGH, runs / OTHER)
    record = json.loads((runs / HIGH / "run.json").read_text())
    (runs / OTHER / "run.json").write_text(json.dumps({**record, "id": OTHER, "model": "other-org/model-y", "effort": "high"}))
    (runs / GAME).mkdir()
    (runs / GAME / "index.html").write_text(GAME_HTML)
    game = {**record, "id": GAME, "model": "game-org/model-z", "output": {"kind": "godot", "ok": True, "verified": True, "error": None, "entry": "index.html"}}
    (runs / GAME / "run.json").write_text(json.dumps(game))
    rebuild(root)
    return root


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    return data["streams"][0]["width"], data["streams"][0]["height"], float(data["format"]["duration"])


def test_grid_tiles_fit_the_canvas_without_overlapping():
    width, height = video.LAYOUTS["grid"]
    for n in range(2, video.MAX_RUNS + 1):
        tiles, label = video.grid_tiles(n)
        assert len(tiles) == n
        for x, y, side in tiles:
            assert x >= 0 and x + side <= width and y >= 300 and y + side + label <= height - 100 and side >= 200
        for i, (x, y, side) in enumerate(tiles):
            for x2, y2, side2 in tiles[i + 1:]:
                assert x + side <= x2 or x2 + side2 <= x or y + side + label <= y2 or y2 + side2 + label <= y


def test_a_caption_names_the_model_and_what_it_cost():
    run = {"model": "openrouter/deepseek/deepseek-v4.1-flash@deepinfra", "effort": "max",
           "metrics": {"duration_ms": 98000, "tokens_total": 10400, "cost_usd": 0.318}}
    assert video.run_info(run) == {"vendor": "deepseek", "name": "deepseek-v4.1-flash", "effort": "max",
                                   "metrics": ["1m 38s", "10k tokens", "$0.32"]}
    assert video.run_info({"model": "x", "effort": "low", "metrics": {"cost_usd": 0}})["metrics"] == []  # unreported cost isn't shown


@needs_tools
def test_a_bad_request_is_refused_before_anything_starts(site):
    for ids, layouts, seconds, message in [
        ([HIGH], None, 6, "compares 2 to 12"),
        ([HIGH, "nope"], None, 6, "no such run"),
        ([HIGH, "model-x-low-20260102-000000"], None, 6, "failed runs"),
        ([HIGH, OTHER], ["square"], 6, "unknown layout"),
        ([HIGH, OTHER], None, 99, "between 2 and 20"),
    ]:
        with pytest.raises(CritError, match=message):
            video.check_request(site, "art", ids, layouts, seconds)
    with pytest.raises(CritError, match="no such page"):
        video.check_request(site, "missing", [HIGH, OTHER], None, 6)


@needs_tools
def test_every_layout_is_made_from_pictures_and_a_video(site, tmp_path):
    said = []
    out = tmp_path / "out"
    files = in_thread(video.make_videos, site, "art", [HIGH, OTHER], None, 2, out, said.append)
    assert [f.name.rsplit("-", 1)[1] for f in files] == ["reveal.mp4", "grid.mp4", "wide.mp4"]
    sizes = {f.stem.rsplit("-", 1)[1]: probe(f) for f in files}
    assert sizes["reveal"][:2] == (1080, 1920) and sizes["grid"][:2] == (1080, 1920) and sizes["wide"][:2] == (1920, 1080)
    assert sizes["reveal"][2] == pytest.approx(2.2 + 2 * 2 + 2.2, abs=0.4)  # intro, a run each, outro
    assert sizes["grid"][2] == pytest.approx(2.2 + 2 + 2.2, abs=0.4)  # intro, everyone at once, outro
    assert not list(out.glob("*.txt"))  # no leftovers beside the videos
    assert any("recording 2/2" in s for s in said) and any("composing wide" in s for s in said)


@needs_tools
def test_a_game_is_recorded_not_just_its_thumbnail(site, tmp_path):
    [reveal] = in_thread(video.make_videos, site, "art", [GAME, HIGH], ["reveal"], 2, tmp_path / "out")
    assert probe(reveal)[:2] == (1080, 1920)
    frames = tmp_path / "frames"
    frames.mkdir()
    for n, at in enumerate((2.9, 3.7)):  # while the game (the first run, 2.2 to 4.2 s) is on screen: the square moves between two frames
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", str(reveal), "-frames:v", "1", str(frames / f"{n}.png")], check=True)
    assert (frames / "0.png").read_bytes() != (frames / "1.png").read_bytes()


@needs_tools
def test_the_cli_prints_the_files_and_the_link_for_the_post(site, tmp_path, capsys):
    rc = in_thread(main, ["video", "art", HIGH, OTHER, "-l", "wide", "-d", "2", "-o", str(tmp_path / "v"), "--root", str(site)])
    out = capsys.readouterr().out
    assert rc == 0 and out.count(".mp4") == 1 and (tmp_path / "v").is_dir()
    assert f"link for the post: https://fenderog.com/art-crit/compare.html?p=art&r={HIGH}%2C{OTHER}" in out
    assert main(["video", "art", HIGH, "--root", str(site)]) == 1  # one run isn't a comparison


# --- the local API -------------------------------------------------------------------------------------------------

def call(base, path, body=None, headers=None):
    request = urllib.request.Request(base + path, method="POST" if body is not None else "GET", headers={"Content-Type": "application/json", **(headers or {})},
                                     data=None if body is None else json.dumps(body).encode())
    try:
        with urllib.request.urlopen(request) as res:
            return res.status, res.read(), res.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers


@needs_tools
def test_the_api_makes_a_video_in_the_background_and_serves_only_its_files(site):
    server = serve_in_thread(site / "docs")
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    try:
        assert json.loads(call(base, "api/local")[1])["video"] is True
        for body, error in [({"runs": [HIGH]}, "compares 2 to 12"), ({"runs": "x"}, "expected runs"), ({"runs": [HIGH, OTHER], "seconds": "6"}, "whole number")]:
            status, out, _ = call(base, "api/video?p=art", body)
            assert status == 400 and error in json.loads(out)["error"]
        assert call(base, "api/video?p=../art", {"runs": [HIGH, OTHER]})[0] == 400

        status, out, _ = call(base, "api/video?p=art", {"runs": [HIGH, OTHER], "layouts": ["wide"], "seconds": 2})
        assert status == 200
        job = json.loads(out)["job"]
        assert call(base, "api/video?p=art", {"runs": [HIGH, OTHER]})[0] == 400  # one at a time
        for _ in range(240):
            state = json.loads(call(base, f"api/video?job={job}")[1])
            if state["state"] != "running":
                break
            time.sleep(0.5)
        assert state["state"] == "done" and len(state["files"]) == 1 and state["link"].endswith(f"&r={HIGH}%2C{OTHER}")
        status, data, headers = call(base, f"api/video/file?job={job}&name={state['files'][0]}")
        assert status == 200 and headers["Content-Type"] == "video/mp4" and b"ftyp" in data[:32]
        assert "Access-Control-Allow-Origin" not in headers  # another website can't read it
        for name in ("../../docs/index.html", "page.json", ""):
            assert call(base, f"api/video/file?job={job}&name={name}")[0] == 404
        assert (site / "videos/art" / state["files"][0]).is_file()  # outside docs/: never published
        assert call(base, "api/video?job=nope")[0] == 404
    finally:
        server.shutdown()
        server.server_close()


def test_the_api_refuses_other_hosts_and_other_sites(site):
    server = serve_in_thread(site / "docs")
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}/"
    try:
        evil = {"Host": f"evil.example:{port}", "Origin": f"http://evil.example:{port}"}
        assert call(base, "api/video?p=art", {"runs": [HIGH, OTHER]}, evil)[0] == 403
        assert call(base, "api/video?job=x", None, {"Host": f"evil.example:{port}"})[0] == 403
        assert call(base, "api/video?p=art", {"runs": [HIGH, OTHER]}, {"Origin": "https://evil.example"})[0] == 403
        req = urllib.request.Request(base + "api/video?p=art", method="POST", data=b"{}", headers={"Content-Type": "text/plain"})
        with pytest.raises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(req)
        assert e.value.code == 415
        assert not (site / "videos").exists()
    finally:
        server.shutdown()
        server.server_close()
