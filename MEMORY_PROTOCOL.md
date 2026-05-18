# Memory Protocol

You are a coding agent working on a long-lived project. Your context window is short. The project is not. This protocol gives you a persistent memory so you do not forget, drift, or rewrite what already exists.

You MUST follow this protocol. It is not optional. It overrides default behaviors when in conflict.

## 1. Read before you act

At the start of every session, BEFORE writing or modifying any code, you MUST read in this order:

1. `memory/architecture.md` — the current state of the system
2. `memory/progress.md` — what is done, what is in flight, what is next
3. The last 20 entries of `memory/decisions.jsonl` — recent architectural decisions
4. The last 10 entries of `memory/drift.jsonl` — recent detected drifts

If any of these files is missing, create it empty with the structure defined in `memory/README.md`. Do not skip this step.

## 2. Decisions are append-only events

Every time you make or apply an architectural choice that affects more than one file, append one line to `memory/decisions.jsonl`. One JSON object per line. Format:

{"timestamp":"ISO-8601","type":"decision","component":"<area>","change":"<what>","reason":"<why>","impact":["<file_or_module>"],"author":"agent"}

Valid type values: decision, constraint, convention, dependency, rollback.

Never edit existing entries. Never delete them. If a decision is reversed, append a new entry with type "rollback" referencing the original timestamp.

## 3. Architecture is the single source of truth

`memory/architecture.md` describes the system as it exists right now. It is overwritable. After any change that affects structure, components, data flow, or external dependencies, update this file in the same session.

Keep it under 200 lines. If it grows beyond that, summarize older sections. Older detail belongs in decisions.jsonl, not here.

Sections required:
- Stack — languages, frameworks, runtimes, key libraries
- Components — top-level modules and their responsibilities
- Data flow — how requests, events, or data move through the system
- External dependencies — APIs, databases, services
- Conventions — naming, file structure, testing, error handling

## 4. Drift detection is mandatory

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

## 10. Confirm at session start

At the start of each session, after reading the memory files, output exactly one line confirming you have done so:

[memory] read architecture, progress, last 20 decisions, last 10 drifts.

If you cannot output this line truthfully, you have not followed the protocol. Go back to step 1.
