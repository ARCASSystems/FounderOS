"""
Tests for the <private> exclusion tag spec and writing-skill gates.

Discovery-based design (F25): instead of hard-coding a list of write surfaces,
the test DISCOVERS every .claude/commands/*.md and skills/*/SKILL.md that
contains a write verb followed by a brain/ or context/ path. Each discovered
surface must either:
  a) Reference the private-tag filter (contain `<private>` in the body), OR
  b) Carry an explicit exemption marker:
       <!-- private-tag: not applicable: <reason> -->

This means adding a new write surface without the filter automatically fails
the test. No one has to remember to update a hard-coded list.

Allowlist approach for structured/computed writes: add the exemption marker
to any surface that writes structured data rather than user-provided speech.
"""

import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATING_RULES = REPO_ROOT / "rules" / "operating-rules.md"

WRITE_PATTERN = re.compile(
    r"(?i)(append|write\s+to|writes\s+to|update|add\s+a\s+line|insert"
    r"|appends\s+to|writes\s+a|scan\s+the\s+source\s+text)\s"
    r".{0,80}?\b(brain/|context/|MEMORY\.md|stack\.json)",
    re.MULTILINE,
)

PRIVATE_MARKER = re.compile(r"<private>", re.IGNORECASE)
EXEMPTION_MARKER = "private-tag: not applicable"


def _discover_write_surfaces() -> list[Path]:
    """Return every command/skill file that writes to a tracked path."""
    candidates = list(
        (REPO_ROOT / ".claude" / "commands").glob("*.md")
    ) + list((REPO_ROOT / "skills").glob("*/SKILL.md"))
    surfaces = []
    for path in sorted(candidates):
        text = path.read_text(encoding="utf-8")
        if WRITE_PATTERN.search(text):
            surfaces.append(path)
    return surfaces


class PrivateTagSpecTests(unittest.TestCase):

    def setUp(self):
        self.body = OPERATING_RULES.read_text(encoding="utf-8")

    def test_operating_rules_documents_tag(self):
        self.assertIn("`<private>` exclusion tag", self.body)

    def test_tag_is_case_insensitive_per_spec(self):
        self.assertIn("case-insensitive", self.body)

    def test_tag_applies_to_named_skills(self):
        for name in ("brain-log", "dream", "knowledge-capture", "rant"):
            with self.subTest(skill=name):
                self.assertIn(
                    name,
                    self.body,
                    f"operating-rules.md must name {name} as a covered surface",
                )


class PrivateTagDiscoveryTests(unittest.TestCase):
    """Every discovered write surface must have the filter or an exemption."""

    @classmethod
    def setUpClass(cls):
        cls.surfaces = _discover_write_surfaces()

    def test_at_least_seven_write_surfaces_discovered(self):
        """Sanity check: discovery must find a reasonable number of surfaces."""
        self.assertGreaterEqual(
            len(self.surfaces),
            7,
            "Too few write surfaces discovered - pattern may be too narrow",
        )

    def test_every_write_surface_has_filter_or_exemption(self):
        """Every write surface must reference <private> filter or carry an exemption."""
        failures = []
        for path in self.surfaces:
            body = path.read_text(encoding="utf-8")
            has_filter = bool(PRIVATE_MARKER.search(body))
            has_exemption = EXEMPTION_MARKER in body
            if not has_filter and not has_exemption:
                failures.append(str(path.relative_to(REPO_ROOT)))
        if failures:
            self.fail(
                "These write surfaces lack the private-tag filter AND an exemption marker.\n"
                "Add the filter phrase or '<!-- private-tag: not applicable: <reason> -->':\n"
                + "\n".join(f"  {f}" for f in failures)
            )

    def test_capture_meeting_has_private_filter(self):
        path = REPO_ROOT / ".claude" / "commands" / "capture-meeting.md"
        self.assertIn("<private>", path.read_text(encoding="utf-8"))

    def test_pre_meeting_has_private_filter(self):
        path = REPO_ROOT / ".claude" / "commands" / "pre-meeting.md"
        self.assertIn("<private>", path.read_text(encoding="utf-8"))

    def test_setup_skill_auto_memory_has_private_filter(self):
        path = REPO_ROOT / "skills" / "founder-os-setup" / "SKILL.md"
        self.assertIn("<private>", path.read_text(encoding="utf-8"))

    def test_brain_log_skill_has_private_filter(self):
        path = REPO_ROOT / "skills" / "brain-log" / "SKILL.md"
        self.assertIn("<private>", path.read_text(encoding="utf-8"))

    def test_dream_command_has_private_filter(self):
        path = REPO_ROOT / ".claude" / "commands" / "dream.md"
        self.assertIn("<private>", path.read_text(encoding="utf-8"))

    def test_knowledge_capture_skill_has_private_filter(self):
        path = REPO_ROOT / "skills" / "knowledge-capture" / "SKILL.md"
        self.assertIn("<private>", path.read_text(encoding="utf-8"))

    def test_rant_command_has_private_filter(self):
        path = REPO_ROOT / ".claude" / "commands" / "rant.md"
        self.assertIn("<private>", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
