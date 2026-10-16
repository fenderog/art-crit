# 0030. The lanes design for home, page and compare; prompt requests become GitHub issues

- Status: Accepted
- Date: 2026-10-16

## Context

The owner redesigned the three main views around the results' pictures: one horizontal lane per model on a page,
image-first cards, a large selection tray leading to a detailed comparison, and a home page whose featured prompt is a
slideshow of its best runs. The old views (table and grid, rank editing, Play all, the local request list) still have
uses for the owner. Separately, prompt requests were local only (ADR-0024); the owner now wants visitors of the
published site to be able to suggest prompts, and wants those to land somewhere visible: the repo's issues.

## Decision

- `docs/index.html`, `page.html` and `compare.html` are the lanes design. Their scripts and stylesheet live in
  `docs/assets/lanes/` and reuse the shared modules (`dom.js`, `runs.js`, `output.js`, `votes.js`, `selection.js`),
  so all sandbox and rendering rules are unchanged. Each page links to its classic counterpart.
- The previous three views are kept, unchanged, in `docs/classic/` (with `<base href="../">`, so their URLs still
  resolve from `docs/`). Rank editing, the runs table, Play all and the local request list live there.
- "Request a prompt" (top bar of the home page) posts `{prompt, kind, note}` to the Worker's `POST api/request`. A
  signed-in visitor's request becomes an issue on `fenderog/art-crit`, labeled `prompt request`, opened with a
  fine-grained bot token (`GITHUB_ISSUES_TOKEN`, Issues: write on this repo only). The prompt and note are put in
  fenced blocks so they show verbatim (no mentions, links or Markdown). D1 counts requests (`prompt_requests`: user id,
  time, issue number; never the text): 5 per user and 50 for the whole site per day.
- Where there is no such API (`art-crit serve`, a Worker not yet configured), the form opens GitHub's own prefilled
  "new issue" page instead, which the visitor submits with their own account.

## Alternatives considered

- **Replace the old views outright**: loses rank editing and the table view the owner still uses.
- **Only the prefilled "new issue" link**: no secrets or server code, but one more step for visitors; kept as the
  fallback.
- **Open the issue as the visitor** (OAuth scope `public_repo`): asks visitors for write access to all their public
  repos, and the site would have to keep their token. The sign-in stays scope-free (ADR-0022).

## Consequences

- The published site now writes two things: votes (D1) and prompt-request issues (GitHub, through the bot token). Both
  need a session and the site's own `Origin`. The bot token is a Worker secret; it is never logged or sent to browsers.
- Setup: create the token, `wrangler secret put GITHUB_ISSUES_TOKEN`, re-apply `schema.sql`, then `wrangler deploy`.
  Until then the form falls back to GitHub's prefilled page.
- ADR-0024's local request list keeps working on `classic/index.html`; the lanes home no longer reads `requests.json`.
- `docs/classic/` is temporary: remove it (and its tests) once the owner no longer needs it.
