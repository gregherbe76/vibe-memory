#!/bin/bash
# SessionStart hook for vibe-memory.
#
# Validates memory/ files at the start of each Claude Code on the web
# session so the agent knows immediately if the append-only logs are
# malformed. Runs only in the remote environment; no-op locally.
#
# No external dependencies — the validator is plain Python 3 stdlib.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

if [ ! -f scripts/validate.py ]; then
  echo "[session-start] scripts/validate.py not found, skipping memory validation" >&2
  exit 0
fi

python3 scripts/validate.py
