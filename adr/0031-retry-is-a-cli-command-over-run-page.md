# 0031. Retry is a CLI command that reuses `run --page` and replaces a failed run once its retry works

- Status: Accepted
- Date: 2026-10-16

## Context

Runs fail for reasons that have nothing to do with the model (a dropped websocket, a timeout, a crashed export), and a page
then shows a broken run for a model/effort that should have a picture. Re-running meant retyping the model, the effort and
the harness, then `art-crit rm` for the dead run. The published run.json records the *display* model name
(`anthropic/claude-opus-5-5`), not the id a harness takes.

## Decision

`art-crit retry <slug> [run_id...]` (`retry.py`) builds the `harness:model:level` specs of the page's failed runs and hands
them to `cmd_run` as an ordinary `--page` request. It adds no run path of its own: planning, briefs, references, publishing
and the failure summary are `run`'s. The model id comes from the harness's own list by display name (no extra field in
run.json, so every old run can be retried). Afterwards a failed run is deleted only when a new run with the same harness,
model and effort is good; otherwise it stays and the command exits 1.

## Alternatives considered

- **A Retry button on the run page** (local `art-crit serve` only): starts paid agents from a browser request, a new
  local-only API with real cost and process-spawning risk, for something a one-line command does. Can be added later over the same function.
- **Keep the failed run next to the retry**: the page then shows two runs per model/effort, one of them broken; `rm --failed` is a second step.
- **Record the harness spec in run.json**: exact, but old runs wouldn't be retryable.

## Consequences

Retrying is one command and reuses everything `run` does. A model a harness no longer offers can't be retried (the error
names it). A run that fails again keeps the old failure, so history of attempts is never silently lost.
