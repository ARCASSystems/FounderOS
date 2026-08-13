#!/usr/bin/env bash
# Start Founder OS - double-click this file to begin (Mac).
#
# What it does: opens Claude Code in this folder. On a fresh install it
# starts the setup wizard for you; after that it just opens your OS.
# It installs nothing and sends nothing anywhere.
#
# First run on a Mac: if macOS says it "cannot be opened because it is from
# an unidentified developer", right-click the file and choose Open once.
# That is macOS being careful with downloaded scripts, not an error here.
# This file is plain text - open it in any editor to read everything it does.

set -u
cd "$(dirname "$0")" || exit 1

# Claude Code installs land in different places depending on how it was
# installed; make sure the common ones are reachable from a double-click.
for p in "$HOME/.local/bin" "/usr/local/bin" "/opt/homebrew/bin" "$HOME/.claude/local"; do
  case ":$PATH:" in
    *":$p:"*) ;;
    *) PATH="$p:$PATH" ;;
  esac
done
export PATH

if ! command -v claude >/dev/null 2>&1; then
  echo ""
  echo "Claude Code is not installed yet - the free app Founder OS runs inside."
  echo ""
  echo "  1. Download it at https://claude.ai/code  (opening that page now)"
  echo "  2. Install it and sign in with your Claude account (Pro or Max plan)"
  echo "  3. Double-click this file again"
  echo ""
  open "https://claude.ai/code" 2>/dev/null || true
  read -r -p "Press Enter to close this window..."
  exit 1
fi

# Early heads-up only: Python 3.11+ check. The setup wizard runs the real
# preflight; this just saves you a surprise twenty minutes in.
py_ok=""
for py in python3 python; do
  if command -v "$py" >/dev/null 2>&1 \
    && "$py" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
    py_ok="1"
    break
  fi
done
if [ -z "$py_ok" ]; then
  echo "One heads-up: Python 3.11 or newer was not found on this machine."
  echo "Founder OS scripts need it. Free download: https://www.python.org/downloads/"
  echo "You can continue now - the setup wizard will remind you before it starts."
  echo ""
fi

# A finished OS opens. An interrupted setup resumes where it stopped. A fresh
# install starts the wizard. The completion marker is written by setup only
# after its final health check, so an identity file alone is no longer read as
# "setup finished" - it lands five phases early. An install set up before the
# markers existed has identity and neither marker; it opens normally, exactly
# as it always has.
if [ -f "state/setup-complete.json" ]; then
  exec claude
elif [ -f "state/setup-progress.json" ]; then
  exec claude "continue Founder OS setup where it left off"
elif [ -f "core/identity.md" ]; then
  exec claude
else
  exec claude "set up Founder OS"
fi
