# Architecture

Last updated: 2026-05-18
Current version: 0.1.0

## Stack

No runtime stack. This repository is a documentation-and-convention template (Markdown + JSONL) consumed by a coding agent. No build system, no package manager, no language runtime required.

## Components

- `MEMORY_PROTOCOL.md` — the rules the agent follows every session
- `replit.md` — Replit-specific entry point and overrides
- `README.md` — human-facing overview
- `memory/architecture.md` — current state of the system (this file)
- `memory/progress.md` — in-flight, next, blocked
- `memory/decisions.jsonl` — append-only decision log
- `memory/drift.jsonl` — append-only drift log
- `memory/README.md` — structure reference for memory files

## Data flow

1. Agent session starts.
2. Agent reads `replit.md` → `MEMORY_PROTOCOL.md` → `memory/architecture.md` → `memory/progress.md` → tail of `decisions.jsonl` → tail of `drift.jsonl`.
3. Agent emits the confirmation line from protocol section 10.
4. Agent performs work; appends decision/drift entries as events occur.
5. At session end, agent updates `architecture.md` and `progress.md` if anything material changed.

## External dependencies

None. No network calls, no databases, no third-party services. Files are local to the repo.

## Conventions

- `decisions.jsonl` and `drift.jsonl` are append-only. Never edit or delete entries; reverse via a new `rollback` entry.
- `architecture.md` and `progress.md` describe current state and may be overwritten.
- One JSON object per line in `.jsonl` files; ISO-8601 timestamps; `author` field required.
- Secrets referenced by name only, never value.
- Keep `architecture.md` under 200 lines, `progress.md` under 100 lines.
