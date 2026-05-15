#!/usr/bin/env python3
"""Brain log history gate.

Exit 0 = `brain/log.md` has at least one `### YYYY-MM-DD` dated entry.
Exit 1 = fresh install, no history yet. One-line reason printed to stdout.

Pure stdlib. brain-pass and similar skills call this before searching the log
so a first-time user does not trigger a "no content found" search loop.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DATED_HEADING = re.compile(r"^###\s+\d{4}-\d{2}-\d{2}")


def check(root: Path) -> tuple[int, str]:
    path = root / "brain" / "log.md"
    if not path.exists():
        return 1, "brain/log.md has no dated entries yet. Skip log-based reasoning."

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as exc:
        return 1, f"brain/log.md could not be read: {exc}"

    for line in text.splitlines():
        if DATED_HEADING.match(line):
            return 0, "brain/log.md has dated entries."

    return 1, "brain/log.md has no dated entries yet. Skip log-based reasoning."


def main() -> int:
    parser = argparse.ArgumentParser(description="Brain log history gate.")
    parser.add_argument("--root", default=".", help="Founder OS root (default: current directory)")
    args = parser.parse_args()

    code, message = check(Path(args.root).resolve())
    print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
