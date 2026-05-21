#!/usr/bin/env python3
"""List captured brand voices under brands/<slug>/.

Reports each brand as one line: <slug>\t<display_name>\t<voice_status>\t<positioning_status>

Used by writing skills to discover brands the operator has set up. Backward-compatible:
if `brands/` does not exist, exits 0 with no output and writing skills fall through
to operator voice as today.

Pure stdlib. No external dependencies.
"""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE_MARKERS = ("[CHOOSE", "<your", "[example:", "[YOUR ", "[BRAND ", "[lowercase-kebab")


def file_status(path: Path) -> str:
    """Return 'ready', 'template', or 'missing' for a YAML file."""
    if not path.exists():
        return "missing"
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            return "missing"

    for line in text.splitlines():
        if "{{" in line:
            return "template"
        for marker in TEMPLATE_MARKERS:
            if marker in line:
                return "template"
    return "ready"


def extract_display_name(voice_path: Path) -> str:
    """Best-effort extraction of display_name from a YAML file without a YAML dep."""
    if not voice_path.exists():
        return "[unknown]"
    try:
        text = voice_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return "[unknown]"
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("display_name:"):
            value = s.split(":", 1)[1].strip().strip('"').strip("'")
            return value or "[unknown]"
    return "[unknown]"


def main() -> int:
    parser = argparse.ArgumentParser(description="List brand voices under brands/<slug>/.")
    parser.add_argument("--root", default=".", help="Founder OS root (default: current directory)")
    parser.add_argument("--format", default="tsv", choices=["tsv", "human"], help="Output format")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    brands_dir = root / "brands"

    if not brands_dir.exists():
        return 0

    slugs = sorted(p.name for p in brands_dir.iterdir() if p.is_dir() and not p.name.startswith("."))

    if not slugs:
        return 0

    for slug in slugs:
        brand_dir = brands_dir / slug
        voice = brand_dir / "voice.yml"
        positioning = brand_dir / "positioning.yml"

        voice_status = file_status(voice)
        positioning_status = file_status(positioning)
        display_name = extract_display_name(voice) if voice.exists() else extract_display_name(positioning)

        if args.format == "tsv":
            print(f"{slug}\t{display_name}\t{voice_status}\t{positioning_status}")
        else:
            voice_marker = {"ready": "[ready]", "template": "[template]", "missing": "[missing]"}[voice_status]
            pos_marker = {"ready": "[ready]", "template": "[template]", "missing": "[missing]"}[positioning_status]
            print(f"  - {display_name} (slug: {slug})  voice {voice_marker}  positioning {pos_marker}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
