from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VOICE_SKILL = REPO_ROOT / "skills" / "voice-interview" / "SKILL.md"
VOICE_TEMPLATE = REPO_ROOT / "templates" / "voice-profile.yml.template"


class VoiceInterviewBuyerLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = VOICE_SKILL.read_text(encoding="utf-8")
        cls.template = VOICE_TEMPLATE.read_text(encoding="utf-8")

    def test_buyer_language_questions_present(self) -> None:
        self.assertIn(
            "When your buyer describes their problem to you, what is the first sentence out of their mouth?",
            self.skill,
        )
        self.assertIn(
            "What is a phrase your buyer says that makes you nod every time?",
            self.skill,
        )

    def test_buyer_language_fields_are_saved(self) -> None:
        for field in (
            "buyer_language:",
            "first_sentence:",
            "phrases:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.skill)
                self.assertIn(field, self.template)

    def test_anti_example_fields_are_saved(self) -> None:
        for field in (
            "anti_examples:",
            "pairs:",
            "bad:",
            "good:",
            "rule:",
            "contrarian_takes:",
            "aesthetic_crimes:",
            "red_flags:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.skill)
                self.assertIn(field, self.template)

    def test_confirm_step_surfaces_buyer_language(self) -> None:
        self.assertIn("Buyer first sentence", self.skill)
        self.assertIn("Buyer phrases", self.skill)

    def test_confirm_step_surfaces_anti_examples(self) -> None:
        for label in (
            "Contrarian takes",
            "Aesthetic crimes",
            "Red flags",
            "Anti-example pairs",
        ):
            with self.subTest(label=label):
                self.assertIn(label, self.skill)

    def test_downstream_writers_named(self) -> None:
        for skill_name in (
            "linkedin-post",
            "email-drafter",
            "proposal-writer",
            "client-update",
        ):
            with self.subTest(skill=skill_name):
                self.assertIn(skill_name, self.skill)


if __name__ == "__main__":
    unittest.main()
