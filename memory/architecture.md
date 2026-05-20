# Architecture

Last updated: 2026-05-19
Current version: 0.4.0

## Stack

No runtime stack. This repository is a documentation-and-convention template (Markdown + JSONL) consumed by a coding agent. A single Python 3 stdlib-only validator (`scripts/validate.py`) ships alongside it. No build system, no package manager, no third-party dependencies.

## Components

- `MEMORY_PROTOCOL.md` — the rules the agent follows every session; semver header; sections include real-time anti-drift (4), session-start recap (10), session-end recap (11)
- `replit.md` — Replit Agent entry point and overrides
- `CLAUDE.md` — Claude Code entry point and overrides
- `lovable.md` — Lovable entry point and overrides
- `AGENTS.md` — generic entry point for agent-agnostic tooling (Cursor, Aider, Codex, OpenHands)
- `README.md` — human-facing overview, quickstart, badges
- `LICENSE` — MIT
- `CHANGELOG.md` — semver-tracked release notes
- `CONTRIBUTING.md` — how to propose protocol, entry-point, or tooling changes
- `install.sh` — one-line installer (`curl … | bash`)
- `memory/` — this repo's own memory (self-describing)
- `template/memory/` — blank starter files for new projects
- `examples/` — three worked memory states (web app, CLI, library)
- `scripts/validate.py` — Python 3 stdlib validator; supports `validate.py [memory_dir] [--check-freshness DAYS]`
- `scripts/render.py` — renders JSONL logs into a chronological markdown journal (derived view; JSONL stays source of truth)
- `scripts/pr_comment.py` — produces a markdown PR comment diffing memory between two refs
- `scripts/memory_assistant.py` — optional v0.4 companion: routes memory writes (entries, recaps) to a cheap LLM via any OpenAI-compatible endpoint
- `scripts/compress.py` — optional v0.4 companion: auto-implements protocol section 7 (archive old entries via cheap LLM)
- `template/vibememory.md` — single-file mono-mode starter (lite protocol + memory in one file)
- `.github/workflows/memory-pr-comment.yml` — posts a sticky PR comment summarizing memory changes
- `tests/test_validate.py` — 16-test unittest suite for the validator
- `schemas/decision.schema.json` + `schemas/drift.schema.json` — JSON schemas for log entries
- `.claude/settings.json` + `.claude/hooks/session-start.sh` — SessionStart hook for Claude Code on the web
- `.github/workflows/validate.yml` — CI: runs validator on root, template, and every example, plus the test suite
- `.pre-commit-hooks.yaml` — pre-commit integration for downstream projects

## Data flow

1. Agent session starts.
2. (Optional, web sessions) `.claude/hooks/session-start.sh` runs `scripts/validate.py` to confirm memory files are well-formed.
3. Agent reads its entry point (`replit.md`, `CLAUDE.md`, or `AGENTS.md`) → `MEMORY_PROTOCOL.md` → `memory/architecture.md` → `memory/progress.md` → tail of `decisions.jsonl` → tail of `drift.jsonl`.
4. Agent emits the confirmation line from protocol section 10.
5. Agent performs work; appends decision/drift entries as events occur.
6. At session end, agent updates `architecture.md` and `progress.md` if anything material changed; runs `scripts/validate.py`.
7. CI re-validates on every push and PR.

## External dependencies

None at runtime. Python 3.10+ (stdlib only) is required to run the validator. GitHub Actions provides CI. No third-party Python packages, no network calls outside install.

## Conventions

- `decisions.jsonl` and `drift.jsonl` are append-only. Never edit or delete entries; reverse via a new `rollback` entry.
- `architecture.md` and `progress.md` describe current state and may be overwritten.
- One JSON object per line in `.jsonl` files; ISO-8601 timestamps; `author` field required.
- Secrets referenced by name only, never value.
- Keep `architecture.md` under 200 lines, `progress.md` under 100 lines.
- New projects copy from `template/memory/`, never from the repo's own `memory/`.
- Validator must stay stdlib-only; no third-party Python deps allowed.
- Protocol changes bump the `Protocol version` header and add a `CHANGELOG.md` entry.
