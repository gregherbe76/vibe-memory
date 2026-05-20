# Changelog

All notable changes to vibe-memory are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/).

## [0.4.0] — 2026-05-19

Cost-optimization release. Stacking the five levers documented here can reduce AI cost by 50-75% on a long-running project.

### Added
- **Protocol section 7.1 — Prompt caching** — recommended convention: mark the memory read as cacheable on Anthropic / OpenAI APIs. Memory files do not change between turns; cached reads pay ~10% of the original cost. Single biggest cost lever for direct API users.
- **Protocol section 7.2 — Cheap-model offloading** — memory writes don't require frontier intelligence. Documents which operations can be offloaded (entries, recaps, summaries) and which must stay on the main model (anti-drift, code, architecture).
- **`scripts/memory_assistant.py`** — optional companion script that routes memory operations to any OpenAI-compatible chat completions endpoint (Groq, Together, Fireworks, OpenRouter, Ollama, Anthropic, OpenAI). Subcommands: `recap` (deterministic by default, no LLM needed), `decision-entry`, `drift-entry`. Pure stdlib (`urllib`).
- **`scripts/compress.py`** — optional companion script implementing protocol section 7 automatically. Summarizes oldest entries into `decisions-archive-<date>.md`, replaces them with a single `archive` entry. `--dry-run`, `--keep`, `--threshold` flags. Uses the same `VIBEMEM_LLM_*` env vars as `memory_assistant.py`.
- **README "Cost optimization" section** — explicit 5-lever stack with sample math, code snippets, and a savings table.
- **8 new tests** (33 total) — covering deterministic recap, JSON extraction from noisy LLM responses, LLM env-var requirement, compress dry-run behavior.

### Changed
- `CLAUDE.md` documents prompt caching as a Claude-specific cost note.
- Protocol version header: 0.3.0 → 0.4.0

### Notes
- `memory_assistant.py` and `compress.py` are **optional companions**. The protocol stays portable, files-only, no-infra by default. These scripts are for heavy users who want to optimize.
- Anti-drift (protocol section 4) **must** stay on the main frontier model. It is the one operation that requires real reasoning. Offloading it would defeat the protocol's most valuable feature.

## [0.3.0] — 2026-05-19

### Added
- **Real-time anti-drift (protocol section 4)** — agent MUST stop and ask for confirmation before writing code that contradicts any entry in the last 50 decisions. Cannot silently override a logged decision. This is the protocol's most visible value to users.
- **Memory recap (protocol section 10)** — 3-line recap covering stack, in-flight item, and open drift. Triggers at every context reset: fresh session, idle > 15 min, after compaction, on explicit user request (`/context`, "where are we", etc.), or when memory is re-read mid-session.
- **Session-end recap (protocol section 11, new)** — before stopping, agent surfaces a 3-5 line summary: changed, logged, next, open question. Lets the user pick up later without scrolling.
- **Mono-file mode** — `template/vibememory.md` is a single self-contained file with the lite protocol + memory tables. Install via `install.sh --mode mono`. Upgrade path to full mode preserved.
- **PR-comment GitHub Action** — `.github/workflows/memory-pr-comment.yml` posts a sticky comment summarizing decisions and drifts added in each PR. Backed by `scripts/pr_comment.py` (3 unit tests).
- Drift detection AFTER the change moved to section 4.5 (kept distinct from real-time anti-drift in section 4).

### Changed
- `install.sh` accepts `--mode mono|full` (default: full)
- README quickstart restructured around mode choice
- Protocol version header: 0.2.0 → 0.3.0

## [0.2.0] — 2026-05-19

### Added
- `LICENSE` — MIT license file (README already advertised MIT)
- `CLAUDE.md` — Claude Code entry point mirroring `replit.md`
- `lovable.md` — Lovable entry point (positions `mem://` as a cache of `memory/`)
- `AGENTS.md` — generic entry point for agent-agnostic tooling
- `scripts/validate.py` — Python 3 stdlib-only validator for `memory/` files; `--check-freshness DAYS` flag
- `scripts/render.py` — renders JSONL logs into a chronological markdown journal
- `tests/test_validate.py` — 22-test suite covering validator + renderer
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
- Protocol section 2 reframed around **structural events** (integration activation, DB migration, new secret/dep, first instance of a new pattern, deployment target change, stack swap) instead of "≥2 files"
- Protocol section 10 confirmation line now has a trivial-session variant
- `scripts/validate.py` gains optional `--check-freshness DAYS` flag (warn-only, soft pressure for stale `progress.md` / `architecture.md`)
- `lovable.md` carves the `mem://` (rules) vs `memory/` (journal) boundary; documents Lovable-specific structural events (Cloud activation, publish, `secrets--*`, SQL migrations); provides a recommended Core snippet for `mem://index.md`

### Removed
- `examples/self-describing/` (content promoted to root `memory/`)

## [0.1.0] — 2026-05-18

### Added
- Initial protocol release: `MEMORY_PROTOCOL.md`, `replit.md`, blank `memory/` folder with README, `.replit` and `.gitignore`

[0.2.0]: https://github.com/gregherbe76/vibe-memory/releases/tag/v0.2.0
[0.1.0]: https://github.com/gregherbe76/vibe-memory/releases/tag/v0.1.0
