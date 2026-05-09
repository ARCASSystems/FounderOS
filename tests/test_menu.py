"""Tests for skills/menu/SKILL.md.

The menu skill is implemented as a Markdown skill spec for Claude to run -
not a Python helper. There is no algorithmic Python module to invoke. So the
tests here are structural: they assert the SKILL.md file exists, has the
required sections that the v1.20 plan calls for, lists the canonical Day-1
starter set, and contains the closing line verbatim.

If a future revision of the menu skill ships a Python helper, replace these
structural tests with behavioural ones (zero-state input -> Day-1 output,
populated-state input -> top 5-7 output, missing snapshot -> graceful fallback).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MENU_SKILL = REPO_ROOT / "skills" / "menu" / "SKILL.md"


CLOSING_LINE = (
    "These are tailored to your current state. Say any of the natural-language "
    "phrases above. Or ask Claude anything in plain English - most of FounderOS "
    "routes by what you say, not what you type."
)


class MenuSkillStructureTests(unittest.TestCase):
    """Structural assertions for the markdown-driven menu skill."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.body = MENU_SKILL.read_text(encoding="utf-8")

    def test_skill_file_exists(self) -> None:
        self.assertTrue(
            MENU_SKILL.is_file(),
            f"Expected skill file at {MENU_SKILL}",
        )

    def test_frontmatter_has_natural_language_first(self) -> None:
        # Frontmatter description should lead with a natural-language phrasing.
        # The slash command appears parenthetically.
        match = re.search(
            r"^---\s*\n(.*?)\n---",
            self.body,
            re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(match, "frontmatter block not found")
        frontmatter = match.group(1)
        self.assertIn("name: menu", frontmatter)
        self.assertIn('Say "show me what you can do"', frontmatter)
        # Slash command must appear, but parenthetically (not as the lead).
        self.assertIn("/founder-os:menu", frontmatter)

    def test_algorithm_sections_present(self) -> None:
        # The five-step algorithm from the v1.20 plan must be documented.
        for required in (
            "## Algorithm",
            "Step 1 - Read current state",
            "Step 2 - Score capabilities",
            "Step 3 - Pick top 5 to 7",
            "Step 4 - Render rows",
            "Step 5 - Close",
        ):
            with self.subTest(section=required):
                self.assertIn(required, self.body)

    def test_state_inputs_documented(self) -> None:
        # Step 1 reads these specific files. Listed in the plan.
        for path in (
            "brain/.snapshot.md",
            "brain/flags.md",
            "cadence/weekly-commitments.md",
            "brain/log.md",
            "core/voice-profile.yml",
            "core/brand-profile.yml",
            "context/priorities.md",
        ):
            with self.subTest(path=path):
                self.assertIn(path, self.body)

    def test_capability_scoring_rules_present(self) -> None:
        # Each capability's surface_when rule must be documented.
        for capability in (
            "voice-interview",
            "brand-interview",
            "priority-triage",
            "weekly-review",
            "forcing-questions",
            "pre-send-check",
            "capture-meeting",
            "audit",
        ):
            with self.subTest(capability=capability):
                self.assertIn(capability, self.body)

    def test_zero_state_safety_section(self) -> None:
        self.assertIn("## Zero-state safety", self.body)
        # Day-1 starter set is non-negotiable per the plan.
        for capability in (
            "voice-interview",
            "brand-interview",
            "priority-triage",
            "ingest",
        ):
            with self.subTest(capability=capability):
                self.assertIn(capability, self.body)
        # /today is the always-bare command in the Day-1 set.
        self.assertIn("/today", self.body)
        # Empty list is forbidden.
        self.assertIn("Never return an empty list", self.body)

    def test_closing_line_present_verbatim(self) -> None:
        self.assertIn(
            CLOSING_LINE,
            self.body,
            "Menu output must end with the canonical closing line so that "
            "operators get the same hint about plain-English routing every "
            "time.",
        )

    def test_no_llm_call_constraint_documented(self) -> None:
        # The "no LLM call inside the algorithm" constraint guards the
        # free-tier accessibility floor and must be stated explicitly.
        self.assertIn("No LLM call", self.body)
        self.assertIn("Free-tier", self.body)

    def test_canonical_trigger_phrases_present(self) -> None:
        # Trigger phrases listed in founder-os-setup Phase 6.2 must appear
        # verbatim in the menu skill so the natural-language path keeps working.
        for phrase in (
            "set up my voice profile",
            "set up my brand profile",
            "what should I focus on next",
            "what's on for today?",
            "audit the OS",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.body)

    def test_no_banned_phrases(self) -> None:
        # Banned phrase list from the v1.20 plan-level constraints.
        banned = (
            "leverage",
            "seamless",
            "robust",
            "comprehensive",
            "holistic",
            "transformative",
            "streamline",
            "optimize",
            "utilize",
            "delve",
            "navigate",
            "ecosystem",
            "landscape",
            "unlock",
            "facilitate",
        )
        body_lower = self.body.lower()
        for word in banned:
            with self.subTest(word=word):
                # Word-boundary match so substrings inside other words
                # (e.g. "navigate" in "navigation") are also caught.
                self.assertNotRegex(
                    body_lower,
                    rf"\b{re.escape(word)}\b",
                    f"Banned phrase '{word}' present in menu skill prose",
                )

    def test_no_em_or_en_dashes(self) -> None:
        # Em dash (U+2014) and en dash (U+2013) are forbidden in v1.20 prose.
        self.assertNotIn("—", self.body, "Em dash found in menu skill")
        self.assertNotIn("–", self.body, "En dash found in menu skill")


if __name__ == "__main__":
    unittest.main()
