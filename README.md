# vibe-memory

A memory protocol for vibe coding agents. Give your Replit Agent or Claude Code a persistent memory in 30 seconds.

## How it works

The agent reads `MEMORY_PROTOCOL.md` and the entry-point file for its runtime (`replit.md` or `CLAUDE.md`) at the start of every session. It logs decisions, detects drift, tracks progress. No CLI, no package, no MCP. Just files.

## Quickstart

From your project root:

```sh
# 1. Grab the protocol files and a blank memory/ folder
curl -sSL https://github.com/gregherbe76/vibe-memory/archive/refs/heads/main.tar.gz \
  | tar -xz --strip-components=1 \
      vibe-memory-main/MEMORY_PROTOCOL.md \
      vibe-memory-main/replit.md \
      vibe-memory-main/CLAUDE.md \
      vibe-memory-main/scripts \
      vibe-memory-main/template

# 2. Promote the blank template into your real memory/ folder
mv template/memory ./memory
rmdir template

# 3. Verify
python3 scripts/validate.py
```

Then start a session. The agent reads `MEMORY_PROTOCOL.md`, follows the rules, and emits the confirmation line from section 10.

## Structure

- `MEMORY_PROTOCOL.md` — the rules the agent follows
- `replit.md` — Replit Agent entry point
- `CLAUDE.md` — Claude Code entry point
- `memory/architecture.md` — current state of the system
- `memory/progress.md` — what's done, in flight, blocked
- `memory/decisions.jsonl` — append-only decision log
- `memory/drift.jsonl` — append-only drift log
- `scripts/validate.py` — sanity-check memory files (run any time)
- `template/memory/` — blank starter files for new projects
- `.claude/hooks/session-start.sh` — optional SessionStart hook for Claude Code on the web

This repo eats its own dog food: the top-level `memory/` describes vibe-memory itself.

## Validating

`scripts/validate.py` checks:

- `architecture.md` exists and is ≤ 200 lines
- `progress.md` exists and is ≤ 100 lines
- every line in `decisions.jsonl` / `drift.jsonl` is valid JSON with required fields, valid type/severity, and an ISO-8601 timestamp

Exit code 0 on success, 1 on any issue. Wire it into CI or a pre-commit hook to keep the logs clean.

## Claude Code on the web

If you use Claude Code on the web, the included `.claude/settings.json` registers a SessionStart hook that runs the validator automatically. Drop the `.claude/` folder into your project to get the same behavior.

## License

MIT — see [LICENSE](LICENSE).
