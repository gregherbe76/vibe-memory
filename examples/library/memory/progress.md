# Progress

Last updated: 2026-05-10

## In progress

- Deprecating `Cache.flush_all()` in favor of `Cache.clear()` (started 2026-05-05). Warning shipped in 3.1.0; removal planned for 4.0.0.

## Next

1. Add `RedisStorage.scan_iter` so large caches can be enumerated without OOM
2. Write migration guide for `flush_all` -> `clear`
3. Investigate user report #218: TTL policy off-by-one at midnight UTC

## Completed (last 10)

- 2026-05-08 — Released 3.1.0
- 2026-04-30 — Added Python 3.13 to CI matrix
- 2026-04-20 — Switched build backend from setuptools to hatchling
- 2026-04-12 — Cut redis backend into a `redis` extra (was a hard dep)
- 2026-03-30 — Replaced custom typing helpers with `typing.Protocol`

## Blocked

None.
