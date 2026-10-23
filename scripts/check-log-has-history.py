#!/usr/bin/env python3
"""Brain log history gate.

Exit 0 = `brain/log.md` has at least one dated entry (`### [YYYY-MM-DD]`,
`### YYYY-MM-DD` or `### YYYY-MM-DD HH:MM`, the shared _common heading).
Exit 1 = fresh install, no history yet. One-line reason printed to stdout.

Pure stdlib. brain-pass and similar skills call this before searching the log
so a first-time user does not trigger a "no content found" search loop.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ENTRY_DATE_HEADING  # noqa: E402

# The shared heading regex. The old local one required `### YYYY-MM-DD` and so
# read the log template's own `### [YYYY-MM-DD]` form as "no dated entries".
DATED_HEADING = ENTRY_DATE_HEADING


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
