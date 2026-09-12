#!/usr/bin/env bash
# Put the Founder OS icon on this folder (macOS).
#
# Windows reads desktop.ini and gets the icon on the first double-click of
# Start Founder OS.bat. macOS has no equivalent file: a custom folder icon
# lives in the folder's own resource fork, which has to be written by hand.
# This writes it.
#
#   bash scripts/set_folder_icon.sh            # brand the Founder OS folder
#   bash scripts/set_folder_icon.sh ~/Work/OS  # brand another folder
#
# It is cosmetic. It never touches your data, it never fails the install, and
# if the tools it needs are missing it says so in one line and exits cleanly.
#
# The tools are Rez, DeRez and SetFile, which arrive with the Xcode Command
# Line Tools. Most Macs used for development already have them. If yours does
# not, `xcode-select --install` is a one-time 2-minute download, or you can
# skip this entirely - the OS works the same either way.

set -u

here="$(cd "$(dirname "$0")/.." && pwd)"
target="${1:-$here}"
icon="$here/assets/arcas.icns"

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This script is for macOS. On Windows the icon is set by Start Founder OS.bat."
  exit 0
fi

if [ ! -f "$icon" ]; then
  echo "No icon at assets/arcas.icns - nothing to set. The OS is unaffected."
  exit 0
fi

if [ ! -d "$target" ]; then
  echo "Not a folder: $target"
  exit 1
fi

for tool in Rez DeRez SetFile; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Skipping the folder icon: $tool is not installed."
    echo "It comes with the Xcode Command Line Tools: xcode-select --install"
    echo "This is cosmetic only. Founder OS works exactly the same without it."
    exit 0
  fi
done

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

cp "$icon" "$work/icon.icns"

# Give the icns file its own icon, then lift that resource out and staple it
# to the folder as the magic Icon? file. The trailing carriage return in the
# name is not a typo - the filename is literally "Icon" plus CR.
sips -i "$work/icon.icns" >/dev/null 2>&1 || true
DeRez -only icns "$work/icon.icns" > "$work/icon.rsrc" 2>/dev/null

if [ ! -s "$work/icon.rsrc" ]; then
  echo "Could not read the icon resource. Leaving the folder as it is."
  exit 0
fi

icon_file="$target/Icon$(printf '\r')"
rm -f "$icon_file"
Rez -append "$work/icon.rsrc" -o "$icon_file" 2>/dev/null

# Check the marker file actually exists before claiming anything. Printing
# "Icon set on:" whatever happened is how a cosmetic step turns into a bug
# report: the founder believes it worked and wonders why Finder disagrees.
if [ ! -s "$icon_file" ]; then
  echo "Could not write the icon marker in: $target"
  echo "Nothing was changed. Founder OS works exactly the same without it."
  exit 0
fi

SetFile -a C "$target"      # the folder has a custom icon
SetFile -a V "$icon_file"   # and the marker file stays out of sight

echo "Icon set on: $target"
echo "Finder caches folder icons, so it can take a moment or a window reopen."
