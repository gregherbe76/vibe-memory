# Architecture

Last updated: 2026-05-10
Current version: 3.1.0

## Stack

- Python 3.10+ (3.10, 3.11, 3.12, 3.13 in CI)
- Pure Python, no compiled extensions
- Build: `hatchling`
- Test: `pytest`, `pytest-asyncio`, `hypothesis`
- Lint: `ruff`, `mypy --strict`
- Distributed on PyPI as `flatcache`

## Components

- `flatcache/__init__.py` — public API: `Cache`, `AsyncCache`, `CacheError`, `EvictionPolicy`
- `flatcache/cache.py` — sync `Cache` implementation
- `flatcache/asyncio.py` — async `AsyncCache` implementation; shares storage layer
- `flatcache/storage/` — pluggable backends: `memory`, `file`, `redis` (extra)
- `flatcache/policy/` — eviction policies: LRU, LFU, TTL
- `flatcache/_internal/` — anything under here is unstable; public users must not import it
- `tests/` — mirror of source layout; one test module per source module

## Data flow

1. User constructs `Cache(storage=..., policy=...)`.
2. `get`/`set`/`delete` calls go to the policy, which consults storage and decides what to evict.
3. Storage backends implement `Storage` protocol (5 methods).
4. `AsyncCache` is a thin wrapper: same storage layer, async methods.

## External dependencies

- `redis` extra: `pip install flatcache[redis]` pulls in `redis>=5`
- No required runtime deps for the core package

## Conventions

- Public API surface is **only** what's re-exported in `flatcache/__init__.py`.
- Breaking changes require a major version bump and a deprecation window of one minor version.
- Type hints are mandatory; `mypy --strict` is enforced in CI.
- Tests use `pytest` with parametrization, no xunit-style classes.
- Docstrings follow Google style; rendered via `mkdocs-material`.
