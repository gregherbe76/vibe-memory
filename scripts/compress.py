#!/usr/bin/env python3
"""Compress old decisions.jsonl entries into an archive summary.

Implements protocol section 7 automatically using a cheap LLM:
when decisions.jsonl exceeds a threshold, the oldest N entries are
summarized into memory/decisions-archive-<date>.md and replaced in
the JSONL by a single "type":"archive" entry that references the
summary file.

The original entries are never deleted from git history — only from
the live decisions.jsonl. To recover them, check out an older commit.

Environment variables (required when not using --dry-run):
  VIBEMEM_LLM_ENDPOINT  OpenAI-compatible chat-completions URL
  VIBEMEM_LLM_MODEL     model name
  VIBEMEM_LLM_API_KEY   bearer token (omit for local Ollama)

Usage:
  compress.py [memory_dir] [--keep N] [--threshold N] [--dry-run]

By default, compresses the oldest entries when decisions.jsonl exceeds
500 lines, keeping the most recent 300 in the live file.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memory_assistant import call_llm  # noqa: E402

DEFAULT_MEM = Path(__file__).resolve().parent.parent / "memory"

SUMMARY_PROMPT = """\
You will be given a chronological list of architectural decisions, one
JSON object per line. Produce a concise markdown summary (400-800 words)
that captures:
- the major themes / phases of the project
- the most consequential decisions (which dependencies were adopted or
  dropped, which patterns were introduced, which were reversed)
- any rollbacks and why
- the convention shifts

Group by theme, not strict chronology. Quote timestamps inline where
they matter. Do not invent information. Output markdown only, starting
with a single H1 line.
"""


def compress(
    mem: Path,
    keep: int,
    threshold: int,
    dry_run: bool,
    today: datetime.date | None = None,
) -> tuple[int, str]:
    """Returns (entries_archived, summary_path_or_empty)."""
    today = today or datetime.date.today()
    decisions_path = mem / "decisions.jsonl"
    if not decisions_path.exists():
        print("[compress] decisions.jsonl missing, nothing to do")
        return 0, ""

    lines = [ln for ln in decisions_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) < threshold:
        print(f"[compress] {len(lines)} entries < {threshold} threshold, nothing to do")
        return 0, ""

    to_archive = lines[:-keep] if keep > 0 else lines
    to_keep = lines[-keep:] if keep > 0 else []

    if not to_archive:
        print("[compress] nothing to archive after applying --keep")
        return 0, ""

    first_ts = json.loads(to_archive[0]).get("timestamp", "?")
    last_ts = json.loads(to_archive[-1]).get("timestamp", "?")
    summary_filename = f"decisions-archive-{today.isoformat()}.md"
    summary_path = mem / summary_filename

    if dry_run:
        print(
            f"[compress] would archive {len(to_archive)} entries "
            f"({first_ts} → {last_ts}) into {summary_filename}; "
            f"would keep {len(to_keep)} in decisions.jsonl"
        )
        return len(to_archive), str(summary_path)

    print(
        f"[compress] archiving {len(to_archive)} entries ({first_ts} → {last_ts}) "
        f"via LLM..."
    )
    summary = call_llm(
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": "\n".join(to_archive)},
        ],
        temperature=0.1,
        max_tokens=1500,
    )
    summary_path.write_text(summary + "\n", encoding="utf-8")

    archive_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "type": "archive",
        "range": f"{first_ts}..{last_ts}",
        "summary_file": summary_filename,
        "count": len(to_archive),
    }
    new_lines = [json.dumps(archive_entry, separators=(",", ":"))] + to_keep
    decisions_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    print(
        f"[compress] wrote {summary_filename} and replaced "
        f"{len(to_archive)} entries with 1 archive entry in decisions.jsonl"
    )
    return len(to_archive), str(summary_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("memory_dir", nargs="?", default=str(DEFAULT_MEM))
    parser.add_argument("--keep", type=int, default=300, help="Entries to keep in the live JSONL")
    parser.add_argument(
        "--threshold",
        type=int,
        default=500,
        help="Compress only when decisions.jsonl has at least this many entries",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        compress(Path(args.memory_dir), args.keep, args.threshold, args.dry_run)
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"[compress] error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
