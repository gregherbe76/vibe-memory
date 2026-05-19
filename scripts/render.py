#!/usr/bin/env python3
"""Render decisions.jsonl and drift.jsonl into a human-readable markdown journal.

The JSONL files remain the source of truth. This script produces a derived view
for humans (and agents that prefer reading markdown). Output is written to
stdout by default, or to a path with --output.

Usage:
  python3 scripts/render.py                       # render ./memory to stdout
  python3 scripts/render.py path/to/memory
  python3 scripts/render.py --output JOURNAL.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_MEM = Path(__file__).resolve().parent.parent / "memory"


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _date(ts: str) -> str:
    return ts.split("T", 1)[0] if "T" in ts else ts


def render(mem: Path) -> str:
    decisions = _load(mem / "decisions.jsonl")
    drifts = _load(mem / "drift.jsonl")

    by_date: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for d in decisions:
        by_date[_date(d.get("timestamp", ""))].append(("decision", d))
    for d in drifts:
        by_date[_date(d.get("timestamp", ""))].append(("drift", d))

    lines = [
        "# Memory journal",
        "",
        "_Auto-generated from `memory/decisions.jsonl` and `memory/drift.jsonl`. Do not edit by hand — edit the JSONL files (append-only) and regenerate._",
        "",
        f"- {len(decisions)} decision(s)",
        f"- {len(drifts)} drift(s)",
        "",
    ]

    for date in sorted(by_date.keys()):
        lines.append(f"## {date}")
        lines.append("")
        for kind, entry in sorted(by_date[date], key=lambda kv: kv[1].get("timestamp", "")):
            if kind == "decision":
                t = entry.get("type", "decision")
                component = entry.get("component", "?")
                change = entry.get("change", "")
                reason = entry.get("reason", "")
                impact = entry.get("impact", [])
                author = entry.get("author", "?")
                if t == "archive":
                    lines.append(
                        f"- **archive** ({entry.get('range', '?')}) → `{entry.get('summary_file', '?')}` ({entry.get('count', '?')} entries)"
                    )
                else:
                    lines.append(f"- **{t}** [{component}] — {change}")
                    if reason:
                        lines.append(f"    - _why:_ {reason}")
                    if impact:
                        impacts = ", ".join(f"`{p}`" for p in impact)
                        lines.append(f"    - _impact:_ {impacts}")
                    lines.append(f"    - _author:_ {author}")
            else:
                severity = entry.get("severity", "?")
                detected = entry.get("detected", "")
                location = entry.get("location", "")
                action = entry.get("suggested_action", "")
                lines.append(f"- **drift** ({severity}) — {detected}")
                if location:
                    lines.append(f"    - _at:_ `{location}`")
                if action:
                    lines.append(f"    - _fix:_ {action}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render vibe-memory JSONL logs to markdown.")
    parser.add_argument(
        "memory_dir",
        nargs="?",
        default=str(DEFAULT_MEM),
        help="Path to memory/ directory (default: ./memory next to this script)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Write to this path instead of stdout",
    )
    args = parser.parse_args(argv)

    out = render(Path(args.memory_dir))
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"[render] wrote {args.output} ({len(out.splitlines())} lines)", file=sys.stderr)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
