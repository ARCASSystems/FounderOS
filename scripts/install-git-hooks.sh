#!/usr/bin/env bash
# Install git hooks for Founder OS private-name guard.
# Idempotent: re-running is a no-op when already configured.
# Usage: ./scripts/install-git-hooks.sh [--dry-run]

set -e

DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
    esac
done

REPO_ROOT="$(git rev-parse --show-toplevel)"
PATTERNS_SRC="$REPO_ROOT/scripts/private-name-patterns.txt.template"
PATTERNS_DST="$REPO_ROOT/scripts/private-name-patterns.txt"

ACTION_HOOKS=""
ACTION_PATTERNS=""

current_hooks=$(git config core.hooksPath 2>/dev/null || echo "")
if [ "$current_hooks" != ".githooks" ]; then
    ACTION_HOOKS="set core.hooksPath to .githooks"
fi

if [ ! -f "$PATTERNS_DST" ]; then
    ACTION_PATTERNS="copy template to scripts/private-name-patterns.txt"
fi

if [ $DRY_RUN -eq 1 ]; then
    echo "--- dry-run: install-git-hooks.sh ---"
    if [ -n "$ACTION_HOOKS" ]; then
        echo "  WOULD: $ACTION_HOOKS"
    else
        echo "  SKIP: core.hooksPath already set to .githooks"
    fi
    if [ -n "$ACTION_PATTERNS" ]; then
        echo "  WOULD: $ACTION_PATTERNS"
    else
        echo "  SKIP: scripts/private-name-patterns.txt already exists"
    fi
    echo "--- end dry-run ---"
    exit 0
fi

if [ -n "$ACTION_HOOKS" ]; then
    git config core.hooksPath .githooks
    echo "Set core.hooksPath to .githooks"
else
    echo "core.hooksPath already set to .githooks — skipping"
fi

for hook in "$REPO_ROOT/.githooks/pre-commit" "$REPO_ROOT/.githooks/commit-msg"; do
    if [ ! -f "$hook" ]; then
        echo "Error: $hook is missing. Cannot install git hooks." >&2
        exit 1
    fi
    if [ ! -x "$hook" ]; then
        chmod +x "$hook" 2>/dev/null || {
            echo "Error: $hook is not executable and chmod failed." >&2
            exit 1
        }
    fi
done

if [ -n "$ACTION_PATTERNS" ]; then
    cp "$PATTERNS_SRC" "$PATTERNS_DST"
    echo "Created $PATTERNS_DST from template."
    echo "Edit it to add your private-name patterns before committing sensitive work."
else
    echo "scripts/private-name-patterns.txt already exists — skipping"
fi

# Force population: a patterns file with no active (non-comment) lines is theater -
# the guard scans nothing. Surface it loudly so the operator finishes the install.
ACTIVE_PATTERNS=$(grep -cvE '^[[:space:]]*(#|$)' "$PATTERNS_DST" 2>/dev/null || true)
ACTIVE_PATTERNS=${ACTIVE_PATTERNS:-0}
if [ "$ACTIVE_PATTERNS" -eq 0 ]; then
    echo ""
    echo "  !! WARNING: $PATTERNS_DST defines 0 patterns - the privacy guard is INACTIVE."
    echo "  !! Add at least your own name (e.g.  \\bYourName\\b ) before committing."
else
    echo "Privacy guard active: $ACTIVE_PATTERNS pattern(s) loaded."
fi

echo "Done. Run './scripts/install-git-hooks.sh --dry-run' to verify state."
