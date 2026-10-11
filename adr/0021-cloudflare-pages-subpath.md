# 0021. Cloudflare Pages at fenderog.com/art-crit/

- Status: Accepted
- Recorded: 2026-10-11

## Context

The site originally ran from `main:/docs` on GitHub Pages (0001). The owner wants it at
`fenderog.com/art-crit/`, with `git push` continuing to publish and no site at the domain root.
The viewer already uses relative links, but Pages custom domains attach to hostnames, not paths.
The deduplicated Godot engine is ~39.5 MB, above Pages' 25 MiB per-asset limit. R2 isn't enabled
on this account, and a Git-connected Pages project needs GitHub app authorization.

## Decision

- Connect `fenderog/art-crit`'s `main` branch to the `art-crit` Cloudflare Pages project. The
  Pages build runs `python3 cloudflare/prepare.py` and publishes `cloudflare-dist/`. Keep
  `art-crit publish` as a `docs/` commit and push; Pages builds from that push. GitHub Pages can
  remain as an old URL during the migration.
- The build copies `docs/` and replaces *each* `engines/<hash>/godot.wasm` with a deterministic
  `godot.wasm.gz` (and checks all outputs against the 25 MiB limit). Source `docs/` stays unchanged
  for local preview and GitHub Pages. No new runtime or Python dependencies.
- A small Worker runs only on `fenderog.com/art-crit` and `fenderog.com/art-crit/*`, removes the
  prefix when fetching `art-crit.pages.dev`, and streams the decompressed engine as
  `application/wasm` with CORS for sandboxed game frames. Pages ignored Range requests for MP4s
  in the live deployment, so the Worker also serves partial (206) responses for the normalized
  videos (≤2 MiB), needed by Safari. It forwards no visitor credentials.
  `/art-crit` redirects to `/art-crit/`; other domain paths aren't routed to the site. A proxied
  DNS record for the apex is required for Worker routes even though the root remains unused.

## Alternatives considered

- **Make the Pages custom domain the apex**: would expose the entire site at `/` and potentially
  interfere with other paths on this domain.
- **Put the engine in R2**: adds a paid service and another deployment step for one compressible
  file. Reconsider if the compressed engine ever exceeds Pages' limit.
- **Serve precompressed WASM from Pages with `_headers`**: testing showed Pages doesn't reliably
  return `Content-Encoding: gzip` for requests without `Accept-Encoding`; clients get gzip bytes
  at a WASM URL. The Worker explicitly decompresses instead.
- **Direct uploads on every publish**: the owner chose Git-linked automatic builds. The `cf`
  CLI can configure Pages but its `cf pages deploy` doesn't support legacy Pages uploads; there
  is no reason to add that to the CLI when Git already handles deployment.

## Consequences

- Every Pages deploy copies the static tree and compresses the engine, rather than serving `docs/`
  directly. Engine requests use Worker compute, but require no R2 or Pages Function.
- The standalone `art-crit.pages.dev` URL serves the viewer but not the compressed Godot engines;
  the public supported URL is `/art-crit/` on the custom domain.
- The domain-root DNS record does not imply a website at `/`. The old GitHub Pages URL can stay
  online until deliberately retired.
