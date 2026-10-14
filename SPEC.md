# art-crit spec

This repo is both the CLI (`src/art_crit/`) and the static site (`docs/`, published on Cloudflare Pages
at `https://fenderog.com/art-crit/`). The CLI writes JSON and files into `docs/data/` and `docs/engines/`,
and the viewer pages fetch that JSON in the browser. Cloudflare's build copies `docs/` to
`cloudflare-dist/` and compresses Godot WASM files to fit Pages' 25 MiB asset limit; the viewer itself
has no build step. See Deployment below.

Guiding rule: **simple and lean.** The CLI is standard-library Python only (argparse, json, hashlib,
tomllib, http.server, subprocess). The site is vanilla JS ES modules, with one pinned, vendored dependency
(`marked` for Markdown tokenization). No frameworks and no bundler.

## Vocabulary

- **Page**: one prompt or task, such as `voxel-horse`.
- **Run**: one model × effort level attempt at a page's task, kept in one directory (`<batch>/<run id>/`, see
  "Run directory"). `art-crit import` publishes it to the site.
- **Kind**: what a page's runs produce. `godot` = a Godot project, published as a playable web build;
  `media` = image and/or video files; `web` = a web page (HTML + ES modules + npm packages), published as one
  self-contained `index.html` packaged with esbuild. Every run of a page has the page's kind.

## Site layout (the data contract between the CLI and the viewer)

```
docs/
  .nojekyll                     # still used by the old GitHub Pages URL
  index.html                      # home: list of pages            (reads data/pages.json)
  page.html?p=<slug>              # one page: runs table + gallery (reads data/<slug>/page.json)
  run.html?p=<slug>&r=<run_id>    # one run: tabs Game | Transcript | Source | Metrics
  compare.html?p=<slug>[&r=<id>,<id>]   # side by side: all runs of the page, or just the listed ones
  play.html?p=<slug>&r=<run_id>   # one run's output alone, full window (the compare cards' pop-out target)
  assets/                         # shared JS/CSS
  engines/<sha12>/godot.wasm      # deduplicated Godot engine files, one dir per unique engine
  engines/<sha12>/godot.js
  engines/<sha12>/godot.audio.worklet.js
  engines/<sha12>/godot.audio.position.worklet.js
  data/
    pages.json                    # [PageSummary]
    <slug>/page.json              # Page
    <slug>/ranking.json           # optional: {"ranks": {"<run id>": 1, ...}, "updated": "<iso>"}, the owner's ranking (see Ranking)
    <slug>/runs/<run_id>/
      run.json                    # Run
      thumb.png                   # optional (godot)
      game/index.html, index.pck, index.png, index.icon.png, index.apple-touch-icon.png   # godot
      media/<file>, media/<name>.poster.jpg                                              # media
      game/index.html             # web: the packaged page, one file (cleaned and secret-scanned like source)
      session/conversation.json   # cleaned (see Cleaning)
      session/stderr.txt          # optional, cleaned
      source/...                  # project files the model wrote
```

All paths inside JSON are **relative to the run directory** (for Run) or to `docs/` (for PageSummary.thumb).

### PageSummary (element of `data/pages.json`)
```json
{ "slug": "voxel-horse", "title": "Voxel horse", "kind": "godot", "n_runs": 3,
  "models": ["openai-codex/gpt-6-sol"], "updated": "2026-09-26T07:15:57Z",
  "thumb": "data/voxel-horse/runs/gpt-6-sol-high-20260926-001158/thumb.png" }
```
`thumb` is taken from the most recent run that has one (its run's `thumb` path), or `null`.

### Page (`data/<slug>/page.json`)
```json
{ "slug": "voxel-horse", "title": "Voxel horse", "kind": "godot",
  "prompt": "<contents of prompt.md, the originating prompt; refreshed on every import>",
  "final_prompt": "<the full brief each run received: first user message of the cleaned transcript; null if none>",
  "created": "2026-09-26T07:12:42Z", "updated": "2026-09-26T07:15:57Z",
  "runs": ["<Run with rank; see below>"] }
```

### Run (`run.json`, and each element of `page.json.runs`)
```json
{
  "id": "gpt-6-sol-high-20260926-001158",
  "page": "voxel-horse",
  "model": "openai-codex/gpt-6-sol",
  "effort": "high",
  "kind": "godot",
  "started_at": "2026-09-26T07:12:42Z",
  "batch": "2026-09-26-001158-voxel-horse",
  "harness": { "name": "pi", "version": "0.87.1" },
  "state": "complete",
  "error": null,
  "route": null,
  "metrics": {
    "duration_ms": 196192, "cost_usd": 0.146, "tool_calls": 16, "turns": 17,
    "tokens_total": 32732, "tokens_input": 25280, "tokens_output": 7452,
    "tokens_reasoning": 3073, "tokens_cache_read": 105984
  },
  "thumb": "thumb.png",
  "output": { "kind": "godot", "entry": "game/index.html", "engine": "41560f8755ed",
             "godot": "4.7.2.stable.official.ed1daf0bf", "threads": false,
             "ok": true, "verified": true, "error": null },
  "session": { "conversation": "session/conversation.json", "stderr": "session/stderr.txt" },
  "source": { "root": "source/", "files": ["README.md", "project.godot", "scenes/main.tscn", "scripts/main.gd"] }
}
```
- `output`, `session`, `source` and `thumb` can each be `null`.
- `rank` exists only in `page.json.runs` (never in `run.json`): the run's rank from `ranking.json`, or `null`.
- `kind` is the page's kind (runs imported before kinds existed have none; the viewer treats that as `godot`). Importing
  into a page of another kind is an error. `batch` = the batch directory's name (runs published before run
  directories hold the old model directory's name).
- **`state`, `output.ok`, `output.verified`: three questions, three places.** `state` is only what the agent did:
  `queued | running | complete | failed | timeout`; `error` is the agent's error (harness exit, timeout, an assistant
  `stopReason: error`, or a note that a pinned OpenRouter run was served outside its upstreams). `output.ok` /
  `output.error` are what the kind step made of the work (Godot export, packaging, media normalization): a run
  whose export failed is `state: complete` with `output: {kind, ok: false, error: "Godot export failed: …",
  verified: null}`. `output.verified` is whether the check passed (booted, loaded offline, files readable), `null`
  when it wasn't run. `output` is `null` only when the agent didn't complete (there was nothing to export).
- `output` carries its own `kind` and the kind's fields (see Kinds): `godot` = `entry`, `engine`, `godot`, `threads`;
  `web` = `entry`, `bytes`, `esbuild`; `media` = `items`, each `{type: "image"|"video", path: "media/<file>", width,
  height, bytes}` plus, for a video, `duration_s, poster: "media/<name>.poster.jpg", transcoded` and `trimmed: true`
  when it was cut to 10 s (width/height can be `null` for an SVG without a size). Paths are relative to the run
  directory. `thumb` = `thumb.png` (the verify step's first screenshot) for godot and web, the first image's path or
  the first video's poster for media. Model-written text (SVGs, the packaged page) is cleaned and secret-scanned like
  source. The run's `source` never includes `node_modules/`; for media it holds only text files of at most 512 KB,
  and `output/` only for the files there that aren't media (a generator script kept in `./output/`).
- `id` = `<model name after the last "/", lowercased>-<effort>-<YYYYMMDD-HHMMSS of the batch>`, with `-cc` after the
  model for Claude Code runs; URL/filesystem-safe: a pinned OpenRouter route (`@…`, which can contain `/` itself) is split
  off first and appended as `-via-<route>`, e.g. `…flash@deepinfra/fp8` → `deepseek-v4.1-flash-via-deepinfra-fp8-low-20261001-101500`;
  anything else outside `[a-z0-9.-]` becomes `-`. It is also the run directory's name; two runs of a batch with one id
  are refused before anything starts.
- `harness` = the agent program and its version; `metrics` as in "Metrics". `metrics.cost_estimated: true` is present for Muse Code API-equivalent estimates (not subscription charges); `metrics.cost_estimate_proxy: "meta/muse-wonder-1.0"` also appears when Wonder Standard's API rate is used as a proxy for an unpriced Wonder variant.
- `route` = what the harness reports about routing, for a pi `openrouter/` run, else `null`:
  `{"requested": {"only": [...], "allow_fallbacks": false}, "served": [...], "cost_usd": 0.00085, "pi_cost_usd": 0.00038}`.
  `requested` is `null` for an unpinned run (OpenRouter chose the upstream); the rest is recorded either way.
  `served` = the upstreams that served the run, in order, as OpenRouter names them ("DeepInfra", "AtlasCloud").
  They're matched to the requested slugs by `upstream_key()` (lowercase alphanumerics of the name, and of the slug
  before its `/variant`: `atlas-cloud/fp8` and "AtlasCloud" → `atlascloud`); one outside `requested.only` is appended
  to `error`. `cost_usd` = what OpenRouter charged (the sum of each response's `usage.cost`), `null` when no response
  reported one; `pi_cost_usd` = pi's own estimate. For an OpenRouter run `metrics.cost_usd` is `cost_usd` when present:
  pi prices every OpenRouter call at one catalog rate whatever upstream served it (≈ 2–7× too low on real runs).

## Run directory (what `art-crit run` writes and `art-crit import` publishes)

```
<run.dir>/<YYYY-MM-DD-HHMMSS>-<page slug>/      # a batch
  batch.json  prompt.md                         # the batch's record (see Resume) and the originating prompt
  <run id>/                                     # one run
    run.json                                    # the run's record: the Run above, minus rank, thumb, session and source;
                                                #   output = {kind, ok, error, verified} (null until the kind step ran)
    work/                                       # the agent's working dir, empty at start; nothing else is ever written here
    harness/                                    # session file(s), stdout (events.jsonl), stderr.txt, brief.md, route.jsonl,
                                                #   conversation.json (the session in pi's format): never published except the
                                                #   transcript and a non-empty stderr
    output/                                     # what the kind made: Godot export (+ verification/), the packaged page
                                                #   (+ verification/), or normalized media + manifest.json
```
`art-crit import` takes one run directory or a batch directory and publishes each run: cleans and secret-scans, copies
`run.json` (adding `thumb`, `output`'s kind fields, `session` and `source`), `harness/conversation.json` as
`session/conversation.json`, `work/` as `source/` and the kind's `output/`, then rebuilds. The page slug is the run's
`page` (`--page` overrides it); the title = the slug with dashes turned into spaces and the first letter capitalized.
The page's prompt is the batch directory's `prompt.md`. Effort-run folders (`fe-model-effort-fanout/1`) are no longer read.

## Godot engine dedupe (proven in `../spike/build.py`)

1. The engine files are `index.wasm`, `index.js`, `index.audio.worklet.js`, `index.audio.position.worklet.js`.
   sha12 = the first 12 hex characters of sha256 over the four files' bytes, concatenated in that order.
2. If `docs/engines/<sha12>/` doesn't exist, copy them there as `godot.wasm`, `godot.js`, `godot.audio.worklet.js`, `godot.audio.position.worklet.js`.
3. Copy the other export files (except `export-manifest.json`, `verification/`, and the engine files) from `output/` into `runs/<id>/game/`.
4. Rewrite `game/index.html`. `rel` = the relative path from the game dir to `docs/engines/<sha12>/godot`:
   - `<script src="index.js"></script>` → `<script src="{rel}.js"></script>`
   - in `const GODOT_CONFIG = {...};`: `executable` = rel, **`mainPack` = "index.pck"** (required), and rename the
     `fileSizes` key `index.wasm` → `{rel}.wasm`.
5. Refuse an export with `threads: true` (from export-manifest.json, or `const GODOT_THREADS_ENABLED = true` in the html)
   with a clear error, unless `--allow-threads` is given. With the flag, store `"threads": true`.
6. `verification/frame-1.png` → `runs/<id>/thumb.png`.

## Cleaning (always runs on text files before they are written to docs/)

1. Remove every `thinkingSignature` key and every `encrypted_content` key, at any depth (a `thinkingSignature`
   value may be a JSON string that contains `encrypted_content`; dropping the whole key is enough).
2. Rewrite path prefixes in all strings: the user's home dir → `~`, plus extra rewrites from `art-crit.toml`:
   ```toml
   [clean]
   rewrite = { "/Volumes/M2SSD" = "<vol>" }
   ```
3. Drop these keys at any depth: `pid`, `completionOwnerId`, `sessionId`, `sessionFile`, `sessionRoot`, `launchContractDigest`.
4. Secret scan over the cleaned text of every published file (the transcript, stderr, source files, SVGs and the packaged page).
   Patterns: `sk-[A-Za-z0-9_-]{20,}`, `ghp_[A-Za-z0-9]{30,}`, `github_pat_[A-Za-z0-9_]{30,}`, `gho_[A-Za-z0-9]{30,}`,
   `AKIA[0-9A-Z]{16}`, `xox[baprs]-[A-Za-z0-9-]{10,}`, `-----BEGIN [A-Z ]*PRIVATE KEY-----`,
   `(?i)(api[_-]?key|secret|token|password)["'\s:=]+[A-Za-z0-9_\-/+]{24,}`.
   Any hit aborts the import **before anything is written**. The error prints file:line and the match masked
   (first 4 characters + `…`). With `--redact`, each match is replaced with `[REDACTED]` and the import continues.
5. Image data (the base64 `data` of `{type: "image"}` blocks in session JSON) is set aside before steps 2 and 4 and
   put back after: it's binary, so rewrites could corrupt it and the scan finds random matches (`AKIA…`) in it.
   Data that isn't plain base64 stays in place and is scanned.
6. JSONL files are cleaned line by line. Source files, stderr, SVGs and the packaged page get steps 2 and 4 only.

## CLI (`art-crit`, run from the repo root, or pass `-C/--root`)

```
art-crit import <run-dir | batch-dir> [-p/--page SLUG] [-t/--title TEXT] [-r/--redact] [-a/--allow-threads] [-n/--dry-run]
art-crit list                      # pages and their runs
art-crit rm <slug> [<run_id>] [-f/--failed] [-y/--yes]   # remove a run (or a whole page); --failed removes every failed run instead, then rebuild
art-crit rename <slug> <new> [-t/--title TEXT]   # move a page to a new slug (rewrites each run.json `page`), then rebuild
art-crit rebuild                   # regenerate page.json + pages.json from runs/*/run.json; delete engines no run references
art-crit serve [-p/--port 8000]    # serve docs/ locally: Access-Control-Allow-Origin: *, .wasm as application/wasm, NO COOP/COEP headers
                                #   plus the local-only ranking API (see Ranking); accept queue 64 for concurrent ES modules
art-crit publish [-m MSG]          # git add docs && git commit && git push (Cloudflare Pages builds main)
art-crit run ...                   # run agents locally, then import (see "Running benchmarks")
art-crit models [SEARCH] [-H/--harness pi|claude-code|agy|grok-build|muse-code|codex]   # models the harness can run; with SEARCH also their effort levels
```
Every long option has a single-dash short form (shown as `-p/--page`); the short forms are listed with each command.
- `import` is idempotent. Re-importing the same directory replaces runs with the same id.
- `import` prints a short summary per run: id, engine stored or reused, bytes written, paths rewritten, secret hits.
- `--failed` removes runs where the agent didn't finish (`state`), the kind step failed (`output.ok`) or the check failed (`output.verified`); it lists them with the reason and asks first unless `-y/--yes`.
- `--dry-run` does all the work, including the secret scan, in a temp dir and writes nothing to docs/.
- Errors go to stderr with a non-zero exit code, and there are no tracebacks for expected errors.

## Running benchmarks (`art-crit run`)

Runs one prompt through one or more models × effort levels on this machine with a **harness** (the agent program;
pi or Claude Code), turns each run's work into its kind's output and verifies it, then imports everything into one page.

```
art-crit run PROMPT | -f/--prompt-file FILE
    -k, --kind godot|media|web what the agents produce (default: the existing page's kind, else godot); must match it
    -m, --model MODEL[@UPSTREAMS][:LEVELS]  repeatable. UPSTREAMS: comma-separated OpenRouter provider slugs, as
                        OpenRouter lists a model's endpoints, variants included (`deepinfra/fp8`, `fireworks/us`)
                        (pi `openrouter/` models only, e.g. `openrouter/deepseek/deepseek-v4.1-flash@deepinfra/fp8:low`);
                        pinned with fallbacks off, recorded as part of the model name. LEVELS: "low,high" | "low..max" (range in LEVEL_ORDER, keeping only supported levels)
                        | "all" (every supported level except off) | explicit "off". No suffix = "all".
    -s, --set SET       repeatable: a model set, either a NAME from art-crit.toml [sets] or a FILE with one
                        MODEL[@UPSTREAMS][:LEVELS] per line (# comments, blank lines ignored). Its entries are added before
                        the -m specs, exactly as if given with -m. An unknown name that isn't a file is an error
                        listing the defined sets.
    -e, --effort LEVELS default LEVELS for every model without a suffix (-m or set entry)
    -i, --pick          pick harnesses, models (by number or a fuzzy search) and levels interactively (implied when no -m/--set is given; needs a tty)
    -p, --page SLUG     add to this page (default: slug of the prompt's first 6 words, max 40 chars). For an existing
                        page, PROMPT can be left out: its prompt (page.json) and kind are reused.
    -c, --change-prompt allow a PROMPT that differs from the existing page's (after path cleaning); without it that's
                        an error, since every import replaces the page's prompt for all its runs
    -t, --title TEXT    page title (default: from slug, as for import)
    -b, --brief FILE    use this brief template instead of the built-in one ({prompt} is substituted)
    -j N                max agents at once (default [run].parallel or 8)
    -T, --timeout DUR   per agent, "30m" / "90s" / "1h" (default [run].timeout or 30m)
    -y, --yes           don't ask for confirmation
    -n, --dry-run       print the plan and exit
    -P, --publish       import and `art-crit publish` each run as it finishes (the default)
    --no-publish        only import at the end; push later with `art-crit publish`
art-crit run -r/--resume DIR  finish an interrupted batch (see Resume)
```
`LEVEL_ORDER = off, minimal, low, medium, high, xhigh, max`. Every requested level is checked against the harness's
list for that model **before anything starts**; an unknown model or unsupported level is an error that names the
supported levels (pi silently clamps unsupported levels, so this check is what keeps labels honest).

With no `-m`/`--set` (or with `-i/--pick`, which adds to the specs already given), and only on a tty, `art-crit run`
asks interactively (`src/art_crit/picker.py`): a numbered **harness menu** (empty = pi, the default), then that
harness's models, then a levels prompt per picked model (default `all`, accepting the same LEVELS syntax). In the
model list, numbers, ranges or `all` select from the listing shown; any other text is an **fzf-style fuzzy search**
(letters and digits in order, separators ignored, so `claudeop55` and `g6sol` match; hits that start a word and runs
of consecutive hits rank higher) that re-lists just its matches, renumbered, and an empty answer brings the full list
back (or picks nothing while it is shown). The picks become ordinary harness-prefixed `-m` specs, so planning
validates them exactly like a hand-typed spec. A harness whose model list can't be read, and a model whose levels
can't be, are reported and skipped; a selection and a levels spec are re-asked until they parse. On a non-tty (e.g. a
script), no `-m`/`--set` is the usual error.

`art-crit.toml`:
```toml
[run]
dir = "~/dev/art-crit-runs"   # where batch directories go (never inside ~/dev/effort-runs)
parallel = 8
timeout = "30m"
tools = ["python3 (standard library only)", "node (no npm packages)", "ffmpeg", "ffprobe"]   # listed in the brief

[sets]   # each a list of "MODEL[@UPSTREAMS][:LEVELS]" strings (anything else is an error)
cheap = ["openai-codex/gpt-6-luna:minimal,low", "openrouter/deepseek/deepseek-v4.1-flash:low..high"]
```

`art-crit.toml` is parsed in one place: `art_crit.config.Config.load(root)` in `cli.main` exposes `.rewrites` (`[clean]`),
`.run` (dir, parallel, timeout, tools) and `.sets`, and is passed to the importer and runner. One run's inputs
are a `art_crit.config.RunRequest` (prompt, kind, page, title, model specs/sets, effort, brief, parallel, timeout,
publish, change_prompt); it round-trips through JSON and is stored in `batch.json`, so a `--resume` (or, later, a
website-started run) replays the same fields. It is validated when built (kind, parallel >= 1, a parseable timeout),
so bad input fails before a batch dir exists; `from_dict` ignores unknown keys. A malformed `art-crit.toml` is a
plain error for every command.

### Flow
1. **Plan**: resolve models + levels (asking on a tty when none were given, see `-i/--pick`), print the harness (name + version), page (new/existing), prompt, the numbered
   model × effort list and the batch dir. Ask `Start? [y/N]` (stdin not a tty and no `--yes` → error). `--dry-run` stops after printing.
2. **Batch dir**: `<run.dir>/<YYYY-MM-DD-HHMMSS>-<page slug>/` with `batch.json`, `prompt.md` and one run directory per
   model × effort (see "Run directory"). Run ids are assigned here from the batch's start time; each run's `state` in
   `batch.json` starts `queued`.
3. **Brief**: the kind's `src/art_crit/kinds/<kind>.md` with `{prompt}` replaced by the prompt verbatim and `{tools}` by the
   installed tools from `[run].tools` (each `"name note"`, e.g. `"python3 (standard library only)"`, listed as
   `name version note`; tools not on PATH are left out with a note). The same text for every run.
   Saved as `harness/brief.md`, never in the agent's working dir.
4. **Agents** (threads + subprocess, at most `-j` at once). Working dir = `<run>/work/` (empty at start); the harness's
   scratch is `<run>/harness/`, kept outside the working dir so the agent's project stays clean. Timeout → kill the
   process group, state `timeout`.
5. **Collect** (per run, when its agent exits): write `harness/conversation.json` (the session as a JSON array; each
   `toolResult` message carries `durationMs`, the tool's duration: from the assistant entry that called it to the
   result entry for pi, from the `tool_use` event to the `tool_result` event for Claude Code) and `run.json` (the
   run's record with `output: null`; see Run). `batch.json`'s state for the run becomes the record's `state`.
6. **Output** (per run, only when `state` is `complete`, and when `output` is missing or not `ok`): the kind's
   `finalize(work, output/)` makes the publishable output, `verify(output/)` checks it (when `finalize` succeeded), and
   `run.json`'s `output` becomes `{kind, ok, error, verified}`. A step that fails leaves `state` alone. See Kinds.
7. **Import**: `art-crit import` the batch directory with `--page` (and `--title` for a new page), then print where to
   preview (`art-crit serve`). Publishing each run is the default: right after its step 6 it is imported and pushed
   on its own (`Publisher`, one run at a time: an import rewrites page.json, and a push must never see a half-written
   run directory), so the live site fills up while the batch still runs; the batch's own import at the end is then
   skipped. `--no-publish` imports the batch once at the end and prints `art-crit publish` instead of pushing.
   Only runs that couldn't be published (a secret hit, a failed push — reported as a `note:`) fall back to it:
   it retries them and exits non-zero.

Progress: on a tty a table (model, effort, state, elapsed, turns, tokens, cost) redrawn every 2s, read from each
session file as it grows; otherwise one line per state change. The states are the agent's (queued, running, complete,
failed, timeout) plus transient labels of the output step (exporting, packaging, processing, verifying, then done, or
"no output" when it failed); the labels are never written to `batch.json`.

After progress and import/publish finish, a **failure summary** on stderr lists affected runs in plan order
(id, harness, model and effort), their agent/timeout, output or verification reasons, and the batch path for
full records/logs. It also lists unrecovered per-run import/push failures; a successful final retry clears those.
Successful runs and skipped checks are omitted. The same summary works on `--resume` and includes completed
failures on Ctrl-C, without treating queued/interrupted jobs as failed. Existing states and exit codes are unchanged.
Verification reports from every kind are saved locally at `output/verification/verify-report.json` for diagnostics
(including on resume). A verifier exception is saved as `{ok: null, error: "could not run verification: …"}`:
reported as a check problem, not an agent failure, and `output.verified` stays null. These reports are not published.

### Kinds (`src/art_crit/kinds/`)

A kind is one class registered in `KINDS` (like `HARNESSES`); the runner and the importer never branch on a kind's name.
```python
class Kind:
    name: str; tools: tuple; tools_hint: str; activity: str; serial: bool   # tools must be on PATH before a batch starts;
                                                                            # serial: finalize runs one at a time
    def brief(self) -> str                              # the template text (kinds/<name>.md)
    def finalize(self, work_dir, out_dir) -> (bool, str | None)    # export / package / normalize -> (ok, error)
    def verify(self, out_dir) -> dict | None            # {ok, ...} or None when it can't be checked here
    def stage(self, out_dir, run_dir, ctx) -> Staged    # the output into the run's published dir; Staged(fields, thumb, engine)
    def keep_source(self, rel, path) -> bool            # whether a work file is published as source
```
- **godot** (`Godot`): `finalize` = **Export**: write `export_presets.cfg` into the project (preset "Web", nothreads), run
  `godot --headless --path <work> --export-release Web <abs output>/index.html`, then check `index.html`, `index.js`,
  `index.wasm`, `index.pck` exist and are non-empty (Godot can exit 0 after failing), and write `export-manifest.json`
  (`godot`, `threads: false`, `template`, `exportedAt`). Failure → `ok: false`, `error = "Godot export failed: <last log line>"`.
  `verify` = serve the export, open it in Chrome with the swiftshader flags, wait for Godot to remove `#status` (≤ 30s), take
  `verification/frame-1.png`, wait 1.2s, take `frame-2.png`; `verify-report.json` = `{ok, booted, framesDiffer,
  consoleErrors, pageErrors}` with `ok = booted and framesDiffer and no pageErrors`. `stage` = the engine dedupe below.
- **web** (`Web`; `esbuild` and `npm` on PATH): `finalize` = **Package**: read `work/index.html` and inline what it references
  (`bundle_html()`): each local `<script type="module">` (with `src` or inline) is bundled by `esbuild --bundle
  --format=esm --minify` with everything it imports, npm packages from `node_modules/` included, and imported assets
  (images, models, audio, fonts) become data: URLs; each local `<link rel="stylesheet">` is bundled into a `<style>`; a
  classic `<script src>` is kept verbatim as a `data:text/javascript` URL (bundling would turn its globals into
  locals). `</script`/`</style` inside inlined code is escaped. Remote URLs, import maps and other script types are
  left alone for verify to catch. A `src`/`href` must name a file inside the work dir. Write `output/index.html` (≤ 20 MB)
  and `package-manifest.json` (`esbuild` version, `bytes`, `packagedAt`). Failure → `ok: false`, `error = "packaging
  failed: <reason>"` (e.g. `esbuild: Could not resolve "./x.js"`). `verify` = serve `output/`, load `index.html` inside
  `verification/frame.html`, an iframe sandboxed exactly like the site's (`allow-scripts allow-pointer-lock`, so storage
  APIs throw), with every request except those two pages aborted and recorded; wait for `document.readyState ==
  "complete"` (≤ 30s) and 1.2s more, then take the two frames. The report adds `blockedRequests`, and `ok = booted and no
  pageErrors and no blockedRequests` (a static page is fine, so frames needn't differ). `stage` copies the page to
  `game/index.html` (cleaned like source). Both Chrome checks are one helper (`browser.verify_page`); Playwright is an
  optional dependency (`pip install art-crit[verify]`), and verification is skipped with a note when it's missing.
- **media** (`Media`; `ffmpeg` and `ffprobe` on PATH): `finalize` checks every media file in `work/output/` (sorted, flattened as
  `a-b.png` for `a/b.png`, at most 8) into `output/`. Images (`.png .jpg .jpeg .webp .gif`) must be readable by ffprobe;
  one over 2 MB is re-encoded as JPEG (a GIF isn't). SVGs must parse as XML with an `<svg>` root (size from width/height
  or viewBox) and be ≤ 2 MB. Videos (`.mp4 .webm .mov`) must have a duration; one that isn't H.264/yuv420p mp4, is over
  10 s or over 2 MB is re-encoded (`libx264`, `-t 10`, max 1280 wide, CRF 26 → 32 → 38 until it fits). Each video gets a
  `.poster.jpg` at 30% of its length. A file that is none of those types isn't output at all: it's skipped without an
  error (a model that keeps its generator script in `./output/` shouldn't fail the step), and `output/` holding no media
  file at all is the error `no image or video files in ./output/`. Unreadable files and name clashes are errors. `manifest.json` =
  `{ok, items, errors}` with `ok` = at least one item and no errors. `ok` of the step = at least one item was kept;
  `error` = the manifest's errors (joined with `; `, the first 200 characters, the kept files are still published);
  `verify` = the manifest's `ok`. `keep_source`: text files of at most 512 KB; `output/` only for the files there that
  aren't media (the script that made them), never the images or videos themselves.

### Metrics (from the session log, the same numbers pi-subagents reported)
Over assistant messages: `turns` = count; `tool_calls` = number of `toolCall` content blocks; `tokens_input/output/
reasoning/cache_read` = sums of `usage.<field>`; `tokens_total = input + output`; `cost_usd` = sum of
`usage.cost.total`. `duration_ms` = wall clock of the harness process. `state = failed` when the process exits non-zero, there is no
session file, or the last assistant message has `stopReason: "error"`; `error` = its `errorMessage` or the last
non-empty stderr line (the first 200 characters).

### Harness interface (`src/art_crit/harness.py`)
Harnesses: `pi` (the default), `claude-code`, `agy` (Antigravity CLI), `grok-build`, `muse-code` and `codex`. A `-m` spec picks one with a prefix: `HARNESS:MODEL[:LEVELS]`
(no prefix, or `pi:`, = pi), in `-m`, `--set` entries and set files alike, so one batch can mix harnesses. Each run
records its harness; batch.json has `harnesses: {name: version}`. The run ids of non-pi harnesses put the harness tag after
the model (`claude-opus-5-5-cc-high-20260928-154152`), so one model under two harnesses never collides.
```python
class Harness:           # one per agent program
    def version(self) -> str | None
    def models(self) -> list[str]
    def resolve(self, model) -> str                     # alias -> id (identity by default)
    def levels(self, model) -> list[str]                # supported effort levels, in LEVEL_ORDER
    def display_model(self, model) -> str               # the model name recorded for the run
    def split_spec(self, rest) -> (str, list | None)    # "MODEL@UPSTREAMS:LEVELS" -> ("MODEL:LEVELS", upstreams)
    def pinned(self, model, upstreams) -> str           # the model argument ("model@a,b"); only pi accepts upstreams
    def command(self, model, level, brief, session_dir) -> list[str]
    def env(self, model=None, harness_dir=None) -> dict | None  # the agent's environment (None = inherit)
    def session_file(self, session_dir) -> Path | None  # the raw session in harness/ (never published)
    def session_entries(self, session_dir, brief, level) -> list  # the session in pi's format -> conversation.json
    def metrics(self, session_dir, level) -> dict | None          # parse_session()'s shape; tolerates a growing file
    def finish(self, harness_dir, model, metrics) -> dict         # final touches from the scratch dir (pi: the OpenRouter route
                                                                  # and cost); `notes` join the run's error, `extra` fields join the run
```
Pi: `pi --version`; `pi --list-models` (parse the table); levels via `pi --mode rpc --no-session --model M -ne -ns -np -nc`
sending `{"type":"get_available_thinking_levels"}` and reading the matching response;
command = `pi -p --mode json --model M:LEVEL --session-dir DIR -ne -ns -np -nc BRIEF` (no user extensions, skills,
prompt templates or AGENTS.md, so runs are reproducible); session file = the `*.jsonl` in DIR that isn't pi's stdout (`events.jsonl`).
Every `openrouter/` run adds `-e src/art_crit/pi_ext/openrouter_routing.ts` (explicit `-e` paths still load under
`-ne`) and sets `ART_CRIT_ROUTE_LOG=<harness dir>/route.jsonl` in that run's environment. A pinned run (`MODEL@slug`)
passes the base id to `--model` and also sets `ART_CRIT_OPENROUTER_ROUTING={"only": [...], "allow_fallbacks": false}`
(never inherited from art_crit's own environment), which the extension merges into the request's
`provider` field. The extension logs, per response (generation id), `{id, provider}` from its first stream chunk and
`{id, cost}` from the final chunk's `usage.cost`; the run records `route` from that log (see Run). The upstream is part of the recorded model name
(`openrouter/…/flash@deepinfra`), so two upstreams are separate rows; run ids use `-via-`.

Claude Code (`claude`): version = first word of `claude --version`. Models come from a table in the harness (there's no
listing command), mirroring the CLI's own alias table: `claude-fable-5-1`, `claude-opus-5-5`, `claude-opus-5`,
`claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-sonnet-5-5`, `claude-sonnet-5`, `claude-sonnet-4-6`,
`claude-haiku-5-5`, plus the aliases fable/opus/sonnet/haiku (each the newest of its family, `sonnet` = `claude-sonnet-5-5`);
runs are recorded as `anthropic/<id>`. Levels are low, medium, high, xhigh, max (no minimal/off), but only the ones the
model actually takes: the CLI silently clamps a level it doesn't accept (measured: `--effort xhigh` on the two `*-4-6`
models sends `effort=high`), so those are listed without xhigh, and a model that ignores effort entirely (e.g.
`claude-haiku-4-5`) isn't listed at all. Command = `claude -p --model ID --effort LEVEL --output-format stream-json --verbose --safe-mode
--permission-mode bypassPermissions --no-session-persistence --tools=Bash,Read,Write,Edit,Glob,Grep
--disallowed-tools=Agent,Task --disable-slash-commands -- BRIEF`: one direct agent with only the core file and shell
tools (like pi: no sub-agents, web, scheduling, messaging or skills), none of the user's CLAUDE.md, memory, plugins,
hooks or MCP servers (login still works), and nothing saved to the user's session history. `CLAUDECODE` and
`CLAUDE_CODE_*` are removed from its environment (art-crit may itself run inside Claude Code). The stdout stream-json is
the session; its raw events carry account/session details, so they're not published (for any harness). Conversion to pi's format:
assistant events are merged by message id (the stream emits one per content block, each repeating the usage) and
become assistant messages (text; thinking only when non-empty, print mode usually omits it; `tool_use` → `toolCall`
with Bash/Write/Edit/MultiEdit/Read mapped to pi's bash/write/edit/read names and argument shapes, file paths made
relative to the run dir; other tools keep their name and input); `tool_result` blocks become `toolResult` messages (text blocks joined into one text block; each image block becomes
`{type: "image", mimeType: "image/jpeg", data: <≤320px JPEG thumbnail made with ffmpeg>, sourceMimeType, bytes}`,
without `data` when ffmpeg is missing or fails, never the original ~500 KB image);
messages keep the stream event's `timestamp` (a merged message its first event's; the session entry and the brief the
first one in the stream); the brief is the first user message; an error result adds a final assistant message with `stopReason: "error"`.
Sub-agent events (`parent_tool_use_id` set) are skipped. Metrics: turns = top-level assistant API messages, tool
calls = their `tool_use` blocks; tokens from the final `result.usage` (the stream's per-message usage is a snapshot
taken before output is written and undercounts it; it's only summed while the run is still going), reasoning =
`result.usage.output_tokens_details.thinking_tokens`; cost = `result.total_cost_usd` (Claude Code's estimate at API
prices, also on a subscription); failed = `result.is_error` (error = `result.result`).
Agy (`agy`): models come from `agy models`, grouping the effort-suffixed slugs (`gemini-3.8-flash-high` → `gemini-3.8-flash:high`). The selected slug is passed with `--model`, **not** separately overridden with `--effort`. Runs use the underlying model vendor prefix (`google/`, `anthropic/`, `openai/` where recognizable), rather than grouping all models as Antigravity. Command uses `-p BRIEF --output-format stream-json --dangerously-skip-permissions --disable-slash-commands`. Stateless headless mode produces `init`, `step_update`, and `result` NDJSON. Tool steps are emitted once on `DONE` (not again on `ACTIVE`); agent response deltas are concatenated in order. The final result's usage supplies tokens (including `thinking_tokens`); cost is unavailable and recorded as 0, not a measured price. Non-success results fail the run. Agy currently has no documented equivalent of Claude Code's `--safe-mode` or tool allowlist: the headless session may load user configuration/tools. Runs should use an isolated CLI profile for reproducibility.

Grok Build (`grok`): models are intersected with `grok models`; effort menus for known models are in `GrokBuild.MODELS` (update when the CLI changes, as `grok models` doesn't list levels). Command uses `-p BRIEF --model ID --reasoning-effort LEVEL --output-format streaming-messages-json --always-approve --verbatim --tools run_terminal_cmd,read_file,write_file,search_replace,grep,list_dir --disallowed-tools Agent --disable-web-search --no-subagents`. The stream's Messages-compatible `assistant`/`user`/`result` events reuse the Claude Code converter. Final result usage has `reasoning_tokens`, and cost is `total_cost_usd` when supplied; under pool/OAuth it can be missing (0 in the current numeric run schema means **unreported**, not free). Grok's MCP meta-tools may still be enabled by the user's configuration, even with `--tools`; run with isolated configuration for strict comparisons.

Muse Code (`muse`): models and levels come from the catalog `muse` caches in `~/.local/share/muse/model-catalog/*.json` (`rows[].model_id` with `reasoning_effort_variants[].tier`, hidden `-contributor` rows included, image models skipped), refreshed only when the Muse TUI fetches it; the `MuseCode.MODELS` table is the fallback without a cache. The recorded model is `meta/<id>`. Command: `bash -c` running `muse exec --json --session-id ID --model M --reasoning-effort L --disable-approval --disable-sandbox --disable-web-tools --disable-reminders --no-foreign-personal-context -- BRIEF`, then `muse export --session ID --out harness/export.json` whatever `exec`'s exit code was (exec's own `--json` stdout, `events.jsonl`, carries no tool calls or usage). `export.json` is the session: its `events` are records whose `runtime.session` payloads of `kind: run` hold `reasoning_committed`, `assistant_message_committed`, `assistant_tool_calls_committed` (`tool_calls[{call_id, name, args}]`), `tool_result_batch_committed`, `model_completed` (`usage`) and `terminal` events; only runs with a `top_level_turn.run_origin` fact count. Conversion: one assistant message per model call (thinking, text, toolCalls, usage); `bash`/`write_file`/`edit_file`/`read_file` become pi's `bash`/`write`/`edit`/`read`; tool durations are exact (the `tool_batch.effect` start and end per call); timestamps from the records' `recorded_at` (µs). Metrics: turns = `model_completed` events, tokens summed over their usage with `input` = `input_tokens` - cache read/write (Muse's include them), reasoning = `reasoning_tokens`; `cost_usd` for models with published [Meta Model API prices](https://dev.meta.ai/docs/pricing-rate-limits) is `(input + cacheWrite) * input_rate + cacheRead * cached_rate + output * output_rate`, divided by 1M (reasoning is already in output). It is marked `metrics.cost_estimated: true`: API-equivalent, **not** actual subscription spend. Supported: Wonder 1.0 Standard ($4/$0.20/$20 per million uncached/cached/output), Spark 1.2/1.3 Standard ($1.25/$0.15/$4.25) and Spark 1.2/1.3 Contributor ($0.10/$0.002/$0.20). Muse Wonder Full and Wonder Contributor have no published API rate: they use Wonder Standard's rate as a **proxy**, marked `metrics.cost_estimate_proxy: "meta/muse-wonder-1.0"` (≈ in the viewer). Unknown models remain 0 (**unknown**, not free). The rates are pinned in `MuseCode.API_PRICES` and require updating when Meta changes pricing. Re-importing a legacy Muse run with `harness/export.json` calculates its estimate without modifying the archived batch run.json. Failed = no `terminal` event or one that is not `completed` (error = its `reason`).

Codex (`codex`): version = second word of `codex --version` (`codex-cli X`). Models and levels come from `codex debug models` (`models[].slug` with `supported_reasoning_levels[].effort`, `visibility: list` rows only; `ultra` is dropped because it isn't in LEVEL_ORDER), cached per harness instance; runs are recorded as `openai/<slug>`. Command = `codex exec --json --ephemeral --ignore-user-config --ignore-rules --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -m ID -c model_reasoning_effort="LEVEL" BRIEF`: one direct agent, no approvals or sandbox (like the other harnesses), no user config or execpolicy rules, and nothing persisted to `~/.codex/sessions`. The stdout JSONL stream is the session. Conversion to pi's format: only `item.completed` items count (`item.started`/`item.updated` are the same item in flight); `reasoning` -> thinking, `agent_message` -> text, each tool item (`command_execution` -> pi's `bash` with the command, `file_change`, `mcp_tool_call`, `collab_tool_call`, `web_search`) becomes one assistant `toolCall` plus its `toolResult` (`command_execution`'s output is `aggregated_output`, failed when its status isn't `completed` or its exit code is non-zero); a `turn.completed` flushes the pending assistant message with that turn's usage. The stream carries no timestamps and no model id, so entries have neither. Metrics: turns = `turn.started` count (at least the completed ones), tool calls = completed tool items, tokens summed over `turn.completed` usage with `input` = `input_tokens` - cached - cache-write (Codex's includes cached ones), reasoning = `reasoning_output_tokens`; cost is not reported (0 = **unreported**, not free); failed = a `turn.failed`/`error` event or no completed turn (error = its message).
Future harnesses and a VM runner plug in here and at "start one agent" in `runner.py`; a container executor mounts one run directory.

### Ctrl-C
Kills every running agent's process group, marks those runs `queued` in batch.json, prints the `--resume` command, exits 130.

### Resume
`batch.json` = `{prompt, kind, page, title, title_is_explicit, harnesses, brief, request, created, runs: [{id, harness, model,
model_arg, level, state}]}`, updated on every state change (`model` = what the site shows, `model_arg` = the harness's id).
`--resume DIR` reads it and, per run: `queued`/`running` → start the agent again (its run directory is emptied first); a
finished agent is never rerun. Then the output step for a `complete` run whose `output` is missing or not `ok` (so a failed
export is retried), and import. Failed and timed-out runs stay as they are. A batch written by an art-crit that grouped runs by
model (no `id` in its runs) can't be resumed.

## Ranking

The page owner ranks runs in the browser; there is no CLI command for it. Only `art-crit serve` can save a ranking
(GitHub Pages is static), so the published site shows rankings read-only.

- `art-crit serve` answers `GET api/local` → `{"rank": true}` and `PUT api/rank?p=<slug>` with body
  `{"ranks": {"<run id>": <int>|null, ...}}`. It validates the slug (`[a-z0-9][a-z0-9-]*`, page must exist), that every
  id is a run of the page, and that each rank is a whole number from 1 to the number of runs (ties allowed; `null`
  = unranked), writes `data/<slug>/ranking.json`, then rebuilds. Errors are `400 {"error": ...}`.
- Cross-site writes are refused: the request must be `Content-Type: application/json` (so another site can't send it
  without a CORS preflight, which the server doesn't answer) → else 415, a loopback `Host` (127.0.0.1, localhost or ::1;
  a DNS-rebinding site sends its own name in both Host and Origin) → else 403, and an `Origin` header, when present, must
  match the `Host` → else 403.
- `rebuild` copies each run's rank into `page.json.runs` (`rank`, `null` when unranked) and drops `ranking.json` entries
  for runs that no longer exist (e.g. after `art-crit rm`).
- The viewer only asks `api/local` when served from localhost; when it answers, the page shows a rank picker per row.

## Community votes

Visitors signed in with GitHub can give each result a heart and hand out one gold, one silver and one bronze medal per
page (ADR-0022). This is the only thing the published site writes; the owner's ranking above stays local. The API is
`cloudflare/votes.mjs`, served by the Worker at `/art-crit/api/*`, storing in D1 (`cloudflare/schema.sql`).

Tables: `hearts(page, run, user_id)`, primary key all three. `medals(page, user_id, medal, run)` with `medal` in
`gold|silver|bronze`, primary key `(page, user_id, medal)` and `UNIQUE (page, user_id, run)`: one of each medal per user
per page, each on a different result. `user_id` is the GitHub numeric id; logins and tokens are never stored.

`tallies(page, run, hearts, gold, silver, bronze)` holds the running totals and is maintained only by four triggers on
`hearts` and `medals`, so every write keeps it exact, atomically. Showing a page therefore reads one `tallies` row per
run plus the viewer's own votes, looked up by `(page, user_id)`: the cost of a view does not grow with the number of
votes. The last statement of `schema.sql` recounts every tally from the votes, so re-applying the schema repairs any
drift and counts votes cast before the table existed. Apply the schema before deploying a Worker that needs it.

| Request | Answer |
|---|---|
| `GET api/login?return=<path>` | 302 to GitHub's authorize URL (no scopes; `redirect_uri` = `api/callback`). Sets the login-state cookie. `return` is kept only if it is a page of this site, else `/art-crit/`. |
| `GET api/callback?code&state` | Checks `state` against the login-state cookie, exchanges the code, reads the GitHub profile, drops the token, sets the session cookie, 302 to the saved page. A declined sign-in returns there with no session; a bad or expired state is 400, GitHub failing 502. |
| `POST api/logout` | Clears the session cookie. |
| `GET api/votes?p=<slug>` | `{"user": {"login"}\|null, "totals": {"<run id>": {"hearts", "gold", "silver", "bronze"}}, "mine": {"hearts": ["<run id>"], "gold": "<run id>"\|null, "silver", "bronze"}\|null}`. `totals` has an entry for every run of the page, `mine` is `null` signed out. Public, `Cache-Control: no-store`. |
| `PUT api/heart` `{"p", "run", "on": true\|false}` | Adds or removes the user's heart; idempotent. Answers like `GET api/votes`. |
| `PUT api/medal` `{"p", "medal", "run": "<id>"\|null}` | Puts the user's medal on `run` (`null` takes it back). In one transaction it removes that medal's old result and any other medal the user had on `run`. Answers like `GET api/votes`. |

Cookies are `__Secure-` prefixed, `HttpOnly; Secure; SameSite=Lax`, `Path=/art-crit/api/`: the session (30 days) and the
login state (10 minutes) are JSON payloads signed with HMAC-SHA-256 (`SESSION_SECRET`) and typed so one can't stand in for
the other. Writes (`PUT`, `POST`) need a valid session (401), an `Origin` header equal to the request's own origin (403;
sandboxed game frames send `null`), `Content-Type: application/json` (415), a body under 2 KiB (413), and a page and run
that exist in the published `page.json` (404 for the page, which must come back as `application/json`, 400 for the run
or a bad slug/medal/flag). Errors are
`{"error": ...}`; no response sets CORS headers. Without D1 and the three secrets (`GITHUB_CLIENT_ID`,
`GITHUB_CLIENT_SECRET`, `SESSION_SECRET`) every route but 404 answers 503.

Viewer (`docs/assets/votes.js`): `loadVotes(slug)` fetches `api/votes` alongside `page.json` (4 s timeout) and returns a
store, or `null` when the API doesn't answer (static hosts, `art-crit serve`), in which case no vote UI is drawn. The
header shows `@login · Sign out` or `Sign in with GitHub` (`renderAuth`). `voteBar(store, runId)` is a labelled
"Community" row of `♡/♥ n` and `🥇 n 🥈 n 🥉 n` buttons (`aria-pressed` = yours, a count only when above 0). Signed out, a
click goes to `api/login` and comes back to the same URL; signed in, it writes and every bar of the page redraws from the
answer, since a medal moves between results. A failed write shows `not saved: <reason>`. The bar is on grid and compare
cards (inside the metrics row, at its bottom so the rows line up across cards, and so a card stays three grid rows), on the run page under the stat tiles, and in a table
row's expanded detail. It is separate from the owner's `rank-chip`.

## Deployment

The `art-crit` Pages project follows GitHub `fenderog/art-crit`'s `main` branch. Build command:
`python3 cloudflare/prepare.py`; output directory: `cloudflare-dist` (project root: repo root).
`art-crit publish` commits and pushes `docs/`; that push triggers Pages. Run the build locally to
check upload limits before publishing. `docs/` remains the source of truth and the local server uses
it directly; `cloudflare-dist/` is gitignored. Each `engines/<sha12>/godot.wasm` is gzip-compressed
as `godot.wasm.gz` with a deterministic header. Files over 25 MiB after staging abort the build.

Pages custom domains cannot mount at a path. A separate `art-crit-router` Worker (configured in
`cloudflare/wrangler.jsonc`, code in `cloudflare/router.mjs`) handles only
`fenderog.com/art-crit` and `fenderog.com/art-crit/*`. It redirects the bare path to the slash
and fetches static files from `art-crit.pages.dev` with `/art-crit` removed. For engine `.wasm`
URLs it fetches the `.wasm.gz` Pages asset and streams the decompressed bytes with
`Content-Type: application/wasm` and `Access-Control-Allow-Origin: *` (the iframe's origin is
opaque). Pages ignores MP4 `Range` requests, so the Worker synthesizes HTTP 206 responses for
normalized videos (≤2 MiB) to support Safari. Every response under `data/` (model-made games, packaged pages, SVGs)
carries `Content-Security-Policy: sandbox allow-scripts allow-pointer-lock`, the viewer's iframe sandbox as a header: a
direct visit to a raw output URL gets an opaque origin too, so it can't use the site's cookies or call the votes API
(ADR-0004). `docs/404.html` makes Pages answer missing paths with 404 instead of `index.html` + 200 (it is plain, with no
assets, because it is served at any depth). No other path is routed; static requests forward no visitor credentials. `/art-crit/api/*` is the
votes API (see Community votes). The apex has a
proxied DNS record to make Worker routes active, but no site at `/`. GitHub Pages can stay online
at its old URL during migration; the Pages subdomain isn't the supported URL for playing games.

## Viewer (docs/)

All four page views use `loadPage(slug)` in dom.js: one fetch of `page.json`, which includes
`runs` sorted by started_at then effort order with ranks applied. `run.json` stays the rebuild source of truth;
`art-crit list` reads `page.json.runs`. Rebuild removes legacy `results.json`. The loader owns missing-page
parameters and fetch-error messages; run/play find their run by id in `page.runs`.

All five viewer documents enforce a meta CSP: `default-src 'self'; script-src 'self'; style-src 'self';
img-src 'self' data:; media-src 'self'; connect-src 'self'; frame-src 'self'; object-src 'none';
base-uri 'none'`. Dynamic styles use CSSOM properties. The transcript lazily loads local Marked 15.0.12
and renders lexer tokens to DOM nodes with textContent, never innerHTML. Raw HTML stays visible text;
links permit only HTTP(S), and remote Markdown images stay alt text to avoid outside requests.

Shared conventions: runs are ordered by model, then effort from minimal to max (`EFFORTS` in runs.js), not
alphabetically. Effort is shown as a pill whose text is just the level, with a 6-step meter. Model ids show the model
name in bold and the provider prefix quietly (`modelLabel()`). Runs are grouped by vendor with a faint tint and a thin
stripe in the vendor's hue on table rows (page.html) and compare cards (`vendorOf()`/`vendorAttrs()`: the first segment of the
model id up to `-`, or the second after `openrouter/`; sets `data-vendor` and `--vh`). It is color only, so it works under any
sort; runs of one vendor sit together in the default model order. "Best" means the lowest cost, duration or total tokens
among runs that made their output (`!isFailed()`: neither a failed agent nor a failed output step ever wins; a cost of 0
is unreported and never wins), only when at least two runs compete (`rankBy()`); it's marked in green
with ★. Styling is one token set on `:root` (light) redefined under `prefers-color-scheme: dark`, system fonts only.

Your ranking (`run.rank`) is shown as 🥇🥈🥉 then `#4`, `#5`… (`rankLabel()`/`rankChip()`): in the runs table's Rank
column, on gallery cards, compare cards and the run title. When any run of a page is ranked, the table
sorts by rank by default, and the gallery and compare order ranked runs first (`byRankThenModel()`). Under `art-crit serve`
(`canEditRanks()`), the Rank column holds a `<select>` (– or 1…N) per row, and each change saves the whole page's ranking
(`saveRanks()`), with a status line next to the run count; a failed save reverts the select and shows the error. Data
JSON is fetched with `cache: "no-cache"` so a saved ranking or a new publish is never hidden by the browser cache.

All output rendering goes through one function, `renderOutput(run, base, opts)` in output.js (the click-to-play frame, the
immediate sandboxed frame, the media gallery, or the "no output" message, with the kind step's own error above it) and
one `KIND_UI` table (chip label, tab label, no-output text and failure badge per kind); page, run, compare and play all call
them. Any output with an `entry` is shown in the sandbox, so a new kind needs no viewer code.

- **index.html**: cards per page (thumb, a Game/Media chip, title, one icon per model vendor (OpenRouter's provider icons, vendored under `assets/vendor/icons/`; its models on hover), n_runs, updated date) → page.html.
- **page.html**: title, a details sidebar with a meta line (kind, n runs, n models), the Prompt (prompt.md) and a collapsed Final prompt,
  then **highlights**: the cheapest, fastest and fewest-tokens run among those that made their output (each links to it; a cost of 0 means unreported and never ranks) plus verified count, failed
  count and total spend. Then a runs table (thumb, rank, model, effort, harness,
  verified ✓/✗ (`output.verified`), run at (the run's `started_at`, local time, year on hover; in the phone cards a line under the metrics), duration, tokens total/reasoning, cost, tool calls). Harness shows "pi 0.87.1" (name only
  when version is null, "–" when missing).
  A `media` page also has a **Gallery** above the table: one card per run (its thumb, effort, model, cost, duration,
  "N files" when more than one), linking to the run. Expanding a media row shows its outputs. A run whose `state` isn't `complete`
  shows a red `failed`/`timeout` badge in the Verified cell (and a red edge on its row), and its expanded row shows `error`. A completed run
  whose output step failed shows a red "export failed" / "packaging failed" / "output failed" badge there instead of a check mark, still counts
  as completed in the highlights, and its expanded row shows `output.error` above "No playable build recorded for this run.".
  The table is sortable (default: model, then effort), numeric columns are right-aligned with a thin bar under the value
  scaled to the column max, the best completed value in duration / tokens / cost is starred, and every header has a help
  tooltip (shown after 0.5s). Clicking a row expands it and boots that run's game inline; clicking again removes it.
  The Harness cell shows the name with the version small underneath. At ≤720px the table turns into a list of cards
  (headers become sort chips; harness and reasoning tokens are hidden). Above that it never scrolls horizontally: the full
  table fits the 1240px page, and below it columns hide by priority: Reasoning at ≤1199px, Harness and Tool calls at ≤959px, the thumbnail at ≤799px. Model, Effort, Run at, Verified, Duration and Cost (plus
  the rank, caret and Tokens) always stay; hidden metrics are on the run page's Metrics tab and in compare.
  (`.table-wrap` keeps `overflow-x: auto` as a safety net only.) Model names with a pinned upstream wrap inside their cell.
- **run.html**: a header with model and effort; a collapsible details sidebar (as on page.html) with the provider, stat tiles (cost, duration, tokens, output tokens, tool calls, turns) each with the run's
  rank among the page's runs that made their output ("cheapest of 6", "3rd of 6"), a line with verified (`output.verified`), harness,
  started (plus the failed/timeout badge for the agent and an "export failed" / "packaging failed" / "output failed"
  badge when the output step failed), and the agent's `error`. Then tabs (the open tab is kept in the URL hash, e.g. `#transcript`; Transcript and
  Source show a count):
  - *Game*: click-to-play overlay (shows thumb). On click it inserts
    `<iframe sandbox="allow-scripts allow-pointer-lock" allow="fullscreen; autoplay; gamepad">` pointing at `output.entry`.
    There's also an "Open full screen ↗" link (link to `play.html`, which boots it in the sandbox).
  - *Transcript*: renders `session.conversation`. System prompt collapsed. User text. For each assistant message:
    thinking (collapsed, toggle "show thinking"), text (markdown), and toolCall blocks paired with their toolResult by
    `toolCallId`. Tool display: `bash` → command + output, `write` → path + content, `edit` → path + old/new blocks,
    `read`/`ls` → args + output. Any block past 20 lines or 4000 characters starts collapsed behind a toggle: output ("Output (N lines)"),
    a written file ("File (N lines)"), an edit's diff, other tools' arguments, and a bash command (its first line shown).
    An image in a tool result is shown as an `<img>` thumbnail (a data: URL, only for
    jpeg/png/gif/webp with plain base64 data, never SVG) captioned `[image: <type>, N KB]`, never as text.
    `isError` gets a ✗ badge. Show `+m:ss` since session start (the clock time on hover) and per-message token usage. A tool's duration is the `durationMs` on its `toolResult` message (when present). Filter buttons: all / tool calls / errors.
  - *Output* (instead of Game, for a `media` run): every `output.items` entry as a captioned figure (file name, size, duration,
    bytes, a `download` link), one per row at its recorded `width`×`height` (never wider than the page). Images, **SVGs included**, are only ever shown with `<img>` (which never runs an
    SVG's scripts), never inlined or put in an object/embed/iframe, and never linked for viewing on this origin.
    Videos use `<video controls preload="none">` with the poster, and never autoplay.
  - *Page* (instead of Game, for a `web` run): the packaged page with click-to-play, in the same sandboxed iframe as games.
  - *Source*: a file list, and clicking a file shows it in a `<pre>`. The first code file opens right away.
  - *Metrics*: all metrics as a table of raw values (with a readable form beside durations, costs and big counts,
    including Harness, State, Error and the output's ok / verified / error), plus links to download the raw session files.
- **compare.html**: one card per run (all runs of the page by default), laid out as a grid of ~380px columns that wraps
  into rows (3 across at desktop width, 1 on phones, never sideways scrolling), ordered by model then effort. Each card has
  the model, its effort pill (plus the failed/timeout badge), one line with harness, duration, tokens and cost (the best
  among the shown runs starred), and its game with click-to-play (each column boots independently, never automatically),
  or for a `media` run one output as the hero with a strip of thumbnails that swap it (the Play all button is hidden when there
  are no games). An image hero links to the run page (`a.media-link`); a video hero doesn't, so a click plays it. page.html's
  Grid view draws the same cards (`renderRunGrid()`).
  Cards are subgrids spanning three grid rows (heading, metrics, output), so those line up across a row even when a metrics line wraps.
  Cards are grouped by vendor (`groupByVendor()`, `vendorOf()`): a section per vendor with a quiet header (name from
  `VENDOR_NAMES`/`vendorName()`, run count, thin rule in the vendor's hue), always shown, even with a single vendor. Within a
  group the order is `byRankThenModel()`; groups go by their best rank, then unranked groups by name. Each group is its own
  grid, so the subgrid rows line up per group. The ★ best values are still computed across all shown runs, and `&r=` only
  limits which runs (and so which groups) appear. `#columns` holds the groups, not the cards.
  A card with output also has a small ↗ button (`a.popout`, next to the effort pill) that opens `play.html` for that run in a
  separate popup window (`window.open(..., "popup,noopener,width=1280,height=800")`); middle/cmd-click falls back to the
  `href` and opens a tab. It never carries `data-play`, so Play all ignores it.
- **play.html**: one run's output alone. A 36px bar (model, effort pill, state badge, "Run page →" link to run.html) above
  the output, which fills the rest of the window: for `godot`/`web` runs one `sandboxedGame()` iframe that boots immediately
  (opening the window was the click), for `media` runs `mediaGallery()` (videos still don't autoplay). A run's `error` is
  shown above the output; a missing/unknown `p`/`r` or a run without output shows a message. Never links or embeds the raw entry URL.
- Everything renders from the JSON. There are no per-page HTML files. It must work under a sub-path (`/art-crit/`),
  so use only relative URLs. It supports dark mode via `prefers-color-scheme`, has readable defaults, and has no frameworks.

## Tests (`uv run pytest`)

- CLI: unit tests plus an end-to-end import of a small synthetic batch directory (run directories with `run.json`,
  `work/`, `harness/`, `output/`). The fixture uses tiny fake engine
  files and a real Godot `index.html` template, and covers dedupe, the html rewrite, cleaning, the secret abort and
  redaction, idempotency, rm, and rebuild.
- Viewer: Playwright (Python, `channel="chrome"`, which uses the installed Google Chrome, so no browser download)
  against `art-crit serve` on a fixture site. It covers each page rendering without console errors, click-to-play inserting
  a sandboxed iframe, the transcript's tool calls and error badges, and compare with 3 runs. A `media` fixture page
  (`art`: an SVG with an embedded script, a PNG and a 1 s mp4) covers the gallery, the Output tab (the SVG's script
  never runs, videos don't autoplay), expanded rows and compare.
  Also covered: effort-order sorting, the highlights (a failed run never wins "cheapest"), best-value stars, the run
  page ranks, the linkable tab hash and the Source tab opening its first file.
- `art-crit run`: a fake `pi` (a Python script put first on PATH by the test) that answers `--version`, `--list-models`,
  the RPC levels request, and `-p` runs by writing a canned session file and a tiny project; env vars make it fail,
  hang, or exit non-zero. Covers level parsing (`all`, ranges, explicit lists, off excluded by default, unsupported
  level → error before anything starts), the plan/confirmation, `-j`, timeout, failed runs being imported, metrics
  against the real voxel-horse `high/session.jsonl` numbers (when present), and `--resume` not rerunning finished
  agents (and retrying a failed output step), a toy kind defined in a test running end to end, and the run directory layout. For a media brief the fake pi writes `./output/` (SVG, PNG and an ffmpeg-made mp4) plus a script and a
  leftover binary frame; with `FAKE_PI_BAD_OUTPUT` it adds an unreadable PNG (the step's error) and a text file in
  `./output/` (published as source, not an error). `tests/test_media.py` checks the media step on ffmpeg-generated inputs (trim + re-encode,
  oversized image → JPEG, bad files, empty output, too many files, name clashes, non-media files being skipped); media tests are skipped without
  ffmpeg. A slow test (skipped without `godot`) exports a tiny real project. No test calls a real model.
  For a web brief the fake pi writes `index.html`, `main.js`, `style.css` and a fake npm package in `node_modules/`.
  `tests/test_web_kind.py` (skipped without esbuild) packages pages with the real esbuild (module + inline module +
  classic scripts, stylesheets, imported assets, `</script>` escaping, remote/importmap left alone, missing imports and
  paths outside the project), verifies offline in the sandbox (a remote fetch and localStorage both fail it), and runs
  a web batch end to end into the viewer (kind chip, Page tab, the bundled package running in the sandboxed iframe).
