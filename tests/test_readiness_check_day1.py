from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
READINESS_SKILL = REPO_ROOT / "skills" / "readiness-check" / "SKILL.md"


class ReadinessCheckDay1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.body = READINESS_SKILL.read_text(encoding="utf-8")

    def test_early_exit_block_has_day1_framing(self) -> None:
        self.assertIn("Day 1", self.body)
        self.assertIn("Founder OS not set up here", self.body)
        self.assertIn("/founder-os:setup", self.body)
        self.assertIn("/founder-os:identity-interview", self.body)
        self.assertIn("/founder-os:voice-interview", self.body)

    def test_early_exit_block_points_back_to_status(self) -> None:
        self.assertIn("/founder-os:status after each step", self.body)

    def test_sub_twenty_score_rule_present(self) -> None:
        self.assertIn("total score is under 20", self.body)
        self.assertIn("NEXT 3 MOVES", self.body)
        self.assertIn("STATUS: Day 1", self.body)

    def test_day1_next_3_moves_lists_three_commands_verbatim(self) -> None:
        self.assertIn("Run /founder-os:identity-interview to capture who you are", self.body)
        self.assertIn("Run /founder-os:voice-interview to capture how you write", self.body)
        self.assertIn("Set 1-3 priorities in `context/priorities.md`", self.body)


if __name__ == "__main__":
    unittest.main()
