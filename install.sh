#!/usr/bin/env bash
# vibe-memory installer.
#
# Drops the protocol files, entry points, validator, optional Claude Code
# hook, and a blank memory/ folder into the current directory.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/gregherbe76/vibe-memory/main/install.sh | bash
#   curl -sSL https://raw.githubusercontent.com/gregherbe76/vibe-memory/main/install.sh | bash -s -- --ref v0.2.0
#
# Will not overwrite existing files. Re-run is safe.
set -euo pipefail

REF="main"
REPO="gregherbe76/vibe-memory"
MODE="full"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ref) REF="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

case "$MODE" in
  full|mono) ;;
  *) echo "unknown --mode: $MODE (expected: full, mono)" >&2; exit 2 ;;
esac

TARGET="${PWD}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "[install] fetching ${REPO}@${REF}"
curl -sSL "https://github.com/${REPO}/archive/${REF}.tar.gz" \
  | tar -xz -C "$TMP" --strip-components=1

copy() {
  local src="$1" dest="$2"
  if [ -e "${TARGET}/${dest}" ]; then
    echo "[install] skip ${dest} (already exists)"
    return
  fi
  mkdir -p "$(dirname "${TARGET}/${dest}")"
  cp -R "${TMP}/${src}" "${TARGET}/${dest}"
  echo "[install] wrote ${dest}"
}

if [ "$MODE" = "mono" ]; then
  copy "template/vibememory.md" "vibememory.md"
  echo
  echo "[install] done (mono mode)."
  echo "[install] edit vibememory.md, then start a session — the agent reads the whole file."
  exit 0
fi

copy "MEMORY_PROTOCOL.md"           "MEMORY_PROTOCOL.md"
copy "replit.md"                    "replit.md"
copy "CLAUDE.md"                    "CLAUDE.md"
copy "lovable.md"                   "lovable.md"
copy "AGENTS.md"                    "AGENTS.md"
copy "scripts/validate.py"          "scripts/validate.py"
copy "scripts/render.py"            "scripts/render.py"
copy "schemas"                      "schemas"
copy "template/memory"              "memory"
copy ".claude/hooks/session-start.sh" ".claude/hooks/session-start.sh"
copy ".claude/settings.json"        ".claude/settings.json"

chmod +x "${TARGET}/scripts/validate.py" 2>/dev/null || true
chmod +x "${TARGET}/scripts/render.py" 2>/dev/null || true
chmod +x "${TARGET}/.claude/hooks/session-start.sh" 2>/dev/null || true

echo
echo "[install] done (full mode)."
echo "[install] next: python3 scripts/validate.py"
