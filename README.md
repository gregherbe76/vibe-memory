# vibe-memory

[![validate](https://github.com/gregherbe76/vibe-memory/actions/workflows/validate.yml/badge.svg)](https://github.com/gregherbe76/vibe-memory/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol version](https://img.shields.io/badge/protocol-v0.2.0-informational)](MEMORY_PROTOCOL.md)

A memory protocol for vibe coding agents. Persistent memory for coding agents — across sessions, across agents, across months.

Works with Replit Agent, Claude Code, Lovable, Cursor, Aider, Codex, OpenHands, and any agent that reads instruction files from the repo.

## How it works

The agent reads `MEMORY_PROTOCOL.md` and an entry-point file for its runtime (`replit.md`, `CLAUDE.md`, `lovable.md`, or `AGENTS.md`) at the start of every session. It logs decisions, detects drift, tracks progress. No CLI, no package, no MCP. Just files.

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

One-line install into the current directory:

```sh
curl -sSL https://raw.githubusercontent.com/gregherbe76/vibe-memory/main/install.sh | bash
```

Or pin to a release:

```sh
curl -sSL https://raw.githubusercontent.com/gregherbe76/vibe-memory/main/install.sh | bash -s -- --ref v0.2.0
```

The installer drops the protocol files, entry points, validator, a blank `memory/` folder, and the optional Claude Code SessionStart hook. It never overwrites existing files.

Then start a session — the agent reads `MEMORY_PROTOCOL.md`, follows the rules, and emits the confirmation line from section 10.

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
- `template/memory/` — blank starter files for new projects
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

## License

MIT — see [LICENSE](LICENSE). Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
