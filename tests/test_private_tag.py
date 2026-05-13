"""
Tests for W4 - <private> exclusion tag spec and writing-skill gates.
All tests are static-content checks: reads actual files, no mocking.
No external dependencies.
"""

import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATING_RULES = REPO_ROOT / "rules" / "operating-rules.md"

# The four writing surfaces that must document the private-tag filter.
# brain-log and knowledge-capture are skills; dream and rant are commands.
WRITING_SURFACES = {
    "brain-log":        REPO_ROOT / "skills" / "brain-log" / "SKILL.md",
    "dream":            REPO_ROOT / ".claude" / "commands" / "dream.md",
    "knowledge-capture": REPO_ROOT / "skills" / "knowledge-capture" / "SKILL.md",
    "rant":             REPO_ROOT / ".claude" / "commands" / "rant.md",
}

PRIVATE_TAG_FILTER_PHRASE = (
    "scan the source text for `<private>...</private>` blocks"
)


class PrivateTagSpecTests(unittest.TestCase):

    def setUp(self):
        self.body = OPERATING_RULES.read_text(encoding="utf-8")

    def test_operating_rules_documents_tag(self):
        self.assertIn("`<private>` exclusion tag", self.body)

    def test_tag_is_case_insensitive_per_spec(self):
        self.assertIn("case-insensitive", self.body)

    def test_tag_applies_to_named_skills(self):
        # The spec must name at least the four writing surfaces.
        for name in ("brain-log", "dream", "knowledge-capture", "rant"):
            with self.subTest(skill=name):
                self.assertIn(name, self.body,
                              f"operating-rules.md must name {name} as a covered surface")


class PrivateTagSkillGateTests(unittest.TestCase):

    def test_each_writing_skill_documents_private_tag_filter(self):
        for name, path in WRITING_SURFACES.items():
            with self.subTest(surface=name):
                body = path.read_text(encoding="utf-8")
                self.assertIn(
                    PRIVATE_TAG_FILTER_PHRASE,
                    body,
                    f"{name}: must document the private-tag scan phrase",
                )

    def test_each_filter_documents_skip_case(self):
        """Each surface must document what happens when entire input is private."""
        for name, path in WRITING_SURFACES.items():
            with self.subTest(surface=name):
                body = path.read_text(encoding="utf-8")
                self.assertIn(
                    "entire input is wrapped in `<private>`",
                    body,
                    f"{name}: must document the all-private skip case",
                )

    def test_each_filter_names_removal_of_tags(self):
        """Each surface must document that the tags themselves are removed."""
        for name, path in WRITING_SURFACES.items():
            with self.subTest(surface=name):
                body = path.read_text(encoding="utf-8")
                self.assertIn(
                    "Remove every matched block (including the tags)",
                    body,
                    f"{name}: must document that tag markup is stripped",
                )


if __name__ == "__main__":
    unittest.main()
