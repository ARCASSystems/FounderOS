#!/usr/bin/env python3
"""Keep every download link pointing at the release that actually exists.

The download link is the first thing a stranger touches, and it is the easiest
thing in the repo to leave stale: VERSION moves, the link does not, and the
button on the front page hands out last quarter's build. Before v1.55 the link
dodged the problem by pointing at `archive/refs/heads/main.zip`, which is never
stale and is also not a release - it is the raw branch, extracting to
`FounderOS-main`, which is the developer artifact this release moved away from.

So the link is now pinned to a version, and this is what stops it rotting. It
reads VERSION, then checks that every download link in the docs points at the
matching release asset. `--fix` rewrites them.

  python scripts/check_download_links.py         # report, exit 1 on mismatch
  python scripts/check_download_links.py --fix   # rewrite, then report

The tests call check() directly, so a version bump that forgets the link fails
the suite rather than shipping.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

OWNER_REPO = "ARCASSystems/FounderOS"
RELEASES = f"https://github.com/{OWNER_REPO}/releases"

# Files that carry a download link a human clicks.
DOC_FILES = ("README.md", "docs/install.md")

# The shape we are enforcing, and the shape we are replacing.
ASSET_RE = re.compile(
    r"https://github\.com/ARCASSystems/FounderOS/releases/download/"
    r"v(?P<tag>[0-9][0-9A-Za-z.\-]*)/FounderOS-(?P<asset>[0-9][0-9A-Za-z.\-]*)\.zip"
)
BRANCH_ZIP_RE = re.compile(
    r"https://github\.com/ARCASSystems/FounderOS/archive/refs/heads/main\.zip"
)


def version() -> str:
    return (REPO / "VERSION").read_text(encoding="utf-8").strip().lstrip("v")


def asset_url(v: str) -> str:
    return f"{RELEASES}/download/v{v}/FounderOS-{v}.zip"


def check(root: Path | None = None) -> list[str]:
    """Return a list of problems. Empty list means every link is current."""
    root = root or REPO
    v = (root / "VERSION").read_text(encoding="utf-8").strip().lstrip("v")
    want = asset_url(v)
    problems: list[str] = []

    for rel in DOC_FILES:
        path = root / rel
        if not path.is_file():
            problems.append(f"{rel}: missing")
            continue
        text = path.read_text(encoding="utf-8")

        if BRANCH_ZIP_RE.search(text):
            problems.append(
                f"{rel}: still links the raw branch zip "
                f"(archive/refs/heads/main.zip). Point it at {want}"
            )

        found = ASSET_RE.findall(text)
        if not found:
            problems.append(f"{rel}: no release-asset download link found. Expected {want}")
            continue
        for tag, asset in found:
            if tag != v or asset != v:
                problems.append(
                    f"{rel}: links release v{tag} asset FounderOS-{asset}.zip "
                    f"but VERSION says {v}. Run: python scripts/check_download_links.py --fix"
                )
    return problems


def fix() -> int:
    v = version()
    want = asset_url(v)
    changed = 0
    for rel in DOC_FILES:
        path = REPO / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        new = ASSET_RE.sub(want, text)
        new = BRANCH_ZIP_RE.sub(want, new)
        if new != text:
            path.write_text(new, encoding="utf-8", newline="")
            print(f"  rewrote {rel}")
            changed += 1
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fix", action="store_true", help="Rewrite stale links in place.")
    args = ap.parse_args()

    if args.fix:
        n = fix()
        print(f"{n} file(s) updated to v{version()}")

    problems = check()
    if problems:
        print("Download links are out of date:")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"Download links point at v{version()}. Current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
