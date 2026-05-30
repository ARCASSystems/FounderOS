#!/usr/bin/env python3
"""Version-parity guard: the release version must be identical across every manifest and the README
status line.

The VERSION file is the source of truth. fc38feb was a hotfix because the manifest version had
silently drifted to 1.32.0 while the content shipped 1.33.0 - check_doc_parity.py checks counts, not
the version field, so the drift sailed through CI. This guard locks the version field so that class
of drift fails the build instead.

Scope, on purpose: VERSION, .claude-plugin/plugin.json, .claude-plugin/marketplace.json (both
metadata.version and plugins[0].version), and the README status line. NOT the playbook sidebar
version - that is a rendered marketing artifact, and guarding it would force a playbook re-render on
every patch.

Takes an optional repo-root argument so the skew test can point it at a scratch copy without touching
the real tree. Exit 0 when every version agrees with VERSION, 1 with a report otherwise. Pure stdlib.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

# Anchors on the README Status-section line, e.g. "Version 1.33.0. Public release. ...", not the
# unrelated "Git - version 2.x" prerequisite line.
README_VERSION_RE = re.compile(r"^Version\s+(\d+\.\d+\.\d+)\.\s", re.MULTILINE)


def collect(root: Path) -> tuple[str | None, list[tuple[str, str | None]]]:
    """Return (canonical version from VERSION, [(label, found version or None), ...])."""

    def read(rel: str) -> str | None:
        p = root / rel
        return p.read_text(encoding="utf-8") if p.exists() else None

    version_text = read("VERSION")
    canonical = version_text.strip() if version_text is not None else None

    found: list[tuple[str, str | None]] = []

    plugin_text = read(".claude-plugin/plugin.json")
    if plugin_text is None:
        found.append((".claude-plugin/plugin.json version", None))
    else:
        try:
            found.append((".claude-plugin/plugin.json version", json.loads(plugin_text).get("version")))
        except json.JSONDecodeError:
            found.append((".claude-plugin/plugin.json version", None))

    mkt_text = read(".claude-plugin/marketplace.json")
    if mkt_text is None:
        found.append((".claude-plugin/marketplace.json metadata.version", None))
        found.append((".claude-plugin/marketplace.json plugins[0].version", None))
    else:
        try:
            mkt = json.loads(mkt_text)
            found.append(
                (".claude-plugin/marketplace.json metadata.version", (mkt.get("metadata") or {}).get("version"))
            )
            plugins = mkt.get("plugins") or []
            found.append(
                (".claude-plugin/marketplace.json plugins[0].version", plugins[0].get("version") if plugins else None)
            )
        except json.JSONDecodeError:
            found.append((".claude-plugin/marketplace.json metadata.version", None))
            found.append((".claude-plugin/marketplace.json plugins[0].version", None))

    readme_text = read("README.md")
    if readme_text is None:
        found.append(("README.md status-line version", None))
    else:
        m = README_VERSION_RE.search(readme_text)
        found.append(("README.md status-line version", m.group(1) if m else None))

    return canonical, found


def compare(canonical: str | None, found: list[tuple[str, str | None]]) -> list[str]:
    """Every collected version must equal the canonical VERSION. A missing anchor is a hard failure
    here (unlike the doc-parity count guard): a version field that has vanished is itself drift."""
    if not canonical:
        return ["VERSION file missing or empty - cannot establish the canonical release version"]
    failures: list[str] = []
    for label, value in found:
        if value is None:
            failures.append(f"{label}: not found (expected {canonical})")
        elif value != canonical:
            failures.append(f"{label}: states {value}, VERSION says {canonical}")
    return failures


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO
    canonical, found = collect(root)
    failures = compare(canonical, found)
    print(f"Canonical version (VERSION): {canonical}")
    if failures:
        print("\nVERSION PARITY FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Version parity OK: VERSION, both manifests, and the README status line all agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
