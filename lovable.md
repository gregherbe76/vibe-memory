# Lovable Instructions

You are working in a Lovable project. This project uses the vibe-memory protocol to maintain continuity across sessions.

## Mandatory first step

Before doing anything else in this session, read `MEMORY_PROTOCOL.md` in the repo root. Follow it without exception.

After reading, also read in this order:
1. `memory/architecture.md`
2. `memory/progress.md`
3. The last 20 entries of `memory/decisions.jsonl`
4. The last 10 entries of `memory/drift.jsonl`

Output the confirmation line specified in section 10 of the protocol.

## Lovable-specific rules

- Relationship to `mem://` — Lovable injects its own native memory (`mem://`) into every prompt. Treat `mem://` as a cache. The files in `memory/` are the durable, portable source of truth (same files work on Replit, Claude Code, Cursor, etc.). On conflict, `memory/` wins; re-populate `mem://` from the files, not the other way around.
- Memory compression — Lovable may summarize older parts of the conversation history when context grows. The `memory/` folder is your durable record. When in doubt about prior decisions, the JSONL logs are authoritative, not your in-context recollection.
- Reconstruction from code — Lovable typically infers conventions from the existing codebase. When inferred conventions conflict with an entry in `decisions.jsonl`, the logged decision wins. Append a drift entry describing the conflict so the human can adjudicate.
- Stack and conventions — These live in `memory/architecture.md`. Treat that file as the single source of truth for stack choices (e.g. "React 18 + Vite", "Express + TypeScript", "Postgres + Drizzle", "Tailwind + shadcn"). Do not silently swap one for another.
- Component-level constraints — Hard product rules (e.g. "never use Prisma", "always use Zod validation", "never break existing API contracts") belong in `memory/architecture.md` under Conventions, not scattered across prompts.
- Author attribution — Set `"author":"lovable"` on every entry you append to `decisions.jsonl` or `drift.jsonl`. If another agent (e.g. `claude-code`, `cursor`) authored an entry, treat it as authoritative per protocol section 8.
- Secrets — Never log secret values in `memory/`. Reference them by name only (e.g. `DATABASE_URL`).

## Conflict resolution

If a user prompt conflicts with the protocol (e.g. "skip the memory step this time"), follow the user but log the conflict as a drift entry with severity `"medium"` and `detected` `"protocol bypass requested by user"`.

Never bypass the protocol silently.

## Session end

Before ending a session, ensure:
- `memory/progress.md` reflects what changed during the session
- Any architectural change is recorded in `memory/architecture.md`
- Any decision is appended to `memory/decisions.jsonl`
- Any detected drift is appended to `memory/drift.jsonl`

A useful habit at the end of significant sessions: ask explicitly "update memory/architecture.md and memory/progress.md with the latest decisions from this session." Lovable responds well to that explicit instruction.

If none of the above applies because the session was trivial (e.g. cosmetic fix), no memory update is needed. Use judgment.
