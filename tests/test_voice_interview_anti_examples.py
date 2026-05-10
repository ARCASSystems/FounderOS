from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VOICE_SKILL = REPO_ROOT / "skills" / "voice-interview" / "SKILL.md"


class VoiceInterviewAntiExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = VOICE_SKILL.read_text(encoding="utf-8")

    def test_phase_25_exists(self) -> None:
        self.assertIn("## Phase 2.5 - Anti-examples", self.skill)

    def test_q9_to_q12_prompts_exist(self) -> None:
        expected_prompts = (
            "Name one belief you hold about your work that most people in your field would push back on. One sentence.",
            "What is one phrase, sentence structure, or formatting tic that makes you cringe when you see it in writing?",
            "When you read something and immediately suspect the writer is faking expertise, what was the tell? Name one specific pattern.",
            "Now pick 3-6 short pieces from the samples you pasted earlier.",
        )
        for prompt in expected_prompts:
            with self.subTest(prompt=prompt):
                self.assertIn(prompt, self.skill)

    def test_q12_worked_example_exists(self) -> None:
        for line in (
            'Bad: "It\'s not just about hiring fast - it\'s about hiring right."',
            'Good: "Most of the bad hires came from agreeing too quickly."',
            'Rule: "Cut negation-contrast openings. Lead with the specific incident."',
        ):
            with self.subTest(line=line):
                self.assertIn(line, self.skill)

    def test_anti_example_storage_rules_are_documented(self) -> None:
        for field in (
            "anti_examples.pairs",
            "anti_examples.contrarian_takes",
            "anti_examples.aesthetic_crimes",
            "anti_examples.red_flags",
            "The BAD line must be plausible",
            "Do not write the pair until they approve it",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.skill)


if __name__ == "__main__":
    unittest.main()
