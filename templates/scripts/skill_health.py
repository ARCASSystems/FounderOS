#!/usr/bin/env python3
"""Skill-health detectors for Founder OS housekeeping.

Two generic, deterministic checks over the shipped skill set. Read-only.

1. Description bloat: a SKILL.md frontmatter `description:` over 900 chars is a
   WARN (hard to route), over 1024 is a FAIL (some skill loaders truncate or
   silently skip long descriptions, so the skill looks installed but never
   fires).
2. Dead skill pointers: a `skills/<slug>/` path or `[[skills/<slug>]]` link in
   any shipped markdown whose skill directory does not exist. Dead pointers
   send the model (and the operator) to a skill that is not there.

Usage:
    python scripts/skill_health.py           # human-readable report
    python scripts/skill_health.py --json    # machine form
    python scripts/skill_health.py --root PATH   # fixture tests

Pure stdlib. ASCII output. Exit 0 always (housekeeping reads the findings; a
detector is a reporter, not a gate).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DESC_WARN = 900
DESC_FAIL = 1024

# Files whose skill references are historical by design, not live pointers.
SKIP_FILES = {"CHANGELOG.md"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "tests",
             "traces", "notes", "state", "archive", ".agents", "plans"}

POINTER_RE = re.compile(r"(?:\[\[)?skills/([a-z0-9][a-z0-9_-]*)/")


def frontmatter_description(text: str) -> str | None:
    """Extract the description scalar from SKILL.md frontmatter, if any."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm = text[3:end]
    m = re.search(r"^description:\s*(.*)$", fm, re.MULTILINE)
    if not m:
        return None
    first = m.group(1).strip()
    if first not in (">", ">-", "|", "|-"):
        return first
    # Block scalar: collect the indented lines that follow.
    lines = []
    after = fm[m.end():].splitlines()
    for line in after:
        if line.strip() == "":
            continue
        if line.startswith((" ", "\t")):
            lines.append(line.strip())
        else:
            break
    return " ".join(lines)


def check_descriptions(root: Path) -> list[dict]:
    findings = []
    for skill_md in sorted((root / "skills").glob("*/SKILL.md")):
        try:
            desc = frontmatter_description(skill_md.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            findings.append({"check": "desc-bloat", "skill": skill_md.parent.name,
                             "status": "UNKNOWN", "detail": f"unreadable: {exc}"})
            continue
        if desc is None:
            findings.append({"check": "desc-bloat", "skill": skill_md.parent.name,
                             "status": "FAIL", "detail": "no description in frontmatter"})
            continue
        n = len(desc)
        if n > DESC_FAIL:
            findings.append({"check": "desc-bloat", "skill": skill_md.parent.name,
                             "status": "FAIL", "detail": f"description {n} chars (> {DESC_FAIL}: loader may silently skip)"})
        elif n > DESC_WARN:
            findings.append({"check": "desc-bloat", "skill": skill_md.parent.name,
                             "status": "WARN", "detail": f"description {n} chars (> {DESC_WARN}: trim toward 600)"})
    return findings


def check_dead_pointers(root: Path) -> list[dict]:
    skill_dirs = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
    findings = []
    seen: set[tuple[str, str]] = set()
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root)
        if rel.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in POINTER_RE.finditer(text):
            slug = m.group(1)
            if slug in skill_dirs:
                continue
            key = (str(rel), slug)
            if key in seen:
                continue
            seen.add(key)
            findings.append({"check": "dead-pointer", "file": str(rel).replace("\\", "/"),
                             "status": "FAIL", "detail": f"references skills/{slug}/ which does not exist"})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Skill-health detectors (read-only)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--root", default=None, help="repo root override (fixture tests)")
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    if not (root / "skills").is_dir():
        msg = f"no skills/ directory under {root}"
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"skill-health: {msg}")
        return 0

    findings = check_descriptions(root) + check_dead_pointers(root)

    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, ensure_ascii=True))
        return 0

    if not findings:
        print("skill-health: OK (no description bloat, no dead skill pointers)")
        return 0

    print(f"skill-health: {len(findings)} finding(s)")
    for f in findings:
        where = f.get("skill") or f.get("file")
        print(f"  [{f['status']}] {f['check']} - {where} - {f['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
