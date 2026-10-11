-- Community votes (adr/0022). Apply once, and again after any change here (everything is IF NOT EXISTS):
--   wrangler d1 execute art-crit-votes --remote --file cloudflare/schema.sql

-- A heart: one per user per result; a user can heart any number of results.
CREATE TABLE IF NOT EXISTS hearts (
  page TEXT NOT NULL,
  run TEXT NOT NULL,
  user_id INTEGER NOT NULL,  -- GitHub's numeric id: logins can change, so they are never stored
  PRIMARY KEY (page, run, user_id)
);

-- A medal: each user has one gold, one silver and one bronze per page, each on a different result.
CREATE TABLE IF NOT EXISTS medals (
  page TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  medal TEXT NOT NULL CHECK (medal IN ('gold', 'silver', 'bronze')),
  run TEXT NOT NULL,
  PRIMARY KEY (page, user_id, medal),
  UNIQUE (page, user_id, run)
);
