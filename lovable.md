# Lovable Instructions

You are working in a Lovable project. This project uses the vibe-memory protocol to maintain continuity across sessions.

## Mandatory first step

Before doing anything else in this session, read `MEMORY_PROTOCOL.md` in the repo root. Follow it without exception.

After reading, also read in this order:
1. `memory/architecture.md`
2. `memory/progress.md`
3. The last 20 entries of `memory/decisions.jsonl` (only if the session touches structure — see protocol section 2)
4. The last 10 entries of `memory/drift.jsonl` (only if the session touches structure)

Output the confirmation line specified in section 10 of the protocol.

## Lovable-specific rules

### Boundary: `mem://` vs `memory/`

Lovable injects its own native memory (`mem://`) into every prompt. The two systems have different jobs and should not overlap:

- `mem://` → **rules** applied automatically to every action: design tokens, naming conventions, "never use X", "always use Y", style preferences, code patterns.
- `memory/` → **journal**: what happened, why, when. Structural decisions, dependencies, migrations, drift.

When in doubt: if it's a preference or constraint, it belongs in `mem://`. If it's an event with a timestamp, it belongs in `memory/`. On conflict, `memory/` is the durable record and wins; re-populate `mem://` from the files when needed, not the other way around. Files in `memory/` are also portable across Replit, Claude Code, Cursor — `mem://` is not.

### Lean on Lovable's native capabilities

- **Compression (protocol section 7) — skip on Lovable.** Lovable's `chat_search` already provides retrieval over the full chat history. Do not summarize `decisions.jsonl` proactively. Only compress when the file exceeds the 500-line threshold and the user explicitly asks.
- **Reading the conditional tier — be selective.** Lovable's `<codebase-context>` injects relevant files automatically. For UI-only or content-only sessions, you may skip the `decisions.jsonl` / `drift.jsonl` tails (mandatory reads remain `architecture.md` + `progress.md`).
- **Rollback entries vs version history.** Lovable's checkpoint / version history covers code-level reverts. Only log `type: "rollback"` in `decisions.jsonl` when reversing an **architectural** decision (a dependency choice, a pattern decision, a stack swap), not when reverting a code change.

### Lovable-specific structural events to log

In addition to the universal triggers in protocol section 2, log these Lovable-specific events:

- **Integration activation** — Lovable Cloud, Stripe, AI Gateway, any third-party service. This is a major event; include the integration name and what it unlocks.
- **Lovable Cloud activation specifically** — this is the bascule from frontend-only to fullstack. Always log it: `component: "cloud-activation"`, `change: "enabled Lovable Cloud"`, with the resulting capabilities (DB, auth, server functions).
- **Secrets added via `secrets--*`** — Lovable manages secrets outside the codebase (no `.env`). Each new secret is a log entry: name only, never the value.
- **Publication / `presentation-open-publish`** — each publish is a release milestone; log it with the version and what shipped.
- **DB migration via `lovable_sql`** — table, RLS policy, function, or index change. Log with the migration name.

### Cross-project preferences

If you maintain `mem://~user/` (user-level cross-project preferences), they take precedence over project rules **only when no project rule applies**. Project-level `mem://` and `memory/` always override `mem://~user/` for that project.

### Author attribution

Set `"author":"lovable"` on every entry you append to `decisions.jsonl` or `drift.jsonl`. If another agent (e.g. `claude-code`, `cursor`) authored an entry, treat it as authoritative per protocol section 8.

### Secrets

Never log secret values in `memory/`. Reference by name only (e.g. `STRIPE_SECRET_KEY`, `DATABASE_URL`).

## Validation surface

The machine-readable contract is enforced, not theoretical. Before writing entries, know that the following will check them:

- `scripts/validate.py` — checks every line of `decisions.jsonl` and `drift.jsonl` is valid JSON, has required fields, valid `type`/`severity`, ISO-8601 timestamps; checks line caps on `architecture.md` (200) and `progress.md` (100). Exit 0 / 1.
- `schemas/decision.schema.json` + `schemas/drift.schema.json` — JSON Schema Draft 2020-12. Usable by any standard schema validator (ajv, python-jsonschema, etc.) independent of `validate.py`.
- `.pre-commit-hooks.yaml` — exposes `vibe-memory-validate` as a pre-commit hook so malformed entries are rejected at commit time.
- `.github/workflows/validate.yml` — CI runs the validator on every push and PR.
- `.claude/hooks/session-start.sh` — Claude Code on the web runs the validator at session start.
- `tests/test_validate.py` — 22 unit tests on the validator itself.

If you write an entry that fails any of these checks, you will be caught — by the pre-commit hook locally, by CI in the PR, or by the session-start hook on the next Claude Code session. Write valid entries the first time.

## Recommended Core snippet for `mem://index.md`

Lovable's protocol adherence depends on the agent's discipline. To make it harder to skip, set the following at the top of `mem://index.md` (short, imperative, hard to miss):

```
RULE: At the start of every session, read MEMORY_PROTOCOL.md and lovable.md. Output the section 10 confirmation line as your first reply. No exceptions.
```

Keep this rule alone in its block — surrounding text dilutes it.

## Conflict resolution

If a user prompt conflicts with the protocol (e.g. "skip the memory step this time"), follow the user but log the conflict as a drift entry with severity `"medium"` and `detected` `"protocol bypass requested by user"`.

Never bypass the protocol silently.

## Session end

Before ending a session, ensure:
- `memory/progress.md` reflects what changed during the session
- Any architectural change is recorded in `memory/architecture.md`
- Any structural decision (see "Lovable-specific structural events" above) is appended to `memory/decisions.jsonl`
- Any detected drift is appended to `memory/drift.jsonl`

If the session was trivial (UI tweak, copy change, content addition with no structural impact), no memory update is needed. Use judgment.
