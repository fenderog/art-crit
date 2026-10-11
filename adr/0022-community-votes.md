# 0022. Community votes: GitHub sign-in, hearts and medals in D1 behind the Worker

- Status: Accepted
- Date: 2026-10-11

## Context

The owner's ranking (0010) is one person's judgment, saved locally and published through git. They now want
visitors to weigh in: a heart per result, and a gold, silver and bronze medal to hand out per page, with GitHub
sign-in so each person counts once.

0010 deliberately kept the published site read-only and named a small write API outside Pages as the way public
voting would have to work. The site now runs behind a Cloudflare Worker on `fenderog.com/art-crit/*` (0021), and
the viewer's CSP already allows `connect-src 'self'`, so that API can live on the same origin.

## Decision

- **The Worker serves `/art-crit/api/*`** (`cloudflare/votes.mjs`); everything else stays static and read-only. It is
  the only write path of the published site. The owner's ranking stays local-only: `PUT api/rank` still exists only in
  `art-crit serve`, and the Worker answers 404 for it.
- **Storage is Cloudflare D1** (`cloudflare/schema.sql`): `hearts(page, run, user_id)` and
  `medals(page, user_id, medal, run)`. Keys make the rules: a heart is unique per user and run; a user has one of each
  medal per page (`PRIMARY KEY (page, user_id, medal)`) and a run holds one medal per user (`UNIQUE (page, user_id, run)`).
  Placing a medal is one transactional batch that frees the medal's old result and any other medal on the new one.
- **Hearts and medals are per user, tallied per result.** Nothing is a single winner; the page shows totals
  (`♥ 12 · 🥇 3 · 🥈 1 · 🥉 2`) in a labelled "Community" row, separate from the owner's rank chip.
- **Sign-in is GitHub's OAuth web flow with no scopes** (public profile only). The Worker keeps the numeric GitHub id
  and login, drops the access token immediately, and sets a stateless session cookie: a JSON payload signed with
  HMAC-SHA-256 (`SESSION_SECRET`), `HttpOnly; Secure; SameSite=Lax`, scoped to `/art-crit/api/`, 30 days. A login-state
  cookie (10 minutes) binds the OAuth `state` to the browser and the page to return to, and cannot be used as a session.
  Only ids go into D1, never logins or tokens.
- **Writes are guarded three ways**: a valid session; an `Origin` header equal to the site's own origin (so another
  site, and a sandboxed game frame whose origin is `null`, can't vote); and a JSON content type. The page and run must
  exist in the published `page.json`. Responses carry no CORS headers.
- **The viewer draws vote controls only when `api/votes` answers.** On `art-crit serve`, the old GitHub Pages URL and
  `*.pages.dev` it doesn't, so nothing appears there.

## Alternatives considered

- **Cloudflare KV**: no transactions, and counting votes per run means listing keys; the medal rules would become
  read-modify-write races. D1's constraints enforce them.
- **A Durable Object per page**: strongest consistency, but more moving parts than a handful of small tables needs.
- **Votes committed to the repo** (like rankings): needs a write path from the browser to git anyway, and every vote
  would be a commit.
- **Stored sessions in D1**: allows instant revocation, at the cost of a lookup on every request and another table.
  A signed cookie is enough while the only abuse response is blocking a user id, which can be added later.
- **Another login provider or anonymous voting**: GitHub matches this audience and makes one-person-one-vote
  plausible without collecting emails.
- **Showing GitHub avatars**: blocked by the viewer's `img-src 'self'` CSP, and not worth loosening it for.

## Consequences

- This reverses 0010's "the published site never gets a way to write data", for votes only. The security of the site
  now includes the Worker's Origin and session checks; keep their tests (`tests/js/votes.test.mjs`).
- **Votes are not in git.** They live only in D1: back them up with `wrangler d1 export`, and deleting a run leaves its
  votes behind (harmless, they are never shown). Local previews have no votes.
- **Sign-in raises the cost of stuffing votes but doesn't stop it**: GitHub accounts are free. There is no rate limit
  in the Worker; add a Cloudflare rate-limiting rule on `/art-crit/api/*` if it is ever needed.
- The Worker now needs a D1 database and three secrets (`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `SESSION_SECRET`),
  and depends on a GitHub OAuth App. The setup is in README.md. Without them it answers 503 and the viewer shows nothing.
- Each vote request fetches the page's `page.json` from Pages to validate run ids (cached for 60 seconds).
- Not built: sorting by votes, a Votes column in the runs table (the table shows the controls in each row's expanded
  detail), an export command.
