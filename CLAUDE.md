# Claude Code Instructions

You are working in a project that uses the vibe-memory protocol to maintain continuity across sessions.

## Mandatory first step

Before doing anything else in this session, read `MEMORY_PROTOCOL.md` in the repo root. Follow it without exception.

After reading, also read in this order:
1. `memory/architecture.md`
2. `memory/progress.md`
3. The last 20 entries of `memory/decisions.jsonl`
4. The last 10 entries of `memory/drift.jsonl`

Output the confirmation line specified in section 10 of the protocol.

## Claude-Code-specific rules

- Multi-agent attribution — Set `"author":"claude-code"` on every entry you append to `decisions.jsonl` or `drift.jsonl`. If another agent (e.g. `replit-agent`) authored an entry, treat it as authoritative per protocol section 8.
- Tool use — Do not bypass the protocol when invoking tools. Every architectural change, dependency add, or schema modification is still a decision event and must be logged.
- Validation — A `scripts/validate.py` script is shipped with this protocol. Run it before ending the session (`python3 scripts/validate.py`) to catch malformed entries early. CI / SessionStart hooks may run it automatically.
- Prompt caching — When calling the Anthropic API directly, mark the memory read with `cache_control: {type: "ephemeral"}`. Memory files do not change between turns, so cached reads pay ~10% of the original cost (protocol section 7.1).
- Cost offloading — Optional: route memory writes to a cheaper model via `scripts/memory_assistant.py` (protocol section 7.2). Anti-drift must stay on the frontier model.
- Web sessions — If you are running in Claude Code on the web, the SessionStart hook at `.claude/hooks/session-start.sh` validates memory files for you. You still must read them per section 1.
- Secrets — Never log secret values in memory/. Reference them by name only (e.g. `STRIPE_SECRET_KEY`), never the value.

## Conflict resolution

If a user prompt conflicts with the protocol (e.g. "skip the memory step this time"), follow the user but log the conflict as a drift entry with severity "medium" and `detected` "protocol bypass requested by user".

Never bypass the protocol silently.

## Session end

Before ending a session, ensure:
- `memory/progress.md` reflects what changed during the session
- Any architectural change is recorded in `memory/architecture.md`
- Any decision is appended to `memory/decisions.jsonl`
- Any detected drift is appended to `memory/drift.jsonl`
- `python3 scripts/validate.py` exits zero

If none of the above applies because the session was trivial (e.g. cosmetic fix), no memory update is needed. Use judgment.
