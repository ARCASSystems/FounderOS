#!/usr/bin/env bash
# Start Founder OS - double-click this file to begin (Mac).
#
# What it does: opens Claude Code in this folder. On a fresh install it
# starts the setup wizard for you; after that it just opens your OS.
# It installs nothing and sends nothing anywhere.
#
# First run on a Mac: if macOS blocks this file because it cannot verify the
# developer, open System Settings > Privacy & Security, click Open Anyway, and
# confirm with Open (Apple's current steps, not yet run by us on a real Mac).
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
  # The desktop-app route below follows Anthropic's docs: the app includes
  # Claude Code but does not add the claude command to PATH, so this file
  # cannot open it. Not yet watched on a fresh install.
  echo ""
  echo "The Claude Code terminal tool was not found on this Mac."
  echo "Founder OS runs inside Claude Code, which needs a paid Claude plan"
  echo "(Pro, Max, Team or Enterprise). It is not free."
  echo ""
  echo "No terminal needed - use the Claude desktop app (opening the download page now):"
  echo "  1. Install it and sign in with your Claude account"
  echo "  2. Open the Code tab, click the folder control under the prompt box, pick this folder"
  echo "  3. Type: set up Founder OS"
  echo ""
  echo "Prefer the terminal? Install Claude Code from"
  echo "  https://code.claude.com/docs/en/quickstart"
  echo "then double-click this file again."
  echo ""
  echo "Stuck? See docs/troubleshooting.md in this folder."
  echo ""
  open "https://claude.com/download" 2>/dev/null || true
  read -r -p "Press Enter to close this window..."
  exit 1
fi

# Early heads-up only: Python 3.11+ check. The setup wizard runs the real
# preflight; this just saves you a surprise twenty minutes in.
#
# On a Mac without Apple's developer tools, /usr/bin/python3 is not Python. It
# is a stand-in that opens Apple's "install the command line developer tools"
# window the moment anything runs it. Probing it here would throw that window
# at the founder for a check that is only a heads-up, so on a Mac the /usr/bin
# copies are tried only when xcode-select reports the tools are installed.
mac_no_dev_tools=""
if [ "$(uname -s)" = "Darwin" ] && ! xcode-select -p >/dev/null 2>&1; then
  mac_no_dev_tools="1"
fi
py_ok=""
for py in python3 python; do
  py_path="$(command -v "$py" 2>/dev/null)" || continue
  case "$py_path" in
    /usr/bin/*) [ -z "$mac_no_dev_tools" ] || continue ;;
  esac
  if "$py_path" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
    py_ok="1"
    break
  fi
done
if [ -z "$py_ok" ]; then
  echo "One heads-up: Python 3.11 or newer was not found on this machine."
  echo "Founder OS scripts need it. Install it from python.org (free):"
  echo "  https://www.python.org/downloads/"
  if [ -n "$mac_no_dev_tools" ]; then
    echo "Use the python.org installer. If macOS offers to install developer tools"
    echo "instead, you can say no - Founder OS does not need them."
  fi
  echo "You can continue now - the setup wizard will remind you before it starts."
  echo ""
fi

# A finished OS opens. An interrupted setup resumes where it stopped. A fresh
# install starts the wizard. The completion marker is written by setup only
# after its final health check, so an identity file alone is no longer read as
# "setup finished" - it lands five phases early. An install set up before the
# markers existed has identity and neither marker; it opens normally, exactly
# as it always has.
# -s, not -f: a marker counts only if it actually holds a record. A zero-byte
# file is a write that failed, and reading one as proof let a truncated
# completion marker suppress setup on an install that had never finished it.
# Progress is read FIRST, and beats a completion marker sitting beside it.
# Finishing setup deletes the progress marker, so the two never coexist in a
# healthy install; when they do, the last thing that happened was a setup that
# started and did not finish. Resuming that is recoverable. Opening silently,
# which is what completion-wins did, is the exact failure these markers exist
# to end.
if [ -s "state/setup-progress.json" ]; then
  exec claude "continue Founder OS setup where it left off"
elif [ -s "state/setup-complete.json" ]; then
  exec claude
elif [ -f "core/identity.md" ]; then
  exec claude
else
  exec claude "set up Founder OS"
fi
