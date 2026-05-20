#!/usr/bin/env python3
"""Optional companion script: route memory operations to a cheap LLM.

Reduces cost on heavy users by offloading memory writes (decision
entries, drift entries, recaps) to a smaller / cheaper model while the
main coding agent stays on a frontier model. Pure stdlib (urllib).

Talks to any OpenAI-compatible /v1/chat/completions endpoint:
  - Groq (Llama 3.1 8B/70B): https://api.groq.com/openai/v1/chat/completions
  - Together / Fireworks / OpenRouter: same shape
  - Anthropic via the OpenAI-compatible proxy: same shape
  - Local Ollama: http://localhost:11434/v1/chat/completions
  - OpenAI: https://api.openai.com/v1/chat/completions

Environment variables:
  VIBEMEM_LLM_ENDPOINT  full chat-completions URL
  VIBEMEM_LLM_MODEL     model name (e.g. llama-3.1-8b-instant)
  VIBEMEM_LLM_API_KEY   bearer token (omit for local Ollama)

If VIBEMEM_LLM_ENDPOINT is not set, the `recap` subcommand falls back to
a deterministic template; `decision-entry` and `drift-entry` exit with
an error.

Usage:
  memory_assistant.py recap [memory_dir]
  memory_assistant.py decision-entry "<description>" [--author NAME]
  memory_assistant.py drift-entry "<description>"
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_MEM = Path(__file__).resolve().parent.parent / "memory"

DECISION_SCHEMA_PROMPT = """\
Output ONE JSON object on a single line, no markdown, no commentary.
Required fields: timestamp (ISO-8601 UTC like 2026-05-19T00:00:00Z),
type (one of: decision, constraint, convention, dependency, rollback),
component (short kebab-case), change (one sentence),
reason (one sentence, the WHY), impact (array of file paths or modules),
author (string).
Example:
{"timestamp":"2026-05-19T12:00:00Z","type":"dependency","component":"orm","change":"adopt Drizzle 0.30","reason":"prisma was too heavy for serverless cold starts","impact":["package.json","lib/db/"],"author":"claude-code"}
"""

DRIFT_SCHEMA_PROMPT = """\
Output ONE JSON object on a single line, no markdown, no commentary.
Required fields: timestamp (ISO-8601 UTC), type ("drift"),
severity (one of: low, medium, high), detected (one sentence),
location (file:line or file), suggested_action (one sentence).
Example:
{"timestamp":"2026-05-19T12:00:00Z","type":"drift","severity":"medium","detected":"inline DB query bypasses lib/db/ convention","location":"app/billing/page.tsx:34","suggested_action":"move query to lib/db/billing.ts"}
"""


def _now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _first_section_item(text: str, section_header: str) -> str | None:
    """Return the first bullet/line under a markdown header."""
    pattern = rf"^#+\s+{re.escape(section_header)}\s*$"
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(pattern, line, re.IGNORECASE):
            for follow in lines[i + 1 :]:
                stripped = follow.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                stripped = re.sub(r"^[-*]\s*", "", stripped).strip()
                if stripped:
                    return stripped
    return None


def deterministic_recap(mem: Path) -> str:
    """Build the section-10 recap without an LLM (template fill)."""
    arch_path = mem / "architecture.md"
    prog_path = mem / "progress.md"
    drift_path = mem / "drift.jsonl"

    arch_text = arch_path.read_text(encoding="utf-8") if arch_path.exists() else ""
    prog_text = prog_path.read_text(encoding="utf-8") if prog_path.exists() else ""

    stack = _first_section_item(arch_text, "Stack") or "(stack not documented)"
    conventions = _first_section_item(arch_text, "Conventions") or ""
    in_flight = _first_section_item(prog_text, "In progress") or "(nothing in flight)"

    last_drift = "none"
    if drift_path.exists():
        lines = [ln for ln in drift_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if lines:
            try:
                obj = json.loads(lines[-1])
                detected = obj.get("detected", "").strip()
                location = obj.get("location", "").strip()
                last_drift = f"{detected} ({location})" if detected else "none"
            except json.JSONDecodeError:
                pass

    stack_line = stack if not conventions else f"{stack} Convention: {conventions}"
    if len(stack_line) > 140:
        stack_line = stack_line[:137] + "..."
    if len(in_flight) > 90:
        in_flight = in_flight[:87] + "..."

    return (
        "[memory] read architecture, progress, last 20 decisions, last 10 drifts.\n"
        f"Stack: {stack_line}\n"
        f"In flight: {in_flight}. Open drift: {last_drift}."
    )


def call_llm(messages: list[dict], temperature: float = 0.1, max_tokens: int = 400) -> str:
    """POST to an OpenAI-compatible chat completions endpoint."""
    endpoint = os.environ.get("VIBEMEM_LLM_ENDPOINT")
    model = os.environ.get("VIBEMEM_LLM_MODEL")
    if not endpoint or not model:
        raise RuntimeError(
            "VIBEMEM_LLM_ENDPOINT and VIBEMEM_LLM_MODEL must be set for LLM operations."
        )
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    api_key = os.environ.get("VIBEMEM_LLM_API_KEY")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"].strip()


def _extract_json_line(text: str) -> str:
    """Pull the first JSON object out of a possibly-noisy LLM response."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"no JSON object found in LLM response: {text!r}")
    return " ".join(match.group(0).split())


def generate_entry(kind: str, description: str, author: str = "memory-assistant") -> str:
    if kind == "decision":
        system_prompt = DECISION_SCHEMA_PROMPT
        hint = f' Author must be "{author}". Timestamp must be {_now_utc()}.'
    elif kind == "drift":
        system_prompt = DRIFT_SCHEMA_PROMPT
        hint = f" Timestamp must be {_now_utc()}."
    else:
        raise ValueError(f"unknown kind: {kind}")

    user_prompt = f"Description: {description}\n\n{hint}"

    raw = call_llm(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=400,
    )
    line = _extract_json_line(raw)
    # round-trip to verify JSON parseability
    parsed = json.loads(line)
    return json.dumps(parsed, separators=(",", ":"))


def cmd_recap(args: argparse.Namespace) -> int:
    mem = Path(args.memory_dir)
    print(deterministic_recap(mem))
    return 0


def cmd_decision_entry(args: argparse.Namespace) -> int:
    line = generate_entry("decision", args.description, author=args.author)
    print(line)
    return 0


def cmd_drift_entry(args: argparse.Namespace) -> int:
    line = generate_entry("drift", args.description)
    print(line)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_recap = sub.add_parser("recap", help="Print a 3-line section-10 recap (deterministic).")
    p_recap.add_argument("memory_dir", nargs="?", default=str(DEFAULT_MEM))
    p_recap.set_defaults(func=cmd_recap)

    p_dec = sub.add_parser("decision-entry", help="Generate a decisions.jsonl line from prose.")
    p_dec.add_argument("description")
    p_dec.add_argument("--author", default="memory-assistant")
    p_dec.set_defaults(func=cmd_decision_entry)

    p_dft = sub.add_parser("drift-entry", help="Generate a drift.jsonl line from prose.")
    p_dft.add_argument("description")
    p_dft.set_defaults(func=cmd_drift_entry)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (RuntimeError, urllib.error.URLError, ValueError, json.JSONDecodeError) as e:
        print(f"[memory_assistant] error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
