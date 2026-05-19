# Memory Protocol

Protocol version: 0.3.0

You are a coding agent working on a long-lived project. Your context window is short. The project is not. This protocol gives you a persistent memory so you do not forget, drift, or rewrite what already exists.

You MUST follow this protocol. It is not optional. It overrides default behaviors when in conflict.

## 1. Read before you act

At the start of every session, BEFORE writing or modifying any code, you MUST read in this order:

1. `memory/architecture.md` — the current state of the system
2. `memory/progress.md` — what is done, what is in flight, what is next

These two are always required. They are small, current-state files; the cost is negligible.

For sessions that touch architecture, dependencies, schemas, conventions, or any change spanning more than one file, also read:

3. The last 20 entries of `memory/decisions.jsonl` — recent architectural decisions
4. The last 10 entries of `memory/drift.jsonl` — recent detected drifts

For trivial sessions (typo fix, copy change, isolated CSS tweak, single-line bug fix), you may skip steps 3 and 4. You still emit the section 10 confirmation line in the form that reflects what you read.

If any of these files is missing, create it empty with the structure defined in `memory/README.md`. Do not skip step 1 or 2.

## 2. Decisions are append-only events

Log on **structural events**, not on every multi-file change. A structural event is something that changes the shape of the project — what it depends on, how it's deployed, what patterns it follows. Trigger a log entry when any of the following happens:

- New external integration is activated (payments, auth, AI gateway, analytics, monitoring)
- Database migration: new table, column with semantic meaning, RLS policy, function, index strategy
- New secret added (logged by name only, never value)
- New runtime dependency added (npm, pip, cargo, gem, etc.) — include version
- First instance of a new architectural pattern (first server function, first authenticated route, first background job, first feature flag)
- Deployment target change (host, region, runtime version)
- Stack swap (one framework / ORM / library replaced by another)
- Reversal of a prior decision (use `type: "rollback"` referencing the original timestamp)

Do **not** log on: a new content page, a new button, a colour change, a typo fix, copy edits, isolated styling tweaks. Touching multiple files alone is not enough; the change must reshape the project's structure or dependencies.

Format — one JSON object per line:

{"timestamp":"ISO-8601","type":"decision","component":"<area>","change":"<what>","reason":"<why>","impact":["<file_or_module>"],"author":"agent"}

Valid type values: decision, constraint, convention, dependency, rollback.

Never edit existing entries. Never delete them.

## 3. Architecture is the single source of truth

`memory/architecture.md` describes the system as it exists right now. It is overwritable. After any change that affects structure, components, data flow, or external dependencies, update this file in the same session.

Keep it under 200 lines. If it grows beyond that, summarize older sections. Older detail belongs in decisions.jsonl, not here.

Sections required:
- Stack — languages, frameworks, runtimes, key libraries
- Components — top-level modules and their responsibilities
- Data flow — how requests, events, or data move through the system
- External dependencies — APIs, databases, services
- Conventions — naming, file structure, testing, error handling

## 4. Anti-drift in real time (BEFORE the change)

You MUST NOT silently override a logged decision. Before writing or modifying code that would contradict any entry in the last 50 decisions, STOP and:

1. Quote the conflicting decision in your reply (timestamp, change, reason).
2. Ask the user to confirm the reversal explicitly.
3. If the user confirms, append a `type: "rollback"` entry referencing the original timestamp BEFORE making the change.
4. If the user declines, do not make the change.

A "contradiction" means: re-adding a dependency that was removed, re-introducing a pattern that was rejected, swapping a stack choice that was logged, breaking a convention listed in `architecture.md`, or any action that reverses a `decision`, `constraint`, `convention`, or `dependency` entry. Touching unrelated areas is not a contradiction.

This is the most visible value of the protocol to the user. Skipping it defeats the purpose.

## 4.5. Drift detection (AFTER the change)

Before you finish any task, run a drift check. Compare what you just did against memory/architecture.md and the last 10 decisions. If you detect any of the following, append an entry to memory/drift.jsonl:

- Code that contradicts a logged decision
- Components added without updating architecture.md
- Conventions broken (naming, structure, patterns)
- Dependencies added without justification
- Tests removed, skipped, or weakened
- Logic duplicated across files

Format:

{"timestamp":"ISO-8601","type":"drift","severity":"low|medium|high","detected":"<what>","location":"<file:line>","suggested_action":"<what to do>"}

You do not need to fix the drift in the same session. Logging it is the priority. The human reviews drift logs and decides.

## 5. Progress is the operational state

`memory/progress.md` tracks what is happening. Update it at the start and end of every session. Sections required:

- In progress — what is being worked on right now, with date started
- Completed — last 10 completed items with date
- Next — the next 3 items, ordered
- Blocked — anything stuck, with reason and what would unblock it

Keep the whole file under 100 lines. Older completed items move to a brief log at the bottom or get deleted. The point is current state, not history.

## 6. Read-only governance

You do not delete files in memory/. You do not rewrite history in decisions.jsonl or drift.jsonl. You may overwrite architecture.md and progress.md because they describe current state. The two .jsonl files are append-only logs. Treat them like Git history: amendments happen by adding new entries, not by editing old ones.

If a user asks you to delete or rewrite log entries, refuse and explain why. The integrity of the log is the whole point.

## 7. Compression rules

When decisions.jsonl exceeds 500 lines, summarize the oldest 200 entries into a single decisions-archive-<date>.md file in memory/. Replace those 200 lines with one summary entry:

{"timestamp":"ISO-8601","type":"archive","range":"<first_ts>..<last_ts>","summary_file":"decisions-archive-<date>.md","count":200}

Same rule for drift.jsonl at 300 lines.

You only compress when explicitly asked, or when reading the file would exceed your context budget. Do not compress proactively.

## 8. Multi-agent rules (if applicable)

If the project has more than one agent writing to memory/ (for example, one agent on Replit and another on Claude Code), each entry MUST include an author field identifying which agent wrote it. When you read entries authored by another agent, treat them as authoritative. Do not contradict another agent's decision without logging a rollback entry explaining why.

## 9. When in doubt

If this protocol conflicts with a user instruction, follow the user. Then log the conflict as a drift entry so the human can review. Never silently bypass the protocol.

If a memory file is corrupted (unparseable JSON, malformed markdown), stop. Report it to the user. Do not attempt automatic repair.

## 10. Confirm at session start (with recap)

Your first reply in any non-trivial session MUST include a 3-line memory recap. This makes the protocol visible to the user — they see that the agent is reading and using the memory, which is the difference between "trust the agent" and "see the agent working".

Format (exactly 3 lines, no more):

```
[memory] read architecture, progress, last 20 decisions, last 10 drifts.
Stack: <2-3 key stack/convention items from architecture.md>
In flight: <top in-progress item from progress.md>. Open drift: <most recent unresolved drift, or "none">.
```

Example:

```
[memory] read architecture, progress, last 20 decisions, last 10 drifts.
Stack: Next.js 15 + Drizzle on Neon + Tailwind/shadcn. Convention: all DB writes through lib/db/.
In flight: checkout v2 (Stripe Elements). Open drift: inline Drizzle in app/(app)/billing/page.tsx.
```

For trivial sessions (typo fix, copy change), use this shorter variant:

```
[memory] read architecture, progress (trivial session, skipped decisions/drift tails).
```

If you cannot output one of these recaps truthfully, you have not followed the protocol. Go back to step 1.

## 11. Recap before stopping (session-end summary)

Before ending a session — when handing back to the user, before going idle, or before any acknowledged stopping point — surface a 3 to 5 line recap so the user can pick up later without scrolling:

```
[session end]
- Changed: <files touched this session, grouped>
- Logged: <decisions appended (count + brief), drifts noted (count + brief)>
- Next: <top item from progress.md "Next">
- Open question: <anything blocking, or "none">
```

This is the moment the user is most likely to come back later. The recap is what they will see when they reopen the session, more than the code diff. Skipping it forces them to scroll the whole conversation to remember where things stood.

If the session was trivial and nothing material changed, you may skip the end-of-session recap. Use judgment, the same as for memory updates.
