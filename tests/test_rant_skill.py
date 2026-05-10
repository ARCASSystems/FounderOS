from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
RANT_COMMAND = REPO_ROOT / ".claude" / "commands" / "rant.md"


class RantRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.body = RANT_COMMAND.read_text(encoding="utf-8")

    def test_one_qualifying_question_present(self) -> None:
        self.assertIn(
            "Does this need a decision, a draft, a plan, or just to be captured?",
            self.body,
        )
        self.assertIn("Ask exactly one qualifying question", self.body)
        self.assertIn("Do not run a multi-turn intake", self.body)

    def test_routes_to_specific_skills(self) -> None:
        for skill in (
            "decision-framework",
            "linkedin-post",
            "email-drafter",
            "proposal-writer",
            "client-update",
            "priority-triage",
            "forcing-questions",
            "brain-log",
        ):
            with self.subTest(skill=skill):
                self.assertIn(skill, self.body)

    def test_capture_path_preserves_existing_rants_file(self) -> None:
        self.assertIn("brain/rants/<YYYY-MM-DD>.md", self.body)
        self.assertIn("Captured. <N> rants today. /dream when ready.", self.body)
        self.assertIn("If the user says \"just capture\"", self.body)

    def test_old_no_follow_up_rule_removed(self) -> None:
        self.assertNotIn("Do not ask follow-up questions", self.body)
        self.assertIn("Ask only the one qualifying question", self.body)


if __name__ == "__main__":
    unittest.main()
