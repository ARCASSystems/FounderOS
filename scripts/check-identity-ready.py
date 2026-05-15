#!/usr/bin/env python3
"""Identity readiness gate.

Exit 0 = `core/identity.md` exists and contains no template markers.
Exit 1 = setup not done. One-line reason printed to stdout.

Pure stdlib. Skills that reason about the founder's real situation call this
before producing output.
"""

from __future__ import annotations

import argparse
from pathlib import Path


BLOCKING_MARKERS = ("[FILL]",)


def check(root: Path) -> tuple[int, str]:
    path = root / "core" / "identity.md"
    if not path.exists():
        return 1, "core/identity.md is missing. Run /founder-os:setup first."

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as exc:
        return 1, f"core/identity.md could not be read: {exc}"

    if "{{" in text:
        return 1, "core/identity.md still has {{template}} markers. Run /founder-os:setup first."
    for marker in BLOCKING_MARKERS:
        if marker in text:
            return 1, f"core/identity.md still has unfilled fields ({marker}). Run /founder-os:setup first."

    return 0, "core/identity.md is ready."


def main() -> int:
    parser = argparse.ArgumentParser(description="Identity readiness gate.")
    parser.add_argument("--root", default=".", help="Founder OS root (default: current directory)")
    args = parser.parse_args()

    code, message = check(Path(args.root).resolve())
    print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
