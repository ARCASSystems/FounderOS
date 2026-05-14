from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WRITING_SKILLS = {
    "linkedin-post": REPO_ROOT / "skills" / "linkedin-post" / "SKILL.md",
    "client-update": REPO_ROOT / "skills" / "client-update" / "SKILL.md",
    "proposal-writer": REPO_ROOT / "skills" / "proposal-writer" / "SKILL.md",
    "email-drafter": REPO_ROOT / "skills" / "email-drafter" / "SKILL.md",
    "content-repurposer": REPO_ROOT / "skills" / "content-repurposer" / "SKILL.md",
}

GATE_MESSAGE = (
    'Your voice profile is empty. Say "set up my voice profile" to run the '
    "interview first, or this output will sound like Claude defaults rather "
    "than you. Want me to start the interview now, or proceed with defaults "
    "anyway?"
)


class WritingSkillVoiceGateTests(unittest.TestCase):
    def test_each_writing_skill_stops_on_empty_voice_profile(self) -> None:
        for name, path in WRITING_SKILLS.items():
            with self.subTest(skill=name):
                body = path.read_text(encoding="utf-8")
                self.assertIn("Before producing output", body)
                self.assertIn("core/voice-profile.yml", body)
                self.assertIn("STOP", body)
                self.assertIn(GATE_MESSAGE, body)

    def test_each_gate_detects_template_defaults(self) -> None:
        markers = ("{{", "<your tone here>", "[CHOOSE", "[example:", "[NOT SET]")
        for name, path in WRITING_SKILLS.items():
            with self.subTest(skill=name):
                body = path.read_text(encoding="utf-8")
                for marker in markers:
                    self.assertIn(marker, body)


class WritingSkillAntiExampleFilterTests(unittest.TestCase):
    def test_each_writing_skill_documents_anti_example_filter(self) -> None:
        required_phrases = (
            "After producing a draft and before returning it, run the anti-examples filter",
            "anti_examples.pairs",
            "core/voice-profile.yml",
            "scan for matches against any `bad:` pattern",
            "rewrite it using the `good:` pattern",
            "the `rule:` line as the constraint",
            "aesthetic_crimes",
            "red_flags",
            "Return the cleaned draft",
            "Do not surface this filter to the user as a separate step",
        )
        for name, path in WRITING_SKILLS.items():
            with self.subTest(skill=name):
                body = path.read_text(encoding="utf-8")
                for phrase in required_phrases:
                    self.assertIn(phrase, body)

    def test_each_filter_names_structural_markers(self) -> None:
        markers = (
            "literal substrings",
            "negation-contrast",
            "rule-of-three",
        )
        for name, path in WRITING_SKILLS.items():
            with self.subTest(skill=name):
                body = path.read_text(encoding="utf-8")
                for marker in markers:
                    self.assertIn(marker, body)


SNAPSHOT_SKILLS = [
    "email-drafter",
    "sop-writer",
    "content-repurposer",
    "client-update",
    "proposal-writer",
]


class WritingSkillSnapshotReadTests(unittest.TestCase):
    def test_each_skill_references_snapshot(self):
        for skill in SNAPSHOT_SKILLS:
            path = REPO_ROOT / "skills" / skill / "SKILL.md"
            body = path.read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertIn("brain/.snapshot.md", body)
                self.assertIn("open-flags", body.lower())
                self.assertIn("must-do", body.lower())

    def test_each_skill_treats_snapshot_as_optional(self):
        for skill in SNAPSHOT_SKILLS:
            path = REPO_ROOT / "skills" / skill / "SKILL.md"
            body = path.read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertTrue(
                    "optional" in body.lower() or "if it exists" in body.lower(),
                    f"{skill}: snapshot must be optional, not required"
                )


if __name__ == "__main__":
    unittest.main()
