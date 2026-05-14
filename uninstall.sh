#!/usr/bin/env bash
# uninstall.sh - mirror of /founder-os:uninstall
#
# Usage:
#   bash uninstall.sh [--target <path>] [--dry-run] [--help]
#
# Removes the FounderOS system layer. Your operating data (core/, cadence/,
# context/, brain/, companies/, network/, clients/, MEMORY.md, CLAUDE.md)
# is NEVER touched. Those files are yours and survive uninstall.
#
# Bash-specific syntax (${var,,} lowercase, local) requires bash 4+.

set -euo pipefail

# ---- constants ---------------------------------------------------------------

DEFAULT_TARGET="$HOME/.claude/plugins/founder-os"
HOOKS_TARGET="$HOME/.claude/hooks"

# Hook files that install.sh copies - uninstall removes the same set.
# Names must match .claude/settings.json registered hooks exactly.
HOOK_FILES=(
  "session-start-brief.sh"
  "session-start-brief.ps1"
  "session-close-revenue-check.sh"
  "session-close-revenue-check.ps1"
  "post-tool-use-observation.sh"
  "post-tool-use-observation.ps1"
)

# User data directories that must never be removed.
PRESERVED_DIRS=(
  "core"
  "cadence"
  "context"
  "brain"
  "companies"
  "network"
  "clients"
)

# User Layer files. Must mirror the User Layer list in .claude/commands/update.md.
# If you add a User Layer path there, add it here too or default uninstall will delete it.
PRESERVED_FILES=(
  "MEMORY.md"
  "CLAUDE.md"
  "stack.json"
)

# ---- argument parsing --------------------------------------------------------

TARGET=""
DRY_RUN=false

show_help() {
  cat <<'EOF'
FounderOS uninstaller

Usage:
  bash uninstall.sh [options]

Options:
  --target <path>  Uninstall from a custom path instead of ~/.claude/plugins/founder-os
  --dry-run        List what would be removed without removing anything
  --help           Show this help

Your operating data (core/, cadence/, context/, brain/, CLAUDE.md, MEMORY.md)
is never removed. Those files are yours.
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      shift
      TARGET="${1:-}"
      if [[ -z "$TARGET" ]]; then
        echo "ERROR: --target requires a path argument." >&2
        exit 1
      fi
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --help|-h)
      show_help
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Run 'bash uninstall.sh --help' for usage." >&2
      exit 1
      ;;
  esac
  shift
done

[[ -z "$TARGET" ]] && TARGET="$DEFAULT_TARGET"

# ---- helpers -----------------------------------------------------------------

info()  { printf '  %s\n' "$*"; }
ok()    { printf '  [removed] %s\n' "$*"; }
skip()  { printf '  [skip] %s\n' "$*"; }
dryrun(){ printf '  [dry-run] would remove: %s\n' "$*"; }

# ---- inventory ---------------------------------------------------------------

echo ""
echo "FounderOS uninstaller"
echo "Target: $TARGET"
echo ""

if [[ ! -d "$TARGET" ]]; then
  info "Nothing to remove - $TARGET does not exist."
  exit 0
fi

echo "The following will be removed:"
echo ""
echo "  Install directory:"
echo "    $TARGET"
echo "  (system layer only - skills, templates, scripts, hooks source)"
echo ""
echo "  Hook copies:"
for hook in "${HOOK_FILES[@]}"; do
  hook_path="$HOOKS_TARGET/$hook"
  if [[ -f "$hook_path" ]]; then
    echo "    $hook_path"
  fi
done
echo ""
echo "The following will NOT be removed (your data):"
for dir in "${PRESERVED_DIRS[@]}"; do
  echo "    $TARGET/$dir/"
done
for file in "${PRESERVED_FILES[@]}"; do
  echo "    $TARGET/$file"
done
echo ""

# ---- confirm -----------------------------------------------------------------

if [[ "$DRY_RUN" == true ]]; then
  echo "Dry run - no changes made."
  exit 0
fi

printf 'Proceed with removal? [y/N] '
read -r answer
answer="${answer,,}"  # bash 4+ lowercase
if [[ "$answer" != "y" && "$answer" != "yes" ]]; then
  info "Cancelled. Nothing was removed."
  exit 0
fi

echo ""

# ---- remove hook copies ------------------------------------------------------

for hook in "${HOOK_FILES[@]}"; do
  hook_path="$HOOKS_TARGET/$hook"
  if [[ -f "$hook_path" ]]; then
    rm "$hook_path"
    ok "$hook_path"
  fi
done

# ---- remove install directory ------------------------------------------------

# We remove the whole directory EXCEPT the preserved paths.
# Strategy: move preserved paths out, delete directory, move back.
# This is safer than trying to enumerate and delete individual system files.

TMPDIR_PRESERVE=$(mktemp -d)

for dir in "${PRESERVED_DIRS[@]}"; do
  src="$TARGET/$dir"
  if [[ -d "$src" ]]; then
    mv "$src" "$TMPDIR_PRESERVE/$dir"
  fi
done

for file in "${PRESERVED_FILES[@]}"; do
  src="$TARGET/$file"
  if [[ -f "$src" ]]; then
    cp "$src" "$TMPDIR_PRESERVE/$file"
  fi
done

rm -rf "$TARGET"
ok "$TARGET (system layer)"

# Restore preserved paths if any were present
mkdir -p "$TARGET"
for dir in "${PRESERVED_DIRS[@]}"; do
  if [[ -d "$TMPDIR_PRESERVE/$dir" ]]; then
    mv "$TMPDIR_PRESERVE/$dir" "$TARGET/$dir"
  fi
done

for file in "${PRESERVED_FILES[@]}"; do
  if [[ -f "$TMPDIR_PRESERVE/$file" ]]; then
    mv "$TMPDIR_PRESERVE/$file" "$TARGET/$file"
  fi
done

rm -rf "$TMPDIR_PRESERVE"

# ---- done --------------------------------------------------------------------

echo ""
echo "FounderOS system layer removed."
echo ""
echo "Your operating data is preserved at $TARGET."
echo "Delete that folder manually if you want a clean removal."
echo ""
