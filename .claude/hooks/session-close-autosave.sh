#!/bin/bash
# Session-close auto-save (the caveman-git safety net).
#
# At session end, if there are uncommitted changes AND the privacy name guard is
# ACTIVE, record a local version so the founder never loses a session of work.
# If the guard is OFF (no name patterns), it WARNS instead of committing, so
# unscanned private names are never auto-committed. Local only: never pushes.
#
# Runs AFTER session-close-revenue-check in the Stop array, so the revenue check
# can inspect the working tree before this commits it.
#
# Trigger: Stop event (registered in .claude/settings.json). Exits 0 in all cases.

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
REPO_ROOT="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)" || exit 0
[ -z "$REPO_ROOT" ] && exit 0

# Platform guard. On Windows (Git Bash, MSYS, Cygwin) the PowerShell hook is the
# canonical writer. Exit early to avoid a double commit.
case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) exit 0 ;;
esac

# Only inside a Founder OS install.
[ ! -f "$REPO_ROOT/core/identity.md" ] && exit 0
[ ! -f "$REPO_ROOT/scripts/caveman_git.py" ] && exit 0

# Nothing to save -> stay silent.
changes="$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null)"
[ -z "$changes" ] && exit 0

# Guard-active check: hooksPath wired AND at least one real name pattern.
hooks_path="$(git -C "$REPO_ROOT" config core.hooksPath 2>/dev/null)"
patterns="$REPO_ROOT/scripts/private-name-patterns.txt"
guard_active=0
if [ "$hooks_path" = ".githooks" ] && [ -f "$patterns" ] && \
   grep -qE '^[[:space:]]*[^#[:space:]]' "$patterns" 2>/dev/null; then
  guard_active=1
fi

if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else exit 0
fi

if [ "$guard_active" = "1" ]; then
  echo ""
  echo "=== AUTO-SAVE ==="
  PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/caveman_git.py" save 2>&1
  echo "(Local only. Say \"undo to ...\" to roll back, \"what changed\" to see versions.)"
  echo "=== END AUTO-SAVE ==="
  echo ""
else
  echo ""
  echo "=== AUTO-SAVE PAUSED ==="
  echo "You have unsaved changes this session, but auto-save is paused because the"
  echo "privacy name guard is not active yet (no patterns in"
  echo "scripts/private-name-patterns.txt). The OS will not auto-commit content that"
  echo "has not been name-scanned."
  echo ""
  echo "Say \"save my work\" to save manually now, or add your name to"
  echo "scripts/private-name-patterns.txt (then run scripts/install-git-hooks.sh) to"
  echo "turn on auto-save."
  echo "=== END AUTO-SAVE ==="
  echo ""
fi

exit 0
