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

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM = ROOT / "memory"

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


def check_markdown(path: Path, max_lines: int, errors: list[str]) -> None:
    if not path.exists():
        fail(errors, f"{path.relative_to(ROOT)}: missing")
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > max_lines:
        fail(errors, f"{path.relative_to(ROOT)}: {len(lines)} lines exceeds {max_lines}-line limit")


def check_decisions(path: Path, errors: list[str]) -> int:
    if not path.exists():
        fail(errors, f"{path.relative_to(ROOT)}: missing")
        return 0
    count = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        count += 1
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            fail(errors, f"{path.relative_to(ROOT)}:{i}: invalid JSON ({e.msg})")
            continue
        if not isinstance(obj, dict):
            fail(errors, f"{path.relative_to(ROOT)}:{i}: must be JSON object")
            continue
        t = obj.get("type")
        if t not in DECISION_TYPES:
            fail(errors, f"{path.relative_to(ROOT)}:{i}: type {t!r} not in {sorted(DECISION_TYPES)}")
        required = ARCHIVE_REQUIRED if t == "archive" else DECISION_REQUIRED
        missing = required - obj.keys()
        if missing:
            fail(errors, f"{path.relative_to(ROOT)}:{i}: missing fields {sorted(missing)}")
        ts = obj.get("timestamp", "")
        if not ISO8601.match(ts):
            fail(errors, f"{path.relative_to(ROOT)}:{i}: timestamp {ts!r} is not ISO-8601")
        if t != "archive" and "impact" in obj and not isinstance(obj["impact"], list):
            fail(errors, f"{path.relative_to(ROOT)}:{i}: impact must be a list")
    return count


def check_drift(path: Path, errors: list[str]) -> int:
    if not path.exists():
        fail(errors, f"{path.relative_to(ROOT)}: missing")
        return 0
    count = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        count += 1
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            fail(errors, f"{path.relative_to(ROOT)}:{i}: invalid JSON ({e.msg})")
            continue
        if not isinstance(obj, dict):
            fail(errors, f"{path.relative_to(ROOT)}:{i}: must be JSON object")
            continue
        missing = DRIFT_REQUIRED - obj.keys()
        if missing:
            fail(errors, f"{path.relative_to(ROOT)}:{i}: missing fields {sorted(missing)}")
        if obj.get("type") != "drift":
            fail(errors, f"{path.relative_to(ROOT)}:{i}: type must be 'drift'")
        sev = obj.get("severity")
        if sev not in DRIFT_SEVERITY:
            fail(errors, f"{path.relative_to(ROOT)}:{i}: severity {sev!r} not in {sorted(DRIFT_SEVERITY)}")
        ts = obj.get("timestamp", "")
        if not ISO8601.match(ts):
            fail(errors, f"{path.relative_to(ROOT)}:{i}: timestamp {ts!r} is not ISO-8601")
    return count


def main() -> int:
    errors: list[str] = []
    check_markdown(MEM / "architecture.md", 200, errors)
    check_markdown(MEM / "progress.md", 100, errors)
    decisions = check_decisions(MEM / "decisions.jsonl", errors)
    drifts = check_drift(MEM / "drift.jsonl", errors)

    if errors:
        print(f"[validate] FAIL ({len(errors)} issue(s))")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"[validate] OK — {decisions} decision(s), {drifts} drift(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
