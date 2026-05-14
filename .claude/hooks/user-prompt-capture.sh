#!/usr/bin/env bash
# UserPromptSubmit hook: capture-aware classifier.
# Reads stdin, hands to scripts/user-prompt-capture.py, prints stdout (a
# capture-suggestion note that Claude reads as added context). Never blocks
# the session - exits 0 even if Python is missing.

set +e

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
REPO="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)" || exit 0
[ -z "$REPO" ] && exit 0

# Platform guard. On Windows (Git Bash, MSYS, Cygwin) the PowerShell hook is
# the canonical writer. Without this guard both hooks fire and the model
# sees duplicate capture-suggestion notes on every prompt.
case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) exit 0 ;;
esac

SCRIPT="$REPO/scripts/user-prompt-capture.py"
[ ! -f "$SCRIPT" ] && exit 0

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  exit 0
fi

# Pass CLAUDE_PROJECT_DIR through so the python script can resolve the repo.
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$REPO}" "$PYTHON" "$SCRIPT" 2>/dev/null

exit 0
