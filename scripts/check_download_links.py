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
  python scripts/check_download_links.py --require-published
                                                 # ALSO ask GitHub whether the
                                                 # asset exists; exit 1 if not

A link that matches VERSION can still point at nothing: v1.56.0's link said
"Current" here while the asset it named returned 404, because the text check
never leaves the machine. --require-published closes that. It sends one HEAD
request per link (following GitHub's redirect to the file store) and fails
unless each answers. Run it after the assets are uploaded, as the last step of
a release. Without the flag the script stays fully offline, so the test suite
and CI never depend on the network.

The docs may also use the stable link `releases/latest/download/FounderOS.zip`,
which build_release.py makes possible by writing an unversioned copy of the
asset. It never goes stale by version, so the text check accepts it; only
--require-published can say whether it resolves.

The tests call check() directly, so a version bump that forgets the link fails
the suite rather than shipping.
"""

from __future__ import annotations

import argparse
import re
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

OWNER_REPO = "ARCASSystems/FounderOS"
RELEASES = f"https://github.com/{OWNER_REPO}/releases"
STABLE_URL = f"{RELEASES}/latest/download/FounderOS.zip"
STABLE_RE = re.compile(
    r"https://github\.com/ARCASSystems/FounderOS/releases/latest/download/FounderOS\.zip"
)

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
            if STABLE_RE.search(text):
                continue  # the stable latest link: right for every version
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


def urls_to_verify(root: Path | None = None) -> list[str]:
    """The download URLs a release must actually serve: the versioned asset
    for VERSION always, plus the stable latest link when any doc uses it."""
    root = root or REPO
    v = (root / "VERSION").read_text(encoding="utf-8").strip().lstrip("v")
    urls = [asset_url(v)]
    for rel in DOC_FILES:
        path = root / rel
        if path.is_file() and STABLE_RE.search(path.read_text(encoding="utf-8")):
            urls.append(STABLE_URL)
            break
    return urls


def _status(url: str, method: str, extra: dict | None = None, timeout: float = 20) -> int:
    """HTTP status for one request, following redirects. Errors that carry a
    status return it; anything else (no network, DNS) raises URLError."""
    headers = {"User-Agent": "founder-os-release-check"}
    headers.update(extra or {})
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def asset_published(url: str, timeout: float = 20) -> tuple[bool, str]:
    """(exists, reason). HEAD first; the file store behind GitHub's redirect
    can refuse HEAD on a signed URL, so a 403 or 405 is retried as a one-byte
    ranged GET before it counts against the asset."""
    try:
        code = _status(url, "HEAD", timeout=timeout)
        if code in (403, 405):
            code = _status(url, "GET", {"Range": "bytes=0-0"}, timeout=timeout)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        return False, f"could not reach GitHub to check ({reason})"
    if code in (200, 206):
        return True, f"HTTP {code}"
    return False, f"HTTP {code}"


def require_published(urls: list[str], probe=None) -> list[str]:
    """Problems for every URL that does not resolve. Empty means all served.
    The probe is looked up at call time, so a test can replace it."""
    probe = probe or asset_published
    problems = []
    for url in urls:
        ok, reason = probe(url)
        if not ok:
            problems.append(f"{url}: not published ({reason})")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fix", action="store_true", help="Rewrite stale links in place.")
    ap.add_argument("--require-published", action="store_true",
                    help="Also check over the network that each release asset the "
                         "docs link to exists. Exit 1 if any does not.")
    args = ap.parse_args(argv)

    if args.fix:
        n = fix()
        print(f"{n} file(s) updated to v{version()}")

    problems = check()
    if problems:
        print("Download links are out of date:")
        for p in problems:
            print(f"  {p}")
        return 1

    if args.require_published:
        missing = require_published(urls_to_verify())
        if missing:
            print(f"Download links point at v{version()}, but the release does not serve them:")
            for p in missing:
                print(f"  {p}")
            print("Upload the assets (python scripts/build_release.py prints the "
                  "gh release upload lines), then run this again.")
            return 1
        print(f"Download links point at v{version()}, and GitHub serves every one. Published.")
        return 0

    print(f"Download links point at v{version()}. Current. (Not checked online - "
          "add --require-published after uploading the release.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
