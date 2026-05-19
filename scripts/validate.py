#!/usr/bin/env python3
"""Validate vibe-memory files.

Checks:
- memory/architecture.md exists and is under 200 lines
- memory/progress.md exists and is under 100 lines
- memory/decisions.jsonl: each line is JSON, has required fields, valid type, ISO-8601 timestamp
- memory/drift.jsonl: each line is JSON, has required fields, valid severity

Exit code: 0 on success, 1 on any failure. Prints a summary either way.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_MEM = Path(__file__).resolve().parent.parent / "memory"

ISO8601 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})$"
)

DECISION_TYPES = {"decision", "constraint", "convention", "dependency", "rollback", "archive"}
DRIFT_SEVERITY = {"low", "medium", "high"}

DECISION_REQUIRED = {"timestamp", "type", "component", "change", "reason", "impact", "author"}
DRIFT_REQUIRED = {"timestamp", "type", "severity", "detected", "location", "suggested_action"}
ARCHIVE_REQUIRED = {"timestamp", "type", "range", "summary_file", "count"}


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def check_markdown(path: Path, max_lines: int, errors: list[str], base: Path) -> None:
    if not path.exists():
        fail(errors, f"{_rel(path, base)}: missing")
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > max_lines:
        fail(errors, f"{_rel(path, base)}: {len(lines)} lines exceeds {max_lines}-line limit")


def check_decisions(path: Path, errors: list[str], base: Path) -> int:
    if not path.exists():
        fail(errors, f"{_rel(path, base)}: missing")
        return 0
    count = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        count += 1
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            fail(errors, f"{_rel(path, base)}:{i}: invalid JSON ({e.msg})")
            continue
        if not isinstance(obj, dict):
            fail(errors, f"{_rel(path, base)}:{i}: must be JSON object")
            continue
        t = obj.get("type")
        if t not in DECISION_TYPES:
            fail(errors, f"{_rel(path, base)}:{i}: type {t!r} not in {sorted(DECISION_TYPES)}")
        required = ARCHIVE_REQUIRED if t == "archive" else DECISION_REQUIRED
        missing = required - obj.keys()
        if missing:
            fail(errors, f"{_rel(path, base)}:{i}: missing fields {sorted(missing)}")
        ts = obj.get("timestamp", "")
        if not ISO8601.match(ts):
            fail(errors, f"{_rel(path, base)}:{i}: timestamp {ts!r} is not ISO-8601")
        if t != "archive" and "impact" in obj and not isinstance(obj["impact"], list):
            fail(errors, f"{_rel(path, base)}:{i}: impact must be a list")
    return count


def check_drift(path: Path, errors: list[str], base: Path) -> int:
    if not path.exists():
        fail(errors, f"{_rel(path, base)}: missing")
        return 0
    count = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        count += 1
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            fail(errors, f"{_rel(path, base)}:{i}: invalid JSON ({e.msg})")
            continue
        if not isinstance(obj, dict):
            fail(errors, f"{_rel(path, base)}:{i}: must be JSON object")
            continue
        missing = DRIFT_REQUIRED - obj.keys()
        if missing:
            fail(errors, f"{_rel(path, base)}:{i}: missing fields {sorted(missing)}")
        if obj.get("type") != "drift":
            fail(errors, f"{_rel(path, base)}:{i}: type must be 'drift'")
        sev = obj.get("severity")
        if sev not in DRIFT_SEVERITY:
            fail(errors, f"{_rel(path, base)}:{i}: severity {sev!r} not in {sorted(DRIFT_SEVERITY)}")
        ts = obj.get("timestamp", "")
        if not ISO8601.match(ts):
            fail(errors, f"{_rel(path, base)}:{i}: timestamp {ts!r} is not ISO-8601")
    return count


def validate(mem: Path) -> tuple[int, list[str], int, int]:
    """Validate a memory/ directory. Returns (exit_code, errors, decisions, drifts)."""
    base = mem.parent
    errors: list[str] = []
    check_markdown(mem / "architecture.md", 200, errors, base)
    check_markdown(mem / "progress.md", 100, errors, base)
    decisions = check_decisions(mem / "decisions.jsonl", errors, base)
    drifts = check_drift(mem / "drift.jsonl", errors, base)
    return (1 if errors else 0, errors, decisions, drifts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate vibe-memory files.")
    parser.add_argument(
        "memory_dir",
        nargs="?",
        default=str(DEFAULT_MEM),
        help="Path to memory/ directory (default: ./memory next to this script)",
    )
    args = parser.parse_args(argv)

    code, errors, decisions, drifts = validate(Path(args.memory_dir))
    if code != 0:
        print(f"[validate] FAIL ({len(errors)} issue(s))")
        for e in errors:
            print(f"  - {e}")
        return code
    print(f"[validate] OK — {decisions} decision(s), {drifts} drift(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
