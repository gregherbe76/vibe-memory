# Changelog

All notable changes to vibe-memory are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/).

## [0.2.0] — 2026-05-19

### Added
- `LICENSE` — MIT license file (README already advertised MIT)
- `CLAUDE.md` — Claude Code entry point mirroring `replit.md`
- `lovable.md` — Lovable entry point (positions `mem://` as a cache of `memory/`)
- `AGENTS.md` — generic entry point for agent-agnostic tooling
- `scripts/validate.py` — Python 3 stdlib-only validator for `memory/` files
- `tests/test_validate.py` — 16-test suite for the validator
- `.github/workflows/validate.yml` — CI running the validator and tests on every push and PR
- `.claude/hooks/session-start.sh` + `.claude/settings.json` — SessionStart hook for Claude Code on the web that runs the validator
- `template/memory/` — blank starter files for new projects
- `schemas/decision.schema.json` + `schemas/drift.schema.json` — JSON schemas formalizing the log entry contract
- `install.sh` — one-line installer for fetching the protocol into an existing project
- `.pre-commit-hooks.yaml` — pre-commit integration so the validator runs before each commit
- `CONTRIBUTING.md` — contribution guide covering protocol, entry-point, and tooling changes
- `examples/` — three worked memory states (web app, CLI, library) showing well-formed entries
- Protocol version header in `MEMORY_PROTOCOL.md`

### Changed
- `README.md` expanded with a quickstart, validation section, web-hook section, CI/license badges, and a "When is this worth it?" caveat
- Repo reorganized: stub starter files moved to `template/memory/`; root `memory/` now self-describes vibe-memory
- Protocol section 1 split into mandatory tier (architecture + progress) and conditional tier (decisions + drift tails) for trivial sessions
- Protocol section 10 confirmation line now has a trivial-session variant
- `scripts/validate.py` gains optional `--check-freshness DAYS` flag (warn-only, soft pressure for stale `progress.md` / `architecture.md`)

### Removed
- `examples/self-describing/` (content promoted to root `memory/`)

## [0.1.0] — 2026-05-18

### Added
- Initial protocol release: `MEMORY_PROTOCOL.md`, `replit.md`, blank `memory/` folder with README, `.replit` and `.gitignore`

[0.2.0]: https://github.com/gregherbe76/vibe-memory/releases/tag/v0.2.0
[0.1.0]: https://github.com/gregherbe76/vibe-memory/releases/tag/v0.1.0
