# vibememory

Single-file memory for your coding agent. Read top to bottom at session start. Append to the bottom sections as you work. Never edit history above the **Decisions** table.

For multi-agent / multi-runtime / CI-validated setups, use the full vibe-memory protocol (`MEMORY_PROTOCOL.md` + `memory/`) instead.

---

## Protocol (lite)

1. **Read this entire file at session start.** Don't write code until you have.
2. **Real-time anti-drift.** If a code change would contradict any row in the Decisions table below, STOP, quote the row, and ask the user to confirm the reversal before proceeding.
3. **Log structural events** in the Decisions table: new integration, DB migration, new secret, new dependency, first instance of a new pattern, deployment target change, stack swap, reversal. Skip: content pages, buttons, colour changes, typos.
4. **Log drift** in the Drift table when you notice code that contradicts an architectural rule or convention. You do not need to fix it in the same session — logging is the priority.
5. **First reply must be a 3-line recap** of architecture, current focus, and any open drift (see protocol section 10 of the full version).
6. **End every non-trivial session with a 3 to 5 line recap**: what changed, what was logged, what's next.
7. **Append-only.** The Decisions and Drift tables are append-only. To reverse a decision, add a new row with `type: rollback` referencing the original date.
8. **Secrets**: never write secret values here. Reference them by name only.

---

## Architecture

_Overwrite this section whenever structure changes. Keep it concise._

Last updated: YYYY-MM-DD

**Stack:** _(languages, frameworks, runtimes, key libraries)_

**Components:** _(top-level modules and their responsibilities)_

**Data flow:** _(how requests / events / data move through the system)_

**External dependencies:** _(APIs, databases, services)_

**Conventions:** _(naming, file structure, testing, error handling, hard rules)_

---

## Progress

_Overwrite this section as work moves. Keep it under ~30 lines._

Last updated: YYYY-MM-DD

**In progress:** _(what's being worked on, with date started)_

**Next:** _(top 3 items, ordered)_

**Completed (last 5):** _(date — what)_

**Blocked:** _(reason + what would unblock, or "None")_

---

## Decisions (append-only, newest at the bottom)

| Date | Type | Component | Change | Why | Author |
|---|---|---|---|---|---|
| YYYY-MM-DD | convention | meta | adopted vibememory mono-file mode | single-file simpler for solo / weekend projects | you |

Valid `type` values: decision, constraint, convention, dependency, rollback.

---

## Drift (append-only, newest at the bottom)

| Date | Severity | Detected | Location | Suggested action |
|---|---|---|---|---|
