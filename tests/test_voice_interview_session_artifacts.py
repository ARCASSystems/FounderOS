from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VOICE_SKILL = REPO_ROOT / "skills" / "voice-interview" / "SKILL.md"


class VoiceInterviewSessionArtifactsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.body = VOICE_SKILL.read_text(encoding="utf-8")

    def test_hard_gate_allows_session_artifacts(self) -> None:
        self.assertIn("sourced from existing session artifacts", self.body)

    def test_pre_step_section_present(self) -> None:
        self.assertIn("Pre-step: Scan for existing artifacts", self.body)

    def test_pre_step_lists_scan_paths(self) -> None:
        paths = [
            "brain/rants/",
            "brain/log.md",
            "context/decisions.md",
            "clients/*/communications/",
        ]
        found = sum(1 for path in paths if path in self.body)
        self.assertGreaterEqual(found, 3, f"only {found} of 4 scan paths present")

    def test_requires_explicit_user_confirmation(self) -> None:
        self.assertIn("explicit yes", self.body)

    def test_falls_through_to_paste_flow_when_artifacts_thin(self) -> None:
        self.assertIn("fewer than 2 candidates exist", self.body)
        self.assertIn("paste flow", self.body)


if __name__ == "__main__":
    unittest.main()
