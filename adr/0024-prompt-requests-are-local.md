# 0024. Prompt requests are local: `art-crit serve` keeps them outside `docs/`

- Status: Partly superseded by [0030](0030-lanes-design-and-prompt-requests-as-issues.md) (the local list remains on `classic/index.html`)
- Date: 2026-10-13

## Context

The owner wants a place to collect ideas for new pages ("request a prompt") with what's needed to run each one, without
deciding yet whether visitors of the published site may submit them. The site writes only one thing today, community
votes through the Worker into D1 (ADR-0022), and rankings are written only by `art-crit serve` (ADR-0010).

## Decision

Prompt requests exist only under `art-crit serve`: `GET`/`PUT api/requests` read and change `requests.json` next to
`docs/` (gitignored), with the same write checks as the ranking API (JSON content type, same-host `Origin`). The viewer
shows the "Request a prompt" form and the list only when `api/local` says `requests: true` on a loopback host. A request
stores the prompt, kind, optional title, note and model set; the viewer turns it into the `art-crit run` command.

## Alternatives considered

- **Public submissions through the Worker into D1**: the natural next step, but it's a second public write path, needs
  moderation and rate limits, and the owner asked for local only for now.
- **`docs/data/requests.json`**: would be served by the site and swept into commits by `run --publish`, which stages
  all of `docs/`.
- **A CLI command (`art-crit request`)**: easy, but the browser form is where the owner browses pages and has ideas;
  a CLI can read the same file later.

## Consequences

Requests never leave the machine and cost nothing to host. Opening them to visitors later means adding them to the
Worker (with its own write rules) and showing the form on the published site; the request shape and the command preview
can stay. The file is per checkout, not synced between machines.
