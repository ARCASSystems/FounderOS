#!/usr/bin/env bash
# PreToolUse snapshot hook (bash variant).
#
# Before any Write/Edit/MultiEdit/NotebookEdit lands, hand the hook JSON to
# scripts/session_changes.py --record, which snapshots the file's pre-edit
# bytes and logs the change. Works with or without git - this is the pre-git
# undo floor for ZIP installs, and a second net everywhere else.
#
# This hook MUST exit 0 in all cases. It can never block or slow a write.

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
[ -n "$HOOK_DIR" ] || exit 0
REPO="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)"
[ -n "$REPO" ] || exit 0

SCRIPT="$REPO/scripts/session_changes.py"
[ -f "$SCRIPT" ] || exit 0

PY="$(command -v python3 2>/dev/null || command -v python 2>/dev/null)"
[ -n "$PY" ] || exit 0

export PYTHONUTF8=1
cat | "$PY" "$SCRIPT" --record 2>/dev/null

exit 0
