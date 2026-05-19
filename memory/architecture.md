# Architecture

Last updated: 2026-05-19
Current version: 0.2.0

## Stack

No runtime stack. This repository is a documentation-and-convention template (Markdown + JSONL) consumed by a coding agent. A single Python 3 stdlib-only validator (`scripts/validate.py`) ships alongside it. No build system, no package manager, no third-party dependencies.

## Components

- `MEMORY_PROTOCOL.md` — the rules the agent follows every session
- `replit.md` — Replit Agent entry point and overrides
- `CLAUDE.md` — Claude Code entry point and overrides
- `README.md` — human-facing overview and quickstart
- `LICENSE` — MIT
- `memory/architecture.md` — current state of the system (this file)
- `memory/progress.md` — in-flight, next, blocked
- `memory/decisions.jsonl` — append-only decision log
- `memory/drift.jsonl` — append-only drift log
- `memory/README.md` — structure reference for memory files
- `scripts/validate.py` — Python 3 validator for memory files
- `template/memory/` — blank starter files for new projects
- `.claude/settings.json` + `.claude/hooks/session-start.sh` — SessionStart hook for Claude Code on the web

## Data flow

1. Agent session starts.
2. (Optional, web sessions) `.claude/hooks/session-start.sh` runs `scripts/validate.py` to confirm memory files are well-formed.
3. Agent reads its entry point (`replit.md` or `CLAUDE.md`) → `MEMORY_PROTOCOL.md` → `memory/architecture.md` → `memory/progress.md` → tail of `decisions.jsonl` → tail of `drift.jsonl`.
4. Agent emits the confirmation line from protocol section 10.
5. Agent performs work; appends decision/drift entries as events occur.
6. At session end, agent updates `architecture.md` and `progress.md` if anything material changed; runs `scripts/validate.py`.

## External dependencies

None. Python 3 (stdlib only) is required to run the validator; no third-party packages, no network calls, no databases.

## Conventions

- `decisions.jsonl` and `drift.jsonl` are append-only. Never edit or delete entries; reverse via a new `rollback` entry.
- `architecture.md` and `progress.md` describe current state and may be overwritten.
- One JSON object per line in `.jsonl` files; ISO-8601 timestamps; `author` field required.
- Secrets referenced by name only, never value.
- Keep `architecture.md` under 200 lines, `progress.md` under 100 lines.
- New projects copy from `template/memory/`, never from the repo's own `memory/`.
