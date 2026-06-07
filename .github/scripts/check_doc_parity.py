#!/usr/bin/env python3
"""Doc-parity guard: skill and command counts must agree across the shipped surfaces.

Ground truth is the filesystem:
  skills   = number of skills/*/SKILL.md
  commands = number of .claude/commands/*.md

Every canonical count statement on a tracked doc surface must match that truth. Run
in CI on every push and PR so a stale number cannot ship again - this is what let
"52 skills" linger in the README and CLAUDE.md after the set had grown to 58.

What this guard does NOT check, on purpose:
  - The test count. tests/ is gitignored and absent from a CI checkout, so counting
    it here is impossible; the maintainer-local test_readme_invariants.py owns it.
  - CHANGELOG.md and "recent versions" prose. Those state historical counts for past
    releases and must not be rewritten, so we only check current-state statements.

Exit 0 when every checked statement agrees, 1 with a report otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def disk_counts() -> tuple[int, int]:
    skills = len(list((REPO / "skills").glob("*/SKILL.md")))
    commands = len(list((REPO / ".claude" / "commands").glob("*.md")))
    return skills, commands


# Each check: (relative path, regex with one numeric group, "skills"|"commands", label).
# The regex anchors on a CANONICAL count statement, not loose prose, so historical or
# example numbers elsewhere in the file are never matched. Every listed anchor is
# canonical: a missing file or missing anchor is a hard failure so wording changes
# cannot silently disable the gate.
CHECKS = [
    ("README.md", r"###\s+Skills\s*\((\d+)\)", "skills", "README '### Skills (N)'"),
    ("README.md", r"###\s+Slash commands\s*\((\d+)\)", "commands", "README '### Slash commands (N)'"),
    ("README.md", r"(\d+)\s+skills,\s*\d+\s+commands,\s*\d+\s+tests", "skills", "README status line skills"),
    ("README.md", r"\d+\s+skills,\s*(\d+)\s+commands,\s*\d+\s+tests", "commands", "README status line commands"),
    ("CLAUDE.md", r"##\s+Skills\s*\((\d+)\s+total", "skills", "CLAUDE.md '## Skills (N total'"),
    ("CLAUDE.md", r"all\s+\d+\s+skills\s+and\s+(\d+)\s+commands", "commands", "CLAUDE.md registry command count"),
    ("AGENTS.md", r"`skills/index\.md`\s*\((\d+)\s+skills,\s*\d+\s+commands\)", "skills", "AGENTS.md registry skill count"),
    ("AGENTS.md", r"`skills/index\.md`\s*\(\d+\s+skills,\s*(\d+)\s+commands\)", "commands", "AGENTS.md registry command count"),
    ("AGENTS.md", r"The\s+(\d+)\s+commands\s+in\s+`\.claude/commands/`", "commands", "AGENTS.md slash command count"),
    ("skills/index.md", r"(\d+)\s+skills\s+as of", "skills", "skills/index.md 'N skills as of'"),
    ("skills/index.md", r"This plugin ships\s+(\d+)\s+slash commands", "commands", "skills/index.md current command count"),
    ("llms.txt", r"Skills catalog\s+\((\d+)\)", "skills", "llms.txt skills catalog count"),
    ("llms.txt", r"Slash commands\s+\((\d+)\)", "commands", "llms.txt slash command count"),
    (".claude-plugin/plugin.json", r"(\d+)\s+skills,\s*\d+\s+commands", "skills", "plugin.json description skills"),
    (".claude-plugin/plugin.json", r"\d+\s+skills,\s*(\d+)\s+commands", "commands", "plugin.json description commands"),
    (".claude-plugin/marketplace.json", r"(\d+)\s+skills,\s*\d+\s+commands", "skills", "marketplace.json description skills"),
    (".claude-plugin/marketplace.json", r"\d+\s+skills,\s*(\d+)\s+commands", "commands", "marketplace.json description commands"),
]


def main() -> int:
    skills, commands = disk_counts()
    expected = {"skills": skills, "commands": commands}
    failures: list[str] = []
    notes: list[str] = []

    for rel, pattern, kind, label in CHECKS:
        path = REPO / rel
        if not path.exists():
            failures.append(f"{label}: required file {rel} not found")
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(pattern, text)
        if m is None:
            failures.append(f"{label}: required anchor not found in {rel}")
            continue
        found = int(m.group(1))
        if found != expected[kind]:
            failures.append(f"{label}: states {found} {kind}, disk has {expected[kind]}")

    # docs/skills.md and docs/commands.md: the rendered entry count must match disk.
    skills_doc = REPO / "docs" / "skills.md"
    if skills_doc.exists():
        entries = len(re.findall(r"(?m)^###\s+\S", skills_doc.read_text(encoding="utf-8")))
        if entries and entries != skills:
            failures.append(f"docs/skills.md lists {entries} '### ' entries, disk has {skills} skills")
        elif not entries:
            notes.append("docs/skills.md: no '### ' entries matched (skipped - check structure)")

    commands_doc = REPO / "docs" / "commands.md"
    if commands_doc.exists():
        entries = len(re.findall(r"(?m)^###\s+\S", commands_doc.read_text(encoding="utf-8")))
        if entries and entries != commands:
            failures.append(f"docs/commands.md lists {entries} '### ' entries, disk has {commands} commands")
        elif not entries:
            notes.append("docs/commands.md: no '### ' entries matched (skipped - check structure)")

    print(f"Disk truth: {skills} skills, {commands} commands")
    for n in notes:
        print(f"  note: {n}")
    if failures:
        print("\nDOC PARITY FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Doc parity OK: every canonical count statement matches disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
