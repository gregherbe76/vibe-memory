# vibe-memory

A memory protocol for vibe coding agents. Give your Replit Agent a persistent memory in 30 seconds.

## How it works

The agent reads MEMORY_PROTOCOL.md and replit.md at the start of every session. It logs decisions, detects drift, tracks progress. No CLI, no package, no MCP. Just files.

## Structure

- MEMORY_PROTOCOL.md — the rules the agent follows
- replit.md — Replit-specific entry point
- memory/architecture.md — current state of the system
- memory/progress.md — what's done, in flight, blocked
- memory/decisions.jsonl — append-only decision log
- memory/drift.jsonl — append-only drift log

## License

MIT
