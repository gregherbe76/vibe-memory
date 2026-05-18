# Memory

This folder is your agent's persistent memory. It survives across sessions, agents, and team members. The agent reads these files at the start of every session and writes to them as it works.

You can read these files. You can edit them. You can commit them to Git. They are plain text.

## What's here

- architecture.md — Living document describing the system as it exists right now. The agent overwrites it when structure changes.
- progress.md — Current operational state: in progress, done, next, blocked.
- decisions.jsonl — Append-only log of architectural decisions. One JSON object per line. Never edited, never deleted.
- drift.jsonl — Append-only log of detected drifts: code that diverges from logged decisions.

## How to read this folder when you come back

1. Open progress.md. You know where things stand in 30 seconds.
2. Open architecture.md if you forgot the structure.
3. Tail decisions.jsonl (last 10-20 lines) for recent moves.
4. Open drift.jsonl if something feels off.

## What you should NOT do

- Don't delete entries from .jsonl files. They are append-only by design.
- Don't edit old entries to "fix" them. Append a new entry instead.
- Don't store secrets here.

## What you SHOULD do

- Commit this folder to Git. Memory is more valuable when versioned.
- Review drift.jsonl weekly. Drift left unfixed compounds.
- Edit architecture.md or progress.md directly when needed.
