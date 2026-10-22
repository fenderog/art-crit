# 0027. A local run monitor in `art-crit serve`, and stopping a run with a file

- Status: Accepted
- Date: 2026-10-15

## Context

`art-crit run` prints a progress table while a batch runs, but nothing survives it: the site only knows runs that were
imported, and a run's transcript appears there after the agent exits and the kind step and verification are done. During
a long batch (blender and godot runs take many minutes) the owner wants to see what each agent is doing, what it has
written so far and what it costs, without tailing `harness/events.jsonl` by hand — and the option to stop a run that has
obviously gone wrong.

The forces: agents are local processes on the same machine (ADR-0009), the batch directory is the only source of truth
for a run in flight, and the site must stay static and read-only for visitors (ADR-0010, ADR-0022). `art-crit serve`
already had two local-only APIs (rankings, prompt requests), both refusing cross-site writes with a JSON content type,
a loopback `Host` and a same-host `Origin`.

## Decision

The monitor is an `art-crit serve`-only view of `[run].dir`: `monitor.html` + `assets/monitor.js` (reached from a
"Runs (local)" link the home page adds when `api/local` answers `runs: true`) polls `GET api/runs` every two seconds
while something is unfinished, and `GET api/run?b=&r=` for one run. Reads are loopback-`Host` only and are answered
**without** `Access-Control-Allow-Origin`, so no other website can read them. Both endpoints return each harness's own
live metrics and, for a running run, a transcript converted on the fly from its session file — lightened (images
dropped, strings clipped, the last 400 entries) because a live pi session can carry megabytes of base64.
Stopping a run goes through the *file* `<run>/harness/stop`, not a pid: the server writes it (`POST api/stop`, same
write checks as the ranking API, only for a run whose batch.json state is `running`), and the `art-crit run` process
that owns the agent sees it within a second, kills the agent's process group and records the run as `failed` with
`error: "stopped from the local monitor"`. That process does its waiting in `runner.wait_agent()`, which also handles
the timeout, so Ctrl-C, the timeout and the Stop button all kill the group in the same place.

## Alternatives considered

- **Killing by pid from `art-crit serve`**: it would have to record each agent's pid and process-group id, then check
  that the pid is still that process (reuse after a crash, `ps` output that differs between a binary and a
  shebang-script harness, platform differences). The file is a request the owner of the process acts on, so it can
  never kill an unrelated process.
- **A `run --follow`/terminal UI only**: no transcript for images, no file lists, and it needs the terminal that
  started the batch; the browser view works from any machine the server is bound to (localhost, in practice).

## Consequences

- The poll rebuilds the panes, so `monitor.js` carries the view across a refresh itself: scroll offsets and open
  `<details>` in `show()`, and the transcript's own DOM (with its filter and show-thinking) until the session file
  changes. Without that the page jumped back to the top every two seconds and the transcript's controls reset.
- A polled view is not a live terminal: a run that never writes a session (muse, until it exits) shows 0 until it does.
- **Publishing the monitor into `docs/`**: it would put batch state, prompts and transcripts into the repo and the
  public site, and `run --publish` stages all of `docs/`.
- **Serving the batch directory over HTTP**: `serve` only serves `docs/`; exposing `~/dev/art-crit-runs/` would publish
  raw sessions, secrets and reference images (ADR-0005) to anything that can reach the port.

## Consequences

A batch is now visible while it runs, from any page of the local site, and a runaway run can be stopped without
finding its terminal. The monitor is the first read API on `serve`: it must keep validating batch and run ids as plain
names (never paths), and it must keep answering without CORS headers. `run_agent` gained a one-second poll loop
(`wait_agent`), so its timeout granularity is a second, and a run stopped this way is `failed` — it is not resumed by
`--resume` and appears on the site like any other failed run. The lightening rules (`MONITOR_ENTRIES`,
`MONITOR_CLIP`) are the only place run data is deliberately not shown in full, so they need to stay conservative.
