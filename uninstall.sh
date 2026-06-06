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
# Targets bash 3.2+ so the macOS system bash works without brew install bash.
# Avoid ${var,,} / declare -A / mapfile / readarray (bash 4+ only).

set -euo pipefail

# ---- constants ---------------------------------------------------------------

DEFAULT_TARGET="$HOME/founder-os"
# Pre-v1.37 installs landed here. Detected below so uninstall still finds an
# older install when the default moved to ~/founder-os.
LEGACY_TARGET="$HOME/.claude/plugins/founder-os"

# install.sh stopped copying hooks to ~/.claude/hooks/ in v1.24.1; hooks now live
# inside the install directory at $TARGET/.claude/hooks/ and are removed
# along with the install directory below. Do NOT re-introduce a global hook
# removal step here: a sibling PersonalOS install shares ~/.claude/hooks/.

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
  --target <path>  Uninstall from a custom path instead of ~/founder-os
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

if [[ -z "$TARGET" ]]; then
  # Prefer the current default ~/founder-os. Fall back to the legacy
  # ~/.claude/plugins/founder-os only if that is where the install actually is.
  if [[ -d "$LEGACY_TARGET" && ! -d "$DEFAULT_TARGET" ]]; then
    TARGET="$LEGACY_TARGET"
  else
    TARGET="$DEFAULT_TARGET"
  fi
fi

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
answer=$(printf '%s' "$answer" | tr '[:upper:]' '[:lower:]')
if [[ "$answer" != "y" && "$answer" != "yes" ]]; then
  info "Cancelled. Nothing was removed."
  exit 0
fi

echo ""

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
