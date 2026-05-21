#!/usr/bin/env python3
"""Brand voice profile readiness gate.

Exit 0 = brands/<slug>/voice.yml is filled and ready for brand-coupled output.
Exit 1 = not ready. One-line reason printed to stdout. Skills read this and stop.

Mirrors scripts/check-voice-ready.py for the operator voice, scoped to a single brand.
Pure stdlib.
"""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE_MARKERS = ("[CHOOSE", "<your", "[example:", "[YOUR ", "[BRAND ", "[lowercase-kebab")


def check(root: Path, slug: str) -> tuple[int, str]:
    voice_path = root / "brands" / slug / "voice.yml"
    positioning_path = root / "brands" / slug / "positioning.yml"

    if not voice_path.exists():
        return 1, f"brands/{slug}/voice.yml is missing. Run /founder-os:brand-voice-interview to create it."

    try:
        text = voice_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = voice_path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as exc:
        return 1, f"brands/{slug}/voice.yml could not be read: {exc}"

    for line in text.splitlines():
        if "{{" in line:
            return 1, f"brands/{slug}/voice.yml still has {{{{template}}}} markers. Run /founder-os:brand-voice-interview or fill it in by hand."
        for marker in TEMPLATE_MARKERS:
            if marker in line:
                return 1, f"brands/{slug}/voice.yml still has template defaults ({marker}). Run /founder-os:brand-voice-interview or fill it in by hand."

    # Positioning is a soft check - voice can be used without it but campaign-from-theme needs it.
    if not positioning_path.exists():
        return 0, f"brands/{slug}/voice.yml is ready. (positioning.yml missing - campaign-from-theme will prompt to complete it.)"

    return 0, f"brands/{slug}/voice.yml is ready."


def main() -> int:
    parser = argparse.ArgumentParser(description="Brand voice readiness gate.")
    parser.add_argument("--root", default=".", help="Founder OS root (default: current directory)")
    parser.add_argument("--brand", required=True, help="Brand slug under brands/<slug>/")
    args = parser.parse_args()

    code, message = check(Path(args.root).resolve(), args.brand)
    print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
