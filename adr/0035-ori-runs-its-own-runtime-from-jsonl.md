# 0035. Ori: run its own runtime agent, read its JSONL stream, take models from OpenRouter's catalog

- Status: Accepted
- Date: 2026-10-23

## Context

Ori (`ori`, OpenRouter's CLI) can start coding agents two ways: its own runtime agent (`ori code`, the built-in
`@ori-builtins/harness-ori`) or as a launcher that routes an existing CLI (Claude Code, Codex, pi, Muse…) through
OpenRouter. art-crit is a harness comparison: what a model makes, per agent program. So the interesting thing Ori adds is
its own agent, not a second way to start the harnesses art-crit already has.

The harness interface (ADR-0007) needs three things from Ori: a command line, a session to convert into pi's format, and
metrics. `ori code -p BRIEF --output jsonl` gives a one-turn headless run whose stdout is a JSONL event stream
(`{kind: "event", event: {type: "runtime.event", event: …}}` per line, then `{kind: "result", ok, sessionId, error}`),
and whose turn results carry OpenRouter's own usage (`inputTokens`, `cacheReadTokens`, `outputTokens`, `costUsd`).
Ori has no `models` command: it resolves `--model` against OpenRouter's catalog, and its own session store
(`~/.ori/global/.ori/session-history.sqlite`, a content-addressed rope of checkpoints) is an internal format.

## Decision

`Ori` is one `Harness` in `harness.py`, running `ori code --harness ori --output jsonl --approvals self-drive --model ID
--reasoning-effort LEVEL -p BRIEF`. `--harness ori` is always pinned, so a user's default harness selection can't change
what an art-crit run is; `self-drive` is Ori's default spelled out, matching the other harnesses' no-approval runs.

- **Models and levels** come live from `https://openrouter.ai/api/v1/models` (public, no credential), fetched by
  `harness.fetch_json` and cached per instance. Text-output models only; levels are the whole ladder when a model
  advertises `reasoning_effort`, `off` alone otherwise (art-crit's `off` → Ori's `--reasoning-effort none`).
- **The JSONL stream is the session.** `ori_runtime_events` unwraps the double envelope and drops audit events;
  deltas join into one assistant message per flush, `tool.started` becomes a `toolCall`, its `tool.succeeded`/`tool.failed`
  a `toolResult` (with Ori's own `durationMs`), a failed turn/session an assistant message with `stopReason: "error"`.
- **Cost is OpenRouter's charge** (`usage.costUsd`), not a local estimate, as for pi's OpenRouter runs (ADR-0014).
- **MCP servers** go in `work/.ori/mcp.json` (`type: "stdio"` required), a workspace config Ori merges per run. Ori has no
  per-server tool filter, so `tools.mcp.<server>.hidden` is recorded empty.
- `run_agent` prefers an agent's own reported error (`metrics.error_message`) over its last stderr line, because Ori
  mirrors its runtime log to stderr.

## Alternatives considered

- **Route the other CLIs through Ori (`ori claude`, `ori pi`)**: duplicates the existing harnesses behind a wrapper, and
  the interesting comparison (Claude Code direct vs. through OpenRouter) is already covered by pi's `openrouter/` models
  (ADR-0014).
- **A static model table** (like `GrokBuild.MODELS`): OpenRouter's catalog changes weekly and has 450+ models; a table in
  the repo would be stale the day it was written.
- **Read Ori's own session store** instead of the JSONL stream: it is an internal content-addressed format
  (`history_nodes`/`history_chunks`, not documented), and it would only exist after the run, so live progress would be
  lost. The stream is the machine-readable interface Ori publishes for exactly this.
- **`--log-level none`** to silence Ori's stderr chatter: the log is useful in `harness/stderr.txt` when a run fails, and
  the error now comes from Ori's own message anyway.

## Consequences

- Planning for `ori:` models needs the network once per batch (`art-crit models -H ori` too). An unreachable catalog is a
  clear `CritError`, and tests never fetch it (`fetch_json` is monkeypatched; conftest fails any other attempt).
- A model without `reasoning_effort` offers `off` only, so `-m ori:MODEL` (all levels) plans no run for it — the same as a
  non-reasoning model under pi.
- Ori merges the user's own `~/.ori/mcp.json` and `./mcp.json` and reads its workspace instructions; art-crit can't turn
  that off, so strict comparisons need isolated Ori configuration (documented in README/SPEC).
- Ori records every run in its own workspace (`~/.ori/...`); art-crit neither reads nor publishes it.
- If Ori's event tags or usage fields change, `convert_ori_stream`/`ori_metrics` break; tests replay the stream shape
  (tests/fixtures/fake_pi/ori) taken from a real `ori code --output jsonl` run.
