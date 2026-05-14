"""Tests for skills/founder-os-setup/SKILL.md MC wizard structure.

The setup wizard is a Markdown skill spec for Claude to run, not a Python
helper. v1.20.0 rewrote the long-form open-ended Phase 0.5 (Tool Stack) and
Phase 0.7 (How You Work) into 4+4 sequential multi-choice prompts. The plan
required tests for the new MC behaviour but none were written. These tests
fill that gap by parsing the SKILL.md and asserting structural properties:

- Four sequential MC prompts in each phase
- Each prompt offers a "skip" path
- "skip" records null and continues
- A backward-compatibility clause for the parse-everything-at-once dump
- Allowed-values map preserved verbatim against stack.json tokens
- Schema fields written downstream (Decision style:, Communication style:)
- No banned prose phrases, no em or en dashes

If the wizard's MC structure is wrong, these tests fail loud rather than
silently passing on file existence.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP_SKILL = REPO_ROOT / "skills" / "founder-os-setup" / "SKILL.md"
STACK_JSON = REPO_ROOT / "stack.json"


def _extract_section(body: str, start_header: str, next_header_pattern: str) -> str:
    """Return the body text between a start header and the next matching header.

    Both headers must already be present. Used to scope assertions to a
    single phase so a token in another phase cannot accidentally satisfy a
    check.
    """
    start_idx = body.index(start_header)
    after_start = body[start_idx + len(start_header):]
    next_match = re.search(next_header_pattern, after_start)
    if next_match is None:
        return after_start
    return after_start[: next_match.start()]


class SetupWizardToolStackPhaseTests(unittest.TestCase):
    """Phase 0.5 (Tool Stack) MC structure assertions."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.body = SETUP_SKILL.read_text(encoding="utf-8")
        cls.section = _extract_section(
            cls.body,
            "### 0.5 Tool Stack",
            r"\n### 0\.6 ",
        )

    def test_phase_header_present(self) -> None:
        self.assertIn("### 0.5 Tool Stack", self.body)

    def test_four_sequential_mc_prompts_present(self) -> None:
        # Each MC prompt is rendered as a numbered question. Phase 0.5 has
        # exactly four covering knowledge base, email, calendar, CRM.
        for prompt_marker in ("1.", "2.", "3.", "4."):
            with self.subTest(marker=prompt_marker):
                self.assertIn(prompt_marker, self.section)

    def test_knowledge_base_prompt_with_options(self) -> None:
        # Knowledge base prompt must list its options on one line.
        self.assertIn("Where do you store written knowledge?", self.section)
        for option in ("Notion", "Obsidian", "Google Drive", "local files only", "other", "skip"):
            with self.subTest(option=option):
                self.assertIn(option, self.section)

    def test_email_prompt_with_options(self) -> None:
        self.assertIn("What email do you use for work?", self.section)
        for option in ("Gmail", "Outlook", "Apple Mail", "other", "none", "skip"):
            with self.subTest(option=option):
                self.assertIn(option, self.section)

    def test_calendar_prompt_with_options(self) -> None:
        self.assertIn("What calendar do you use?", self.section)
        for option in ("Google Calendar", "Outlook", "Apple Calendar", "other", "none", "skip"):
            with self.subTest(option=option):
                self.assertIn(option, self.section)

    def test_crm_prompt_with_options(self) -> None:
        # v1.22 W5/M1: prompt broadened to cover B2C subscriber-list users.
        self.assertIn("Where do you track customers, subscribers, or your pipeline?", self.section)
        for option in ("Notion DB", "HubSpot", "Airtable", "subscriber list", "spreadsheet", "nothing yet", "skip"):
            with self.subTest(option=option):
                self.assertIn(option, self.section)

    def test_skip_path_offered_in_every_prompt(self) -> None:
        # Each numbered prompt line must offer "skip" as a terminal option.
        # v1.22 W5/M2: Q5 (primary channel) added, so there are now 5 prompts.
        prompt_lines = re.findall(
            r"^\d\. \"[^\"]+\"",
            self.section,
            re.MULTILINE,
        )
        self.assertEqual(
            len(prompt_lines),
            5,
            f"Expected exactly 5 numbered MC prompts, found {len(prompt_lines)}",
        )
        for line in prompt_lines:
            with self.subTest(line=line):
                self.assertTrue(
                    line.rstrip(".\"").endswith("skip"),
                    f"Prompt does not end with 'skip' option: {line}",
                )

    def test_skip_records_null_and_continues(self) -> None:
        # The behaviour clause must explicitly state skip -> null + continue.
        self.assertIn("\"skip\" on any prompt records `null`", self.section)
        self.assertIn("continues", self.section)
        self.assertIn("No \"are you sure?\" follow-up", self.section)

    def test_parse_everything_at_once_clause(self) -> None:
        # Backward-compatibility path: founder dumps multiple tools in one
        # reply, wizard parses all and skips remaining prompts.
        self.assertIn("Backward compatibility", self.section)
        self.assertIn("parse-everything-at-once", self.section)
        self.assertIn("Notion, Gmail, Google Calendar, no CRM", self.section)
        self.assertIn("Do not re-ask", self.section)

    def test_allowed_values_tokens_preserved(self) -> None:
        # Tokens must match stack.json _allowed_values verbatim. Any drift
        # here breaks every skill that reads stack.json.
        for token in (
            "notion",
            "obsidian",
            "google_drive",
            "local",
            "gmail",
            "outlook",
            "apple_mail",
            "google_calendar",
            "outlook_calendar",
            "notion_db",
            "hubspot",
            "airtable",
            "none",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.section)

    def test_field_name_mapping_present(self) -> None:
        # Each MC prompt must map to its stack.json field name so the
        # downstream Phase 5.0 write step knows where to put the value.
        for field in ("knowledge_base", "email_platform", "calendar", "crm"):
            with self.subTest(field=field):
                self.assertIn(field, self.section)


class SetupWizardPositioningPhaseTests(unittest.TestCase):
    """Phase 0.2.5 positioning prompts feed downstream writing skills."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.body = SETUP_SKILL.read_text(encoding="utf-8")
        cls.section = _extract_section(
            cls.body,
            "### 0.2.5 Positioning",
            r"\n### 0\.3 ",
        )

    def test_phase_header_present(self) -> None:
        self.assertIn("### 0.2.5 Positioning", self.body)

    def test_three_positioning_prompts_present(self) -> None:
        expected = (
            "Who do you sell to in one sentence?",
            "What do you sell in one sentence?",
            "What visible pain does your buyer feel before they come to you?",
        )
        for prompt in expected:
            with self.subTest(prompt=prompt):
                self.assertIn(prompt, self.section)

    def test_skip_path_is_explicit(self) -> None:
        self.assertIn("skip-able", self.section)
        self.assertIn("write `[NOT SET]`", self.section)

    def test_parse_everything_at_once_clause_present(self) -> None:
        self.assertIn("parse-everything-at-once", self.section)
        self.assertIn("I sell to UAE SMEs", self.section)
        self.assertIn("Do not re-ask", self.section)

    def test_identity_schema_fields_present(self) -> None:
        phase_one = _extract_section(
            self.body,
            "### 1.1 Identity File",
            r"\n### 1\.2 ",
        )
        for field in ("**Sells to:**", "**Sells:**", "**Buyer pain:**"):
            with self.subTest(field=field):
                self.assertIn(field, phase_one)
        self.assertIn("## Positioning", phase_one)

    def test_downstream_consumers_named(self) -> None:
        for skill in (
            "linkedin-post",
            "proposal-writer",
            "client-update",
            "business-context-loader",
        ):
            with self.subTest(skill=skill):
                self.assertIn(skill, self.section)


class SetupWizardWorkStylePhaseTests(unittest.TestCase):
    """Phase 0.7 (How You Work) MC structure assertions."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.body = SETUP_SKILL.read_text(encoding="utf-8")
        cls.section = _extract_section(
            cls.body,
            "### 0.7 How You Work",
            r"\n### 0\.8 ",
        )

    def test_phase_header_present(self) -> None:
        self.assertIn("### 0.7 How You Work", self.body)

    def test_four_sequential_mc_prompts_present(self) -> None:
        prompt_lines = re.findall(
            r"^\d\. \"[^\"]+\"",
            self.section,
            re.MULTILINE,
        )
        self.assertEqual(
            len(prompt_lines),
            4,
            f"Expected exactly 4 numbered MC prompts in Phase 0.7, found {len(prompt_lines)}",
        )

    def test_deep_work_prompt_with_options(self) -> None:
        self.assertIn("When do you do your best deep work?", self.section)
        for option in ("Morning", "afternoon", "evening", "variable", "skip"):
            with self.subTest(option=option):
                self.assertIn(option, self.section)

    def test_decision_style_prompt_with_options(self) -> None:
        self.assertIn("How do you usually make decisions?", self.section)
        for option in ("Gut", "data", "dialogue", "mixed", "skip"):
            with self.subTest(option=option):
                self.assertIn(option, self.section)

    def test_communication_style_prompt_with_options(self) -> None:
        self.assertIn("How do you prefer Claude to communicate with you?", self.section)
        for option in ("Direct and short", "detailed and explanatory", "skip"):
            with self.subTest(option=option):
                self.assertIn(option, self.section)

    def test_overwhelm_prompt_with_options(self) -> None:
        self.assertIn("What overwhelms you most?", self.section)
        for option in (
            "Too many open loops",
            "unclear next step",
            "context switching",
            "decision fatigue",
            "other",
            "skip",
        ):
            with self.subTest(option=option):
                self.assertIn(option, self.section)

    def test_skip_records_null_and_continues(self) -> None:
        self.assertIn("\"skip\" on any prompt records `null`", self.section)
        self.assertIn("No \"are you sure?\" follow-up", self.section)

    def test_parse_everything_at_once_clause(self) -> None:
        self.assertIn("Backward compatibility", self.section)
        self.assertIn("parse-everything-at-once", self.section)
        self.assertIn("morning, gut, direct, too many open loops", self.section)

    def test_encoding_tokens_for_decision_style(self) -> None:
        # Each decision-style answer maps to a structured token consumed by
        # downstream skills. Drift here breaks rule-based skill behaviour.
        for token in ("`gut`", "`data`", "`dialogue`", "`mixed`"):
            with self.subTest(token=token):
                self.assertIn(token, self.section)

    def test_encoding_tokens_for_communication_style(self) -> None:
        for token in ("`direct`", "`detailed`"):
            with self.subTest(token=token):
                self.assertIn(token, self.section)

    def test_encoding_tokens_for_deep_work(self) -> None:
        for token in ("`morning`", "`afternoon`", "`evening`", "`variable`"):
            with self.subTest(token=token):
                self.assertIn(token, self.section)

    def test_encoding_tokens_for_overwhelm(self) -> None:
        for token in (
            "`open_loops`",
            "`unclear_next`",
            "`context_switching`",
            "`decision_fatigue`",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.section)

    def test_downstream_schema_field_names_referenced(self) -> None:
        # The encoding clause must name the exact schema fields downstream
        # files consume so identity.md and operating-rules.md keep working.
        self.assertIn("**Decision style:**", self.section)
        self.assertIn("**Communication style:**", self.section)
        self.assertIn("core/identity.md", self.section)
        self.assertIn("rules/operating-rules.md", self.section)


class StackJsonPrimaryChannelTests(unittest.TestCase):
    """stack.json must include primary_channel and its allowed values."""

    @classmethod
    def setUpClass(cls) -> None:
        with STACK_JSON.open(encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_stack_json_parses(self) -> None:
        self.assertIsInstance(self.data, dict)

    def test_primary_channel_field_present(self) -> None:
        self.assertIn(
            "primary_channel",
            self.data,
            "stack.json is missing the primary_channel field",
        )

    def test_primary_channel_in_allowed_values(self) -> None:
        allowed = self.data.get("_allowed_values", {})
        self.assertIn(
            "primary_channel",
            allowed,
            "stack.json _allowed_values is missing primary_channel",
        )

    def test_primary_channel_allowed_values_non_empty(self) -> None:
        allowed = self.data.get("_allowed_values", {}).get("primary_channel", [])
        self.assertGreater(
            len(allowed),
            0,
            "stack.json _allowed_values.primary_channel must be a non-empty list",
        )

    def test_primary_channel_allowed_values_includes_linkedin(self) -> None:
        allowed = self.data.get("_allowed_values", {}).get("primary_channel", [])
        self.assertIn("linkedin", allowed)

    def test_wizard_maps_primary_channel(self) -> None:
        body = SETUP_SKILL.read_text(encoding="utf-8")
        self.assertIn("primary_channel", body)


class SetupWizardProseHygieneTests(unittest.TestCase):
    """Cross-cutting prose checks on the full SKILL.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.body = SETUP_SKILL.read_text(encoding="utf-8")

    def test_no_em_or_en_dashes(self) -> None:
        self.assertNotIn(chr(0x2014), self.body, "Em dash found in setup wizard SKILL.md")
        self.assertNotIn(chr(0x2013), self.body, "En dash found in setup wizard SKILL.md")

    def test_no_banned_phrases_in_mc_blocks(self) -> None:
        # Regression check: the MC rewrite should not have introduced
        # corporate-speak. Scan only the two MC phase sections.
        tool_stack = _extract_section(
            self.body,
            "### 0.5 Tool Stack",
            r"\n### 0\.6 ",
        )
        work_style = _extract_section(
            self.body,
            "### 0.7 How You Work",
            r"\n### 0\.8 ",
        )
        scope = (tool_stack + "\n" + work_style).lower()
        banned = tuple(
            "".join(parts)
            for parts in (
                ("leve", "rage"),
                ("sea", "mless"),
                ("ro", "bust"),
                ("compre", "hensive"),
                ("hol", "istic"),
                ("trans", "formative"),
                ("stream", "line"),
                ("uti", "lize"),
                ("del", "ve"),
                ("eco", "system"),
                ("land", "scape"),
                ("un", "lock"),
                ("faci", "litate"),
            )
        )
        for word in banned:
            with self.subTest(word=word):
                self.assertNotRegex(
                    scope,
                    rf"\b{re.escape(word)}\b",
                    f"Banned phrase '{word}' present in MC prompt blocks",
                )


if __name__ == "__main__":
    unittest.main()
