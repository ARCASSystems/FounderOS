"""Tests for scripts/brain-snapshot.py."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "brain-snapshot.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "snapshot-corpus"
FIXED_TODAY = "2026-05-08"


def run(*args: str, root: Path = FIXTURE) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), "--root", str(root), "--today", FIXED_TODAY, *args]
    return subprocess.run(cmd, text=True, capture_output=True)


class BrainSnapshotTests(unittest.TestCase):
    def test_happy_path_renders_all_sections(self) -> None:
        result = run()
        self.assertEqual(result.returncode, 0)
        out = result.stdout
        self.assertIn("# Brain snapshot", out)
        self.assertIn(f"date: {FIXED_TODAY}", out)
        self.assertIn("daily_anchor: fresh", out)
        self.assertIn("weekly: fresh", out)
        self.assertIn("weekly-must-do: fresh", out)
        self.assertIn("- rhythm: short_hits", out)
        self.assertIn("- opening_style: punch", out)
        self.assertIn("- closing_style: weight", out)
        self.assertIn("- contractions: sometimes", out)
        self.assertIn("- reading_level: 8", out)
        self.assertIn("- preferred: ship, fix, build", out)
        self.assertIn("- banned: synergy, paradigm", out)
        self.assertIn("- display_name: Acme Studio", out)
        self.assertIn("- primary_color: #0A66C2", out)
        self.assertIn("- primary_font: Inter", out)
        self.assertIn("- 2026-05-04 - Pipeline follow-up stalled", out)
        self.assertIn("- Ship v1.10 release", out)
        self.assertIn("- Pricing tier rename", out)

    def test_missing_voice_profile_marks_fields_unset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "founder-os"
            shutil.copytree(FIXTURE, tmp_root)
            (tmp_root / "core" / "voice-profile.yml").unlink()
            result = run(root=tmp_root)
            out = result.stdout
            self.assertEqual(result.returncode, 0)
            self.assertIn("- rhythm: [NOT SET]", out)
            self.assertIn("- preferred: [NOT SET]", out)
            self.assertIn("- banned: [NOT SET]", out)
            # Other sections still render.
            self.assertIn("- 2026-05-04 - Pipeline follow-up stalled", out)
            self.assertIn("- Ship v1.10 release", out)
            self.assertIn("- display_name: Acme Studio", out)

    def test_template_defaults_count_as_unset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "founder-os"
            shutil.copytree(FIXTURE, tmp_root)
            (tmp_root / "core" / "voice-profile.yml").write_text(
                "voice:\n"
                "  rhythm: \"[CHOOSE: short_hits | long_builders]\"\n"
                "  opening_style: \"[CHOOSE]\"\n"
                "  closing_style: \"[CHOOSE]\"\n"
                "  contractions: \"[CHOOSE]\"\n"
                "  reading_level: \"[CHOOSE]\"\n"
                "  preferred_words:\n"
                "    - \"[example: build]\"\n"
                "  banned_words:\n"
                "    - \"[example: synergy]\"\n",
                encoding="utf-8",
            )
            result = run(root=tmp_root)
            out = result.stdout
            self.assertEqual(result.returncode, 0)
            self.assertIn("- rhythm: [NOT SET]", out)
            self.assertIn("- opening_style: [NOT SET]", out)
            self.assertIn("- preferred: [NOT SET]", out)
            self.assertIn("- banned: [NOT SET]", out)

    def test_no_flags_file_marks_section_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "founder-os"
            shutil.copytree(FIXTURE, tmp_root)
            (tmp_root / "brain" / "flags.md").unlink()
            result = run(root=tmp_root)
            out = result.stdout
            self.assertEqual(result.returncode, 0)
            self.assertIn("## Open flags (top 3)", out)
            # The flags section must show [unavailable] but other sections must keep rendering.
            flags_block = out.split("## Open flags (top 3)", 1)[1].split("##", 1)[0]
            self.assertIn("[unavailable]", flags_block)
            self.assertIn("- Ship v1.10 release", out)

    def test_stale_cadence_emits_days_past(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "founder-os"
            shutil.copytree(FIXTURE, tmp_root)
            (tmp_root / "cadence" / "daily-anchors.md").write_text(
                "# Daily Anchors\n\n## Today: 2026-04-01\n\n**Anchor:** stale anchor.\n",
                encoding="utf-8",
            )
            (tmp_root / "cadence" / "weekly-commitments.md").write_text(
                "# Weekly Commitments\n\n## Week of 2026-03-01\n\n## Must Do (max 3)\n\n1. Old item\n",
                encoding="utf-8",
            )
            result = run(root=tmp_root)
            out = result.stdout
            self.assertEqual(result.returncode, 0)
            self.assertIn("daily_anchor: stale (37 days past)", out)
            self.assertIn("weekly: stale (68 days past)", out)
            self.assertIn("weekly-must-do: [unavailable - weekly file stale]", out)

    def test_top_three_flags_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "founder-os"
            shutil.copytree(FIXTURE, tmp_root)
            (tmp_root / "brain" / "flags.md").write_text(
                "# Flags\n\n"
                "## 2026-05-04 - Flag A\n\nStatus: **OPEN**\n\n---\n\n"
                "## 2026-05-03 - Flag B\n\nStatus: **OPEN**\n\n---\n\n"
                "## 2026-05-02 - Flag C\n\nStatus: **OPEN**\n\n---\n\n"
                "## 2026-05-01 - Flag D\n\nStatus: **OPEN**\n\n---\n\n"
                "## 2026-04-30 - Flag E\n\nStatus: **OPEN**\n\n---\n",
                encoding="utf-8",
            )
            result = run(root=tmp_root)
            out = result.stdout
            self.assertEqual(result.returncode, 0)
            self.assertIn("- 2026-05-04 - Flag A", out)
            self.assertIn("- 2026-05-03 - Flag B", out)
            self.assertIn("- 2026-05-02 - Flag C", out)
            self.assertNotIn("Flag D", out)
            self.assertNotIn("Flag E", out)

    def test_write_flag_creates_file_and_silences_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "founder-os"
            shutil.copytree(FIXTURE, tmp_root)
            target = tmp_root / "brain" / ".snapshot.md"
            self.assertFalse(target.exists())
            result = run("--write", root=tmp_root)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertTrue(target.exists())
            content = target.read_text(encoding="utf-8")
            self.assertIn("# Brain snapshot", content)
            self.assertIn(f"date: {FIXED_TODAY}", content)
            # Without --write, stdout has the snapshot and no file is written.
            target.unlink()
            stdout_result = run(root=tmp_root)
            self.assertEqual(stdout_result.returncode, 0)
            self.assertIn("# Brain snapshot", stdout_result.stdout)
            self.assertFalse(target.exists())

    def test_determinism_against_same_fixture(self) -> None:
        first = run()
        second = run()
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        # date is fixed via --today, so the full output should match byte-for-byte.
        self.assertEqual(first.stdout, second.stdout)


if __name__ == "__main__":
    unittest.main()
