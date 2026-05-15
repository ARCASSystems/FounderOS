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

if [ -n "$ACTION_PATTERNS" ]; then
    cp "$PATTERNS_SRC" "$PATTERNS_DST"
    echo "Created $PATTERNS_DST from template."
    echo "Edit it to add your private-name patterns before committing sensitive work."
else
    echo "scripts/private-name-patterns.txt already exists — skipping"
fi

echo "Done. Run './scripts/install-git-hooks.sh --dry-run' to verify state."
