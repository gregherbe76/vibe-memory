#!/usr/bin/env python3
"""Produce a markdown summary of memory changes between two refs.

Compares two snapshots of memory/decisions.jsonl and memory/drift.jsonl
(base vs head) and emits a markdown comment suitable for a PR.

Usage:
  python3 scripts/pr_comment.py BASE_DIR HEAD_DIR
  # BASE_DIR and HEAD_DIR each contain a memory/ subdirectory

Writes to stdout. Exits 0 always.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _parse_safe(line: str) -> dict | None:
    try:
        obj = json.loads(line)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def _new_entries(base_lines: list[str], head_lines: list[str]) -> list[dict]:
    base_set = set(base_lines)
    return [obj for line in head_lines if line not in base_set and (obj := _parse_safe(line))]


def render_comment(base_dir: Path, head_dir: Path) -> str:
    base_decisions = _load_lines(base_dir / "memory" / "decisions.jsonl")
    head_decisions = _load_lines(head_dir / "memory" / "decisions.jsonl")
    base_drifts = _load_lines(base_dir / "memory" / "drift.jsonl")
    head_drifts = _load_lines(head_dir / "memory" / "drift.jsonl")

    new_decisions = _new_entries(base_decisions, head_decisions)
    new_drifts = _new_entries(base_drifts, head_drifts)

    if not new_decisions and not new_drifts:
        return "_No vibe-memory changes in this PR._"

    parts: list[str] = ["## 🧠 vibe-memory changes in this PR", ""]

    if new_decisions:
        parts.append(f"**{len(new_decisions)} new decision(s):**")
        parts.append("")
        for d in new_decisions:
            t = d.get("type", "decision")
            component = d.get("component", "?")
            change = d.get("change", "")
            reason = d.get("reason", "")
            author = d.get("author", "?")
            parts.append(f"- **{t}** [{component}] — {change}")
            if reason:
                parts.append(f"  - _why:_ {reason}")
            parts.append(f"  - _by:_ `{author}`")
        parts.append("")

    if new_drifts:
        parts.append(f"**{len(new_drifts)} new drift(s):**")
        parts.append("")
        for d in new_drifts:
            severity = d.get("severity", "?")
            detected = d.get("detected", "")
            location = d.get("location", "")
            action = d.get("suggested_action", "")
            parts.append(f"- **{severity}** — {detected}")
            if location:
                parts.append(f"  - _at:_ `{location}`")
            if action:
                parts.append(f"  - _fix:_ {action}")
        parts.append("")

    parts.append("_Posted by the vibe-memory PR-comment workflow. Edit decisions/drift entries before merging if needed._")
    return "\n".join(parts).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diff vibe-memory between two snapshots and emit a PR comment.")
    parser.add_argument("base_dir", help="Directory containing base ref's memory/")
    parser.add_argument("head_dir", help="Directory containing head ref's memory/")
    args = parser.parse_args(argv)

    sys.stdout.write(render_comment(Path(args.base_dir), Path(args.head_dir)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
