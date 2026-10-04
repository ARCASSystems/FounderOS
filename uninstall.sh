#!/usr/bin/env bash
# uninstall.sh - mirror of /founder-os:uninstall
#
# Usage:
#   bash uninstall.sh [--target <path>] [--dry-run] [--help]
#
# Removes the FounderOS system layer by NAMING what it removes, never by
# wiping and restoring. Anything this script does not name survives by
# construction: your operating data (core/, cadence/, context/, brain/,
# capture/, brands/, companies/, network/, clients/, roles/, system/, rules/,
# memory/, CLAUDE.md, MEMORY.md, stack.json, os-config.yaml) and any company
# or project folder setup created at the root. The earlier version of this
# script kept a preserve-list and deleted everything else, which destroyed
# any user path the list had fallen behind on. A remove-list cannot make
# that mistake: an unknown path is left alone, not deleted.
#
# The remove-list must mirror the System Layer list in
# .claude/commands/update.md. A path added there joins this list in the
# same commit.
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

# System Layer directories - the OS's machinery. This list is the ONLY thing
# this script deletes. rules/ is deliberately absent: update.md classifies it
# as founder-personalized, so uninstall leaves it too.
SYSTEM_DIRS=(
  "skills"
  "scripts"
  "templates"
  "notion-package"
  "docs"
  "updates"
  ".claude/commands"
  ".claude/hooks"
  ".claude-plugin"
)

# System Layer files at the root.
SYSTEM_FILES=(
  ".claude/settings.json"
  "VERSION"
  "AGENTS.md"
  "GEMINI.md"
  "AVATAR.md"
  "README.md"
  "CHANGELOG.md"
  "LICENSE"
  "install.sh"
  "uninstall.sh"
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

Removes only the named system layer (skills, scripts, templates, docs,
updates, commands, hooks, plugin manifests, root reference files). Everything
else in the folder is yours and is not touched: core/, cadence/, context/,
brain/, capture/, brands/, companies/, network/, clients/, roles/, system/,
rules/, memory/, CLAUDE.md, MEMORY.md, stack.json, os-config.yaml, and any
company or project folders setup created.
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

echo "The following system-layer paths will be removed:"
for dir in "${SYSTEM_DIRS[@]}"; do
  if [[ -d "$TARGET/$dir" ]]; then
    echo "    $TARGET/$dir/"
  fi
done
for file in "${SYSTEM_FILES[@]}"; do
  if [[ -f "$TARGET/$file" ]]; then
    echo "    $TARGET/$file"
  fi
done
echo ""
echo "Everything else in $TARGET is your data and will NOT be touched."
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

# ---- remove named system paths ----------------------------------------------

for dir in "${SYSTEM_DIRS[@]}"; do
  path="$TARGET/$dir"
  if [[ -d "$path" ]]; then
    rm -rf "$path"
    ok "$path"
  fi
done

for file in "${SYSTEM_FILES[@]}"; do
  path="$TARGET/$file"
  if [[ -f "$path" ]]; then
    rm -f "$path"
    ok "$path"
  fi
done

# .claude/ itself stays if anything of the user's is left in it; remove it
# only when empty.
if [[ -d "$TARGET/.claude" ]] && [[ -z "$(ls -A "$TARGET/.claude" 2>/dev/null)" ]]; then
  rmdir "$TARGET/.claude"
  ok "$TARGET/.claude (empty)"
fi

# ---- done --------------------------------------------------------------------

echo ""
echo "FounderOS system layer removed."
echo "Your data is still in: $TARGET"
echo "To remove your data too, delete that folder yourself - this script never does."
echo ""
echo "Plugin path: if you installed via the Claude Code plugin marketplace, also run"
echo "  /plugin uninstall founder-os"
echo "to de-register the plugin."
