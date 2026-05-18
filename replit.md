# Replit Agent Instructions

You are working in a Replit project. This project uses a memory protocol to maintain continuity across sessions.

## Mandatory first step

Before doing anything else in this session, read MEMORY_PROTOCOL.md in the repo root. Follow it without exception.

After reading, also read in this order:
1. memory/architecture.md
2. memory/progress.md
3. The last 20 entries of memory/decisions.jsonl
4. The last 10 entries of memory/drift.jsonl

Output the confirmation line specified in section 10 of the protocol.

## Replit-specific rules

- Database changes — Replit projects often use Replit DB or Postgres via Replit. Any schema change is a decision event. Log it before applying.
- Secrets — Never log secret keys, tokens, or environment variables in memory/. If a decision references a secret, reference it by name only (e.g. STRIPE_SECRET_KEY), never the value.
- Deployments — When you deploy to Replit Autoscale, Reserved VM, or Static, log a decision entry with component "deployment" and the deployment type.
- Package installs — Every new dependency installed via the Packager tool is a decision event with type "dependency". Include version.
- Rollbacks — Replit's Checkpoint system is not a substitute for memory logging. When you restore a checkpoint, append a rollback entry describing what was reverted and why.

## Conflict resolution

If a user prompt conflicts with the protocol (e.g. "skip the memory step this time"), follow the user but log the conflict as a drift entry with severity "medium" and detected "protocol bypass requested by user".

Never bypass the protocol silently.

## Session end

Before ending a session, ensure:
- memory/progress.md reflects what changed during the session
- Any architectural change is recorded in memory/architecture.md
- Any decision is appended to memory/decisions.jsonl
- Any detected drift is appended to memory/drift.jsonl

If none of the above applies because the session was trivial (e.g. cosmetic fix), no memory update is needed. Use judgment.
