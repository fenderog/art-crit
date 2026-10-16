-- Community votes (adr/0022). Apply once, and again after any change here (everything is IF NOT EXISTS):
--   wrangler d1 execute art-crit-votes --remote --config cloudflare/wrangler.jsonc --file cloudflare/schema.sql
-- Apply it BEFORE deploying a Worker that needs a newer schema: the older Worker keeps working on the newer schema.

-- A heart: one per user per result; a user can heart any number of results.
CREATE TABLE IF NOT EXISTS hearts (
  page TEXT NOT NULL,
  run TEXT NOT NULL,
  user_id INTEGER NOT NULL,  -- GitHub's numeric id: logins can change, so they are never stored
  PRIMARY KEY (page, run, user_id)
);
-- "What did this user heart on this page" must not scan the page's other voters (the primary key leads with run).
CREATE INDEX IF NOT EXISTS hearts_by_user ON hearts (page, user_id, run);

-- A medal: each user has one gold, one silver and one bronze per page, each on a different result.
CREATE TABLE IF NOT EXISTS medals (
  page TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  medal TEXT NOT NULL CHECK (medal IN ('gold', 'silver', 'bronze')),
  run TEXT NOT NULL,
  PRIMARY KEY (page, user_id, medal),
  UNIQUE (page, user_id, run)
);

-- Prompt requests sent from the site (adr/0029): only who and when (and the issue they became), to cap them per user
-- and per day. The prompt itself lives in the GitHub issue, not here.
CREATE TABLE IF NOT EXISTS prompt_requests (
  user_id INTEGER NOT NULL,
  at INTEGER NOT NULL,       -- unix seconds
  issue INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS prompt_requests_by_user ON prompt_requests (user_id, at);
CREATE INDEX IF NOT EXISTS prompt_requests_by_time ON prompt_requests (at);

-- Running totals per result, kept by the triggers below so that showing a page reads one row per run instead of
-- counting every vote on it. Nothing writes this table directly.
CREATE TABLE IF NOT EXISTS tallies (
  page TEXT NOT NULL,
  run TEXT NOT NULL,
  hearts INTEGER NOT NULL DEFAULT 0,
  gold INTEGER NOT NULL DEFAULT 0,
  silver INTEGER NOT NULL DEFAULT 0,
  bronze INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (page, run)
);

CREATE TRIGGER IF NOT EXISTS hearts_added AFTER INSERT ON hearts BEGIN
  INSERT INTO tallies (page, run, hearts) VALUES (NEW.page, NEW.run, 1)
    ON CONFLICT (page, run) DO UPDATE SET hearts = hearts + 1;
END;

CREATE TRIGGER IF NOT EXISTS hearts_removed AFTER DELETE ON hearts BEGIN
  UPDATE tallies SET hearts = hearts - 1 WHERE page = OLD.page AND run = OLD.run;
END;

CREATE TRIGGER IF NOT EXISTS medals_added AFTER INSERT ON medals BEGIN
  INSERT INTO tallies (page, run, gold, silver, bronze)
    VALUES (NEW.page, NEW.run, NEW.medal = 'gold', NEW.medal = 'silver', NEW.medal = 'bronze')
    ON CONFLICT (page, run) DO UPDATE SET
      gold = gold + excluded.gold, silver = silver + excluded.silver, bronze = bronze + excluded.bronze;
END;

CREATE TRIGGER IF NOT EXISTS medals_removed AFTER DELETE ON medals BEGIN
  UPDATE tallies SET
    gold = gold - (OLD.medal = 'gold'), silver = silver - (OLD.medal = 'silver'), bronze = bronze - (OLD.medal = 'bronze')
    WHERE page = OLD.page AND run = OLD.run;
END;

-- Recompute every tally from the votes themselves. One statement, so it is atomic and safe to run at any time: it
-- is how votes cast before the tallies existed are counted, and the fix if a tally ever drifts.
INSERT OR REPLACE INTO tallies (page, run, hearts, gold, silver, bronze)
  SELECT page, run, SUM(hearts), SUM(gold), SUM(silver), SUM(bronze) FROM (
    SELECT page, run, 1 AS hearts, 0 AS gold, 0 AS silver, 0 AS bronze FROM hearts
    UNION ALL
    SELECT page, run, 0, medal = 'gold', medal = 'silver', medal = 'bronze' FROM medals
  ) GROUP BY page, run;
