#!/usr/bin/env bash
# Session-close change manifest hook (bash variant).
#
# At session end, render state/session-manifest.md - the list of every file
# this session wrote to, with a one-command restore per file - and print a
# one-line summary. The visibility half of the session-changes tracker.
#
# This hook MUST exit 0 in all cases.

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
[ -n "$HOOK_DIR" ] || exit 0
REPO="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)"
[ -n "$REPO" ] || exit 0

SCRIPT="$REPO/scripts/session_changes.py"
[ -f "$SCRIPT" ] || exit 0

PY="$(command -v python3 2>/dev/null || command -v python 2>/dev/null)"
[ -n "$PY" ] || exit 0

export PYTHONUTF8=1
cat | "$PY" "$SCRIPT" --manifest 2>/dev/null

exit 0
