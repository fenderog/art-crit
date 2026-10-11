// Just enough of Cloudflare D1's API (prepare, bind, batch) over an in-memory SQLite, so the tests run the real
// schema.sql and the Worker's real SQL. Needs node:sqlite (Node 22.13+).
import { readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";

export function memoryD1() {
  const db = new DatabaseSync(":memory:");
  db.exec(readFileSync(new URL("../../cloudflare/schema.sql", import.meta.url), "utf8"));
  const statement = (sql, args = []) => ({
    bind: (...values) => statement(sql, values),
    exec() {
      const prepared = db.prepare(sql);
      if (/^\s*select/i.test(sql)) return { results: prepared.all(...args) };
      prepared.run(...args);
      return { results: [] };
    },
  });
  return {
    prepare: (sql) => statement(sql),
    // D1 runs a batch as one transaction.
    async batch(statements) {
      db.exec("BEGIN");
      try {
        const results = statements.map((s) => s.exec());
        db.exec("COMMIT");
        return results;
      } catch (err) {
        db.exec("ROLLBACK");
        throw err;
      }
    },
  };
}
