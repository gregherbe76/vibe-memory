# Architecture

Last updated: 2026-05-02
Current version: 1.2.0

## Stack

- Rust 1.78 (edition 2021)
- `clap` 4 for CLI parsing
- `tokio` 1.38 for async runtime (only the HTTP fetch path)
- `reqwest` 0.12 with rustls for HTTPS
- `serde` + `serde_json` for config
- Published as `vendor-watch` on crates.io and as static binaries via GitHub Releases (cargo-dist)

## Components

- `src/main.rs` — entry point, sets up `clap` and dispatches to subcommands
- `src/cmd/` — one module per subcommand: `init`, `check`, `watch`, `report`
- `src/source/` — vendor source adapters (npm registry, PyPI, GitHub releases). One file per adapter implementing the `Source` trait.
- `src/store/` — local SQLite cache via `rusqlite`; schema in `src/store/schema.sql`
- `src/notify/` — desktop notification + webhook dispatch
- `tests/` — integration tests using `assert_cmd`

## Data flow

1. User runs a subcommand. `clap` parses args, builds a `Config`.
2. `cmd` module loads `~/.config/vendor-watch/config.toml`.
3. `source` adapters fetch current versions; `store` reads cached previous versions.
4. Diffs go to `notify` (stdout, desktop notification, or webhook).
5. `store` writes the new versions back.

## External dependencies

- npm registry (`https://registry.npmjs.org`)
- PyPI (`https://pypi.org/pypi`)
- GitHub Releases API (`https://api.github.com`; optional `GITHUB_TOKEN` for rate limit)
- Local SQLite file at `~/.local/share/vendor-watch/cache.db`

## Conventions

- One subcommand per file in `src/cmd/`; module name == subcommand name.
- Errors flow through `anyhow::Result` at the binary boundary; library code uses `thiserror`-derived enums.
- All HTTP calls go through `source::http_client()` so retry + timeout policy is one place.
- Tests in `tests/` use `assert_cmd` + `predicates`; no real network calls (use `wiremock`).
- `clippy::pedantic` is enabled in CI; warnings fail the build.
