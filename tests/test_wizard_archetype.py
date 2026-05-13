"""
W5 - Setup wizard archetype and role-detection tests.
Verifies that the setup wizard skill documents the role question with three
options, branches at least three downstream questions by role, the bootloader
template uses {{role_noun}} substitution, and v1.21-W4 DEFER gaps M1 and M2
are addressed.
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIZARD_SKILL = REPO_ROOT / "skills" / "founder-os-setup" / "SKILL.md"
BOOTLOADER_TEMPLATE = REPO_ROOT / "templates" / "bootloader-claude-md.md"
MENU_PY = REPO_ROOT / "scripts" / "menu.py"


class WizardRoleDetectionTests(unittest.TestCase):

    def test_wizard_asks_role_question(self):
        """Wizard skill body must include a role-detection question."""
        body = WIZARD_SKILL.read_text(encoding="utf-8")
        # The role question must contain recognisable role-question language.
        self.assertRegex(
            body,
            r"(?i)(what best describes your role|your role)",
            "Wizard does not contain a role-detection question",
        )

    def test_wizard_documents_three_role_options(self):
        """Wizard must present all three role options: founder, operator, team-of-one."""
        body = WIZARD_SKILL.read_text(encoding="utf-8")
        for option in ("Founder", "Operator", "Team-of-one"):
            self.assertIn(
                option,
                body,
                f"Wizard role question is missing the '{option}' option",
            )


class WizardRoleBranchingTests(unittest.TestCase):

    def test_buyer_questions_phrase_by_role(self):
        """Wizard must show operator-specific phrasing for the 'who do you sell to' question."""
        body = WIZARD_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "Who does your company sell to",
            body,
            "Wizard missing operator variant for 'who do you sell to' question",
        )

    def test_pain_questions_phrase_by_role(self):
        """Wizard must show operator-specific phrasing for the buyer-pain question."""
        body = WIZARD_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "your company's typical buyer",
            body,
            "Wizard missing operator variant for buyer-pain question",
        )

    def test_m1_crm_question_includes_subscriber_option(self):
        """M1 fix: tool-stack CRM question must offer a subscriber/audience option."""
        body = WIZARD_SKILL.read_text(encoding="utf-8")
        # The subscriber list option must be present in the CRM question context.
        self.assertRegex(
            body,
            r"(?i)subscriber\s+list",
            "Wizard CRM question missing subscriber list option (M1 gap not addressed)",
        )

    def test_m2_primary_channel_question_present(self):
        """M2 fix: wizard must ask about primary marketing channel and map to primary_channel."""
        body = WIZARD_SKILL.read_text(encoding="utf-8")
        self.assertRegex(
            body,
            r"(?i)(main channel|primary channel)",
            "Wizard missing primary marketing channel question (M2 gap not addressed)",
        )
        self.assertIn(
            "primary_channel",
            body,
            "Wizard does not map primary channel answer to primary_channel field (M2 gap not addressed)",
        )


class BootloaderTemplateTests(unittest.TestCase):

    def test_template_uses_role_placeholder(self):
        """Bootloader template must contain {{role_noun}} placeholder."""
        body = BOOTLOADER_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(
            "{{role_noun}}",
            body,
            "Bootloader template is missing the {{role_noun}} placeholder",
        )

    def test_template_no_hardcoded_founder_in_role_context(self):
        """Bootloader template must not have 'founder' in role-context sentences (beyond product name)."""
        body = BOOTLOADER_TEMPLATE.read_text(encoding="utf-8")
        # Known role-context phrases that must NOT appear as literal "founder" any more.
        forbidden_phrases = [
            "for a founder who runs alone",
            "Every interaction is founder-initiated",
        ]
        for phrase in forbidden_phrases:
            self.assertNotIn(
                phrase,
                body,
                f"Bootloader template still has hardcoded founder role context: '{phrase}'",
            )

    def test_menu_py_reads_primary_channel(self):
        """menu.py must contain a function that reads primary_channel from stack.json."""
        body = MENU_PY.read_text(encoding="utf-8")
        self.assertIn(
            "primary_channel",
            body,
            "scripts/menu.py does not handle primary_channel (M2 fix not applied to menu engine)",
        )
        self.assertIn(
            "stack.json",
            body,
            "scripts/menu.py does not read from stack.json for primary_channel",
        )


if __name__ == "__main__":
    unittest.main()
