# Agent Instructions

You are working in a project that uses the vibe-memory protocol. This file is the entry point for agent-agnostic tooling (Cursor, Aider, Codex, OpenHands, and any other coding agent that reads an `AGENTS.md`).

## Mandatory first step

Before doing anything else in this session, read `MEMORY_PROTOCOL.md` in the repo root. Follow it without exception.

After reading, also read in this order:
1. `memory/architecture.md`
2. `memory/progress.md`
3. The last 20 entries of `memory/decisions.jsonl`
4. The last 10 entries of `memory/drift.jsonl`

Output the confirmation line specified in section 10 of the protocol.

## Attribution

Set the `author` field on every `decisions.jsonl` and `drift.jsonl` entry to a stable identifier for your agent. Examples: `"cursor"`, `"aider"`, `"codex"`, `"openhands"`. If multiple agents work on this project, treat entries authored by other agents as authoritative (protocol section 8); do not contradict them without logging a `rollback` entry that references the original timestamp.

## Validation

Run `python3 scripts/validate.py` before ending a session. CI runs it on every push; a malformed log will fail the build.

## Secrets

Never log secret values in `memory/`. Reference them by name only (e.g. `STRIPE_SECRET_KEY`).

## Conflict resolution

If a user prompt conflicts with the protocol (e.g. "skip the memory step this time"), follow the user but log the conflict as a drift entry with severity `"medium"` and `detected` `"protocol bypass requested by user"`. Never bypass the protocol silently.

## Session end

Before ending a session, ensure:
- `memory/progress.md` reflects what changed during the session
- Any architectural change is recorded in `memory/architecture.md`
- Any decision is appended to `memory/decisions.jsonl`
- Any detected drift is appended to `memory/drift.jsonl`
- `python3 scripts/validate.py` exits zero

If none of the above applies because the session was trivial (e.g. cosmetic fix), no memory update is needed. Use judgment.
