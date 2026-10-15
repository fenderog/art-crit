# 0025. Blender kind: a windowless Blender per run, driven through the official MCP server

- Status: Accepted
- Date: 2026-10-15

## Context

We want to compare what models make in Blender: modeling, materials, lighting, renders. The comparison should be
judged by eye on the site, both as renders and as a model you can turn around. Blender Lab publishes an official MCP
server (projects.blender.org/lab/blender_mcp, v1.0.3). It has two parts: an add-on that runs inside Blender and serves
a local TCP socket, and a stdio MCP server (`blender-mcp`) that relays tool calls (run Python, search the API and manual
docs, render, screenshot the window, jump to a view) to that socket. The add-on also has a background mode
(`blender -b --command blender_mcp --port N`) that needs no window.

A batch runs many agents in parallel as local processes (ADR-0009), across harnesses that convert into pi's session
format (ADR-0007). Three of them (pi, Claude Code, Codex) can be given MCP servers per run; agy, Grok Build and Muse
Code can't, at least not without touching the user's global config.

## Decision

- `blender` is a kind (ADR-0018). Its runs need MCP (`Kind.needs_mcp`), so planning refuses harnesses without
  `supports_mcp`.
- Each run gets **its own windowless Blender** on a free port, started in the run's `work/` by `Kind.agent_session` and
  killed when the agent ends. The add-on is installed once into an art-crit-owned Blender user dir
  (`BLENDER_USER_RESOURCES`), never into the user's own Blender. The MCP server runs from a pinned commit through `uvx`.
- The MCP config is per run, passed in the way each harness allows: Claude Code gets `--mcp-config` with
  `--strict-mcp-config`, Codex gets `-c mcp_servers.*` overrides, and pi gets a project `work/.pi/mcp.json` trusted
  with `--approve`. Nothing is written to `~/.pi`, `~/.claude` or `~/.codex`.
- The 7 tools that need a window (3 screenshot, 4 `jump_to_*`) are hidden from every model. The brief says to check work
  by rendering to a file and looking at it.
- Output is the media step plus `.glb`: renders are images, and the model is a `model` item checked as glTF 2.0
  binary that the viewer can decode.
- The site shows a `.glb` with a vendored three.js bundle (GLTFLoader + OrbitControls), loaded only on click. A .glb is
  data, so it's parsed on the site's origin rather than framed (ADR-0004 is about code); `blob:` is added to `img-src`
  and `connect-src` for the textures three.js decodes.

## Alternatives considered

- **A Blender with a window per run** (the add-on's interactive mode): the screenshot tools would work, but every run
  opens a Blender window on the user's desktop. The "screenshot" can be had from a render anyway.
- **Blender's full UI in a Linux container with a virtual display** (the repo's `blender_headless.py` + weston):
  screenshots and deferred replies would work, but Docker on macOS has no GPU, so EEVEE and the viewport would render in
  software, several times slower. That's a bad trade when renders are the output. It also brings an image to build and
  a shared volume at matching paths. Worth revisiting on a Linux host with a GPU.
- **Our own small MCP server** (stdlib, run `bpy` code + render + export): leaner and identical across harnesses, but
  the user asked for the official server, and its docs-search tools are part of what is being tested.
- **ahujasid/blender-mcp** (the popular third-party one, which is also what `uvx blender-mcp` on PyPI resolves to): has
  extras (Poly Haven, Hyper3D asset generation) that would make runs unequal, and it needs the GUI add-on.
- **pi's codemode exposure** for the MCP tools (the model writes JavaScript that calls them in pi's sandbox): lets one
  call chain and filter many Blender calls, but no other harness works that way, so pi runs would show fewer turns, tool
  calls and tokens for reasons unrelated to the model. `direct` exposure keeps the three harnesses comparable. It could
  be an opt-in variant later.
- **`<model-viewer>`** for the site: one file with nice defaults, but bigger and less controllable than three.js, which
  the web kind already depends on in spirit.

## Consequences

- Update (2026-10-15): agy, Grok Build and Muse Code take Blender too, so all six harnesses do. agy and Muse read MCP
  servers only from the user's global config (Muse ignores a project file, and its `--trust-workspace` turns on
  sub-agents), so with the user's consent each got one permanent `art-crit-blender` entry pointing at a stdlib proxy
  in `~/.cache/art-crit/`. Inside a run the proxy reads `<run>/harness/art-crit-mcp.json` and runs that run's server,
  dropping the hidden tools. Elsewhere it is a server with no tools, so the user's own sessions are unaffected. Grok
  gets a per-run project config that runs the same proxy (it can't hide tools itself), with `GROK_FOLDER_TRUST=0`
  rather than `--trust`, which would record every run dir. Grok's models reach MCP tools only through
  `search_tool`/`use_tool`, an extra step the other harnesses don't have; keep that in mind when comparing.
- Claude Code MCP runs can't use `--safe-mode`, which drops
  `--mcp-config` (measured). They use `--setting-sources=`, `--strict-mcp-config` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY`
  instead, and the system prompt was checked to match safe mode's except for the server's tools. Re-check that after
  Claude Code updates.
- pi MCP runs pass `--approve`, which would also load other project resources in `work/`. The work dir is fresh, but
  an agent could add some mid-run; they only load at the next start, which doesn't happen.
- A single MCP call is limited to 5 minutes by the server's socket timeout, and background mode can't defer replies,
  so very long renders fail. The brief says to keep renders quick.
- Bumping the MCP server means updating `MCP_VERSION`, `MCP_COMMIT` and `ADDON_SHA256` in `kinds/blender.py`. The
  install dir is versioned, so a new version installs next to the old one.
- The repo grows by up to 15 MB per published .glb. Watch it as with Godot engines (ADR-0008).
