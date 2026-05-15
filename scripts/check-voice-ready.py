#!/usr/bin/env python3
"""Voice profile readiness gate.

Exit 0 = `core/voice-profile.yml` is filled and ready for voice-coupled output.
Exit 1 = not ready. One-line reason printed to stdout. Skills read this and stop.

Pure stdlib. Same template-marker conventions as scripts/brain-snapshot.py.
"""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE_MARKERS = ("[CHOOSE", "[NOT SET]", "<your", "[example:", "[YOUR ")


def check(root: Path) -> tuple[int, str]:
    path = root / "core" / "voice-profile.yml"
    if not path.exists():
        return 1, "core/voice-profile.yml is missing. Run /founder-os:setup to create it."

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as exc:
        return 1, f"core/voice-profile.yml could not be read: {exc}"

    for line in text.splitlines():
        if "{{" in line:
            return 1, "core/voice-profile.yml still has {{template}} markers. Run /founder-os:setup or fill it in by hand."
        for marker in TEMPLATE_MARKERS:
            if marker in line:
                return 1, f"core/voice-profile.yml still has template defaults ({marker}). Run /founder-os:setup or fill it in by hand."

    return 0, "core/voice-profile.yml is ready."


def main() -> int:
    parser = argparse.ArgumentParser(description="Voice profile readiness gate.")
    parser.add_argument("--root", default=".", help="Founder OS root (default: current directory)")
    args = parser.parse_args()

    code, message = check(Path(args.root).resolve())
    print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
