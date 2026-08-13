#!/usr/bin/env python3
"""open_folder.py - open a folder in the system file manager, safely.

Why a script for something this small: the `where` skill used to close with
"open it with `explorer` / `open` / `xdg-open` on the discovered path", which
hands a shell command an argument that came out of a directory scan. A folder
name is founder-controlled data - it can contain spaces, quotes, or anything
else a founder types into a folder name - and the outside review of v1.53.0
was right to flag an unconstrained shell interpolation there, even unexploited.
This script removes the interpolation: the path is passed as one argv element
with no shell involved, and it must resolve inside the OS folder.

Standard library only. Opens exactly one existing directory under the root and
does nothing else - no files, no URLs, no creation, no fallback guessing.

Usage:
  python scripts/open_folder.py "Client Work/march-pitch"
  python scripts/open_folder.py "Client Work" --root /path/to/os
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def open_folder(target: Path) -> None:
    """One argv element, no shell, per platform. os.startfile is the Windows
    native call; the other two run the platform opener with shell=False."""
    if sys.platform.startswith("win"):
        os.startfile(str(target))  # noqa: S606 - the resolved, contained dir
    elif sys.platform == "darwin":
        subprocess.run(["open", str(target)], shell=False, check=True, timeout=15)
    else:
        subprocess.run(["xdg-open", str(target)], shell=False, check=True, timeout=15)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Open one folder inside the OS folder.")
    p.add_argument("path", help="folder to open, relative to the OS folder")
    p.add_argument("--root", default=str(REPO_ROOT))
    a = p.parse_args(argv)

    root = Path(a.root).resolve()
    target = (root / a.path).resolve()

    if target != root and root not in target.parents:
        print(f"Not opened: {a.path} points outside your Founder OS folder, "
              "and this only opens folders inside it.", file=sys.stderr)
        return 2
    if not target.is_dir():
        print(f"Not opened: there is no folder at {a.path} right now. "
              "It may have been moved or renamed - ask \"where is my work\" to find it.",
              file=sys.stderr)
        return 1
    try:
        open_folder(target)
    except Exception:
        print(f"Your system did not open the folder. The full location, ready to "
              f"paste into your file manager:\n{target}", file=sys.stderr)
        return 1
    print(f"Opened {target.name}/ in your file manager.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
