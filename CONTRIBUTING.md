# Contributing

vibe-memory is a small protocol repo. Most contributions fall into one of three categories.

## 1. Protocol changes (`MEMORY_PROTOCOL.md`)

Changes to the protocol itself are the most impactful — they change behavior for every consumer.

- Open an issue first describing the problem and the proposed change.
- In your PR, bump the `Protocol version` header at the top of `MEMORY_PROTOCOL.md` using semver (breaking → major, additive → minor, clarification → patch).
- Add a `CHANGELOG.md` entry under a new version section.
- Append a `decision` entry to `memory/decisions.jsonl` with `component: "protocol"` describing the change.

## 2. Agent entry points (`replit.md`, `CLAUDE.md`, `AGENTS.md`)

When a new agent runtime gains traction, add a dedicated entry point so users can opt in by simply having the file present.

- Mirror the structure of the existing entry points.
- Specify the agent's stable `author` identifier in the attribution section.
- Document any runtime-specific quirks (hooks, settings, sandboxing).

## 3. Tooling (`scripts/`, `.github/`, `.claude/`)

The validator, CI, schemas, and hooks are tooling. They must remain stdlib-only (no third-party Python deps) so the install path stays a single `curl | tar`.

- Add tests in `tests/` for any validator change. Run `python3 -m unittest discover -s tests` locally before pushing.
- Keep `scripts/validate.py` working under Python 3.10+.

## Conventions

- One JSON object per line in `*.jsonl`. ISO-8601 timestamps. `author` field required.
- `decisions.jsonl` and `drift.jsonl` are append-only — never edit or delete entries.
- `architecture.md` ≤ 200 lines, `progress.md` ≤ 100 lines.

## Running the validator

```sh
python3 scripts/validate.py          # validate ./memory
python3 scripts/validate.py path/to/memory
python3 -m unittest discover -s tests
```

## Releases

Tags follow `v<major>.<minor>.<patch>`. The version in `MEMORY_PROTOCOL.md`'s header and the latest `CHANGELOG.md` section must match the tag.
