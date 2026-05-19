# vibe-memory

[![validate](https://github.com/gregherbe76/vibe-memory/actions/workflows/validate.yml/badge.svg)](https://github.com/gregherbe76/vibe-memory/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol version](https://img.shields.io/badge/protocol-v0.3.0-informational)](MEMORY_PROTOCOL.md)

**A continuity layer for AI-built projects.** Persistent memory for Claude Code, Cursor, Lovable, Replit Agent — across sessions, across agents, across months.

> Without continuity, the human becomes the project's memory system. vibe-memory takes that load off.

Works with Replit Agent, Claude Code, Lovable, Cursor, Aider, Codex, OpenHands, and any agent that reads instruction files from the repo.

## The moment that pays for it

You decided to drop Prisma a month ago. Today the agent is about to re-add it. With vibe-memory, this happens **before** the import goes in:

<p align="center">
  <video src="https://github.com/user-attachments/assets/c23603d0-2d6d-4d9d-b9cf-825e9fdeb93e" controls width="720" muted></video>
</p>

If your renderer doesn't play the video inline (GitHub mobile, some markdown viewers), [watch it here](assets/anti-drift-demo.mp4). The fallback text version:

```
⚠️  Conflicting decision detected
    2026-03-12 — dependency: dropped Prisma in favor of Drizzle
    Reason: serverless cold starts on Neon
    Confirm reversal? (y/N)
```

No silent regression. No "wait why does this still use Prisma?" three weeks later. That's the protocol's most visible value — see section 4 of `MEMORY_PROTOCOL.md`.

## How it works

The agent reads `MEMORY_PROTOCOL.md` and an entry-point file for its runtime (`replit.md`, `CLAUDE.md`, `lovable.md`, or `AGENTS.md`) at the start of every session. It logs structural decisions, detects drift, tracks progress, and stops itself when about to contradict a logged choice. No CLI, no package, no MCP. Just files.

## When is this worth it?

vibe-memory pays off when **time** and **architectural change** stack up. Use it for:

- ✅ Projects expected to live more than a month, with multiple sessions
- ✅ Multiple agents (or multiple humans) working on the same project
- ✅ Architecture that evolves: refactors, schema migrations, dependency swaps

Skip it for:

- ❌ Weekend prototype or throwaway MVP
- ❌ A 1–2 page static site
- ❌ Anything where the whole project fits in one prompt

If two weeks in your `memory/` files don't reflect reality, you've over-applied the protocol. Simplify (drop drift logging, keep only `architecture.md`) or fall back to your agent's native memory. The validator's `--check-freshness DAYS` flag warns when `progress.md` / `architecture.md` go stale.

## Quickstart

Two modes. Pick one:

### Mono-file mode (recommended for solo / weekend / MVP)

A single `vibememory.md` file that contains the lite protocol AND your memory:

```sh
curl -sSL https://raw.githubusercontent.com/gregherbe76/vibe-memory/main/install.sh | bash -s -- --mode mono
```

You get one file to edit. The agent reads it top-to-bottom at session start, appends to the tables at the bottom as it works. No validator, no CI, no JSON. Upgrade to full mode if the project grows.

### Full mode (multi-agent, multi-runtime, CI-validated)

The full protocol with separate `architecture.md`, `progress.md`, append-only JSONL logs, validator, schemas, and optional hooks:

```sh
curl -sSL https://raw.githubusercontent.com/gregherbe76/vibe-memory/main/install.sh | bash
```

Or pin to a release:

```sh
curl -sSL https://raw.githubusercontent.com/gregherbe76/vibe-memory/main/install.sh | bash -s -- --ref v0.3.0
```

The installer drops the protocol files, entry points, validator, a blank `memory/` folder, and the optional Claude Code SessionStart hook. It never overwrites existing files.

Then start a session — the agent reads `MEMORY_PROTOCOL.md`, follows the rules, and emits the section 10 confirmation recap.

### Manual install

```sh
curl -sSL https://github.com/gregherbe76/vibe-memory/archive/refs/heads/main.tar.gz \
  | tar -xz --strip-components=1 \
      vibe-memory-main/MEMORY_PROTOCOL.md \
      vibe-memory-main/replit.md \
      vibe-memory-main/CLAUDE.md \
      vibe-memory-main/AGENTS.md \
      vibe-memory-main/scripts \
      vibe-memory-main/schemas \
      vibe-memory-main/template
mv template/memory ./memory
rmdir template
python3 scripts/validate.py
```

## Structure

- `MEMORY_PROTOCOL.md` — the rules the agent follows (versioned, semver)
- `replit.md`, `CLAUDE.md`, `lovable.md`, `AGENTS.md` — runtime-specific entry points
- `memory/` — this repo's own memory; self-describes vibe-memory
- `template/memory/` — blank starter files for new projects (full mode)
- `template/vibememory.md` — single-file starter (mono mode)
- `examples/` — three worked memory states (web app, CLI, library)
- `scripts/validate.py` — Python 3 stdlib validator
- `scripts/render.py` — render `decisions.jsonl` + `drift.jsonl` into a human-readable markdown journal
- `schemas/` — JSON schemas for decision and drift entries
- `tests/` — unittest suite for the validator
- `.claude/` — SessionStart hook + settings for Claude Code on the web
- `.github/workflows/validate.yml` — CI running the validator on every push
- `install.sh` — one-line installer
- `.pre-commit-hooks.yaml` — pre-commit integration

## Validating

`scripts/validate.py` checks:

- `architecture.md` exists and is ≤ 200 lines
- `progress.md` exists and is ≤ 100 lines
- every line in `decisions.jsonl` / `drift.jsonl` is valid JSON with required fields, valid type/severity, and an ISO-8601 timestamp

Exit code 0 on success, 1 on any issue.

```sh
python3 scripts/validate.py                    # validate ./memory
python3 scripts/validate.py path/to/memory     # validate a specific dir
python3 scripts/validate.py --check-freshness 30   # warn if progress/architecture stale
python3 -m unittest discover -s tests          # run the validator's own tests
```

## Reading the journal

JSONL is the source of truth; if you'd rather read a chronological markdown view, render it:

```sh
python3 scripts/render.py                      # to stdout
python3 scripts/render.py --output JOURNAL.md  # to a file
```

## Pre-commit hook

Add to your project's `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gregherbe76/vibe-memory
    rev: v0.2.0
    hooks:
      - id: vibe-memory-validate
```

## Claude Code on the web

The included `.claude/settings.json` registers a SessionStart hook that runs the validator automatically. The installer drops it into `.claude/` so every web session begins with a green validation check.

## Multi-agent

Each entry in `decisions.jsonl` and `drift.jsonl` carries an `author` field. When more than one agent works on a project (e.g. Claude Code reviewing what Cursor wrote), each agent treats the other's entries as authoritative and logs a `rollback` entry if it needs to reverse a prior decision. See `MEMORY_PROTOCOL.md` section 8.

## FAQ

### Why not an MCP memory server?

MCP servers do **retrieval** — semantic search over large context, embeddings, knowledge graphs. vibe-memory does **continuity** — making sure architectural decisions survive sessions and that the agent doesn't silently contradict them. The two are complementary: use both if you need both. vibe-memory's territory is portability, auditability, git-native, visible anti-drift, zero infra.

### Why not just a `CLAUDE.md` / `.cursorrules`?

Those store **rules** (preferences, conventions, "never use X"). vibe-memory stores **events** — decisions with timestamps, drift detected, progression over time. The two are complementary. On Lovable specifically the boundary is explicit: `mem://` = rules, `memory/` = journal (see `lovable.md`).

### Is this just ADRs (Architecture Decision Records)?

ADRs are a format written by humans, for humans, often after the fact. vibe-memory is the same idea **operationalized** for AI coding: machine-readable (JSONL + JSON Schema), written by the agent during the session, re-read by the agent at every future session. ADRs informed the design; vibe-memory is what you get when the audience changes from human reviewer to coding agent.

### Will the agent actually follow the protocol?

Frontier models (Claude 4.x, GPT-5, etc.) follow structured instructions reliably. The validator catches malformed entries (CI blocks, pre-commit rejects). The section 10 recap shows you in real time whether the agent read the memory. For substantive adherence to logged decisions, the loop closes when you skim the log periodically (the `--check-freshness` flag warns when you've stopped).

### How does it scale?

Manual compression when `decisions.jsonl` exceeds 500 lines (protocol section 7). On Lovable, that section is skipped because `chat_search` provides retrieval natively. For semantic search over a very large log, pair vibe-memory with an MCP memory server — vibe-memory writes the truth, MCP indexes it.

### What about token cost?

Tiered reading (protocol section 1). On a typo-fix session, the agent reads only `architecture.md` + `progress.md` (~200 tokens). On a structural session, also the tails of `decisions.jsonl` + `drift.jsonl` (~800-1500 tokens). Compared to a manual re-briefing or a regression to fix, it's negligible.

## License

MIT — see [LICENSE](LICENSE). Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
