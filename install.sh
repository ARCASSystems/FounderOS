#!/usr/bin/env bash
# install.sh - one-line curl installer for FounderOS
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ARCASSystems/FounderOS/main/install.sh | bash
#   bash install.sh [--target <path>] [--dry-run] [--help]
#
# Bash-specific syntax is used (not POSIX sh) but the script targets bash 3.2+
# so the macOS one-liner works on the system bash. Avoid:
#   - ${var,,} / ${var^^} (use tr '[:upper:]' '[:lower:]' instead)
#   - declare -A / mapfile / readarray (bash 4+ only)
# Requires: bash 3.2+, git, python 3.11+

set -euo pipefail

# ---- constants ---------------------------------------------------------------

REPO_URL="https://github.com/ARCASSystems/FounderOS.git"
DEFAULT_TARGET="$HOME/.claude/plugins/founder-os"
HOOKS_TARGET="$HOME/.claude/hooks"

# ---- argument parsing --------------------------------------------------------

TARGET=""
DRY_RUN=false

show_help() {
  cat <<'EOF'
FounderOS installer

Usage:
  bash install.sh [options]

Options:
  --target <path>  Install to a custom path instead of ~/.claude/plugins/founder-os
  --dry-run        Print what would happen without making any changes
  --help           Show this help

After install, say "set up Founder OS" (or run /founder-os:setup) to personalise the OS.
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
      echo "Run 'bash install.sh --help' for usage." >&2
      exit 1
      ;;
  esac
  shift
done

[[ -z "$TARGET" ]] && TARGET="$DEFAULT_TARGET"

# ---- helpers -----------------------------------------------------------------

info()  { printf '  %s\n' "$*"; }
ok()    { printf '  [ok] %s\n' "$*"; }
err()   { printf '  [error] %s\n' "$*" >&2; }
step()  { printf '\n-- %s\n' "$*"; }
dryrun(){ printf '  [dry-run] %s\n' "$*"; }

run() {
  # Execute a command, or print it in dry-run mode.
  if [[ "$DRY_RUN" == true ]]; then
    dryrun "$*"
  else
    "$@"
  fi
}

# ---- prerequisite checks -----------------------------------------------------

step "Checking prerequisites"

check_bash_version() {
  local major
  major="${BASH_VERSINFO[0]:-0}"
  if [[ "$major" -lt 3 ]]; then
    err "bash 3.2 or newer is required (found bash $BASH_VERSION)."
    return 1
  fi
  if [[ "$major" -lt 4 ]]; then
    info "bash $BASH_VERSION (3.2 mode - works, but bash 4+ recommended)"
  else
    ok "bash $BASH_VERSION"
  fi
}

check_git() {
  if ! command -v git &>/dev/null; then
    err "git is not installed."
    info "Install git:"
    info "  macOS:  brew install git"
    info "  Ubuntu: sudo apt-get install git"
    info "  Windows (git-bash): https://git-scm.com/download/win"
    return 1
  fi
  ok "git $(git --version | awk '{print $3}')"
}

check_python() {
  local py_cmd py_version
  for py_cmd in python3 python; do
    if command -v "$py_cmd" &>/dev/null; then
      py_version=$("$py_cmd" -c 'import sys; print(".".join(str(x) for x in sys.version_info[:3]))' 2>/dev/null || true)
      if [[ -n "$py_version" ]]; then
        local major minor
        major=$(echo "$py_version" | cut -d. -f1)
        minor=$(echo "$py_version" | cut -d. -f2)
        if [[ "$major" -gt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -ge 11 ]]; }; then
          ok "python $py_version ($py_cmd)"
          return 0
        fi
      fi
    fi
  done
  err "Python 3.11 or newer is required."
  info "Download from https://www.python.org/downloads/"
  info "Or with a version manager: pyenv install 3.11"
  return 1
}

failed=false
check_bash_version || failed=true
check_git          || failed=true
check_python       || failed=true

# In dry-run mode, prereq failures become warnings: the founder still gets the
# planned-operations preview so they can see what install.sh would do once they
# install the missing prerequisites. A non-dry-run with failed prereqs still exits.
if [[ "$DRY_RUN" == true ]]; then
  echo ""
  step "Installing FounderOS to $TARGET (dry-run)"
  dryrun "Would install to: $TARGET"
  dryrun "Would copy hooks to: $HOOKS_TARGET"
  dryrun "Source repo: $REPO_URL"
  echo ""
  if [[ "$failed" == true ]]; then
    info "Dry-run complete. One or more prerequisites are missing - install them before running for real."
  else
    info "Dry-run complete. No changes were made."
  fi
  echo ""
  info "To run the real install: bash install.sh"
  exit 0
fi

if [[ "$failed" == true ]]; then
  echo ""
  err "One or more prerequisites are missing. Fix them and re-run this script."
  exit 1
fi

# ---- install or update -------------------------------------------------------

step "Installing FounderOS to $TARGET"

if [[ -d "$TARGET/.git" ]]; then
  # Existing install - offer update
  local_version="(unknown)"
  if [[ -f "$TARGET/VERSION" ]]; then
    local_version=$(cat "$TARGET/VERSION")
  fi
  info "FounderOS is already installed at $TARGET (version: $local_version)."
  printf '  Update to the latest version? [y/N] '
  read -r answer
  answer=$(printf '%s' "$answer" | tr '[:upper:]' '[:lower:]')
  if [[ "$answer" == "y" || "$answer" == "yes" ]]; then
    step "Updating FounderOS"
    git -C "$TARGET" pull --ff-only
    ok "Updated to $(cat "$TARGET/VERSION" 2>/dev/null || echo "latest")"
  else
    info "No changes made. Your install is at $TARGET."
    exit 0
  fi
else
  # Fresh install
  step "Cloning FounderOS"
  mkdir -p "$(dirname "$TARGET")"
  git clone --depth 1 "$REPO_URL" "$TARGET"
  ok "Cloned to $TARGET"
fi

# ---- copy hooks --------------------------------------------------------------

step "Wiring hooks to $HOOKS_TARGET"

mkdir -p "$HOOKS_TARGET"

hooks_src="$TARGET/.claude/hooks"
if [[ -d "$hooks_src" ]]; then
  for hook_file in "$hooks_src"/*.sh "$hooks_src"/*.ps1; do
    [[ -f "$hook_file" ]] || continue
    run cp "$hook_file" "$HOOKS_TARGET/"
    ok "Copied $(basename "$hook_file")"
  done
else
  info "No hook files found at $hooks_src - skipping hook copy."
fi

# ---- done --------------------------------------------------------------------

echo ""
echo "======================================================"
echo "  FounderOS installed successfully"
echo "======================================================"
echo ""
echo "  Location: $TARGET"
echo ""
echo "  Next step:"
echo "  Say \"set up Founder OS\" (or run /founder-os:setup)"
echo ""
echo "  That wizard builds your identity, priorities, and"
echo "  cadence files - takes 15 to 20 minutes the first time."
echo ""
echo "  Full docs: $TARGET/docs/first-day.md"
echo "======================================================"
echo ""
