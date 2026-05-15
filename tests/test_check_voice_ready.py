"""Tests for scripts/check-voice-ready.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check-voice-ready.py"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), "--root", str(root)]
    return subprocess.run(cmd, text=True, capture_output=True)


def write_voice(root: Path, body: str) -> None:
    (root / "core").mkdir(parents=True, exist_ok=True)
    (root / "core" / "voice-profile.yml").write_text(body, encoding="utf-8")


class CheckVoiceReadyTests(unittest.TestCase):
    def test_missing_file_exits_1_and_mentions_setup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run(Path(tmp))
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing", result.stdout.lower())
            self.assertIn("setup", result.stdout.lower())

    def test_template_braces_exit_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            write_voice(
                tmp_root,
                "voice:\n"
                "  rhythm: \"short_hits\"\n"
                "  founder: {{FOUNDER_NAME}}\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("template", result.stdout.lower())

    def test_choose_markers_exit_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            write_voice(
                tmp_root,
                "voice:\n"
                "  rhythm: \"[CHOOSE: short_hits | long_builders]\"\n"
                "  contractions: \"sometimes\"\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("template", result.stdout.lower())

    def test_filled_profile_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            write_voice(
                tmp_root,
                "voice:\n"
                "  rhythm: \"short_hits\"\n"
                "  opening_style: \"punch\"\n"
                "  closing_style: \"weight\"\n"
                "  contractions: \"sometimes\"\n"
                "  reading_level: 8\n"
                "  preferred_words:\n"
                "    - \"ship\"\n"
                "    - \"fix\"\n"
                "  banned_words:\n"
                "    - \"synergy\"\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 0, msg=result.stdout)
            self.assertIn("ready", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
