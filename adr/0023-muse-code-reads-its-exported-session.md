# 0023. Muse Code: the session is `muse export`ed after `exec`, not read from `--json`

- Status: Accepted
- Date: 2026-10-12

## Context

`muse exec --json` prints a live event stream, but it is a thin one: task lifecycle and output deltas, with no tool
calls, tool results or token usage. The durable session log has all of that (`muse export` writes it as one JSON
document), and it also records the background reminder agents, which must not count toward a run. The harness
interface (ADR-0007) wants a session file to convert into pi's format and metrics read from it.

## Decision

`MuseCode.command` wraps `muse exec` in `bash -c` that runs `muse export --session ID --out harness/export.json`
after the agent exits, whatever its exit code (the session id is chosen by art-crit with `--session-id`). `export.json`
is the harness's session file; `events.jsonl` (the live stream) is ignored. Only runs marked as the top-level turn
count, and reminder agents are turned off for the run anyway.

## Alternatives considered

- **Parse the `--json` stream**: no tool calls or usage in it, so no transcript and no tokens.
- **A `Harness.after_run` hook that calls `muse export`**: cleaner than a shell wrapper, but a new runner concept
  for one harness; the wrapper keeps `runner.py` untouched.
- **Read `~/.local/share/muse/sessions/` directly**: an undocumented binary journal format.

## Consequences

- There is no session until the agent exits, so live progress for Muse runs shows 0 turns and tokens.
- A run killed by a timeout or Ctrl-C has no export (the wrapper dies with the process group), so it has no transcript.
- If `muse export` changes its document layout, `convert_muse_export` and `muse_metrics` break; the tests use a
  hand-made export in the real shape (tests/fixtures/fake_pi/muse).
- Cost is not in the log, so it is recorded as 0 (unreported).
