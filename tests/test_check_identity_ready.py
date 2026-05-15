"""Tests for scripts/check-identity-ready.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check-identity-ready.py"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), "--root", str(root)]
    return subprocess.run(cmd, text=True, capture_output=True)


def write_identity(root: Path, body: str) -> None:
    (root / "core").mkdir(parents=True, exist_ok=True)
    (root / "core" / "identity.md").write_text(body, encoding="utf-8")


class CheckIdentityReadyTests(unittest.TestCase):
    def test_missing_file_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run(Path(tmp))
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing", result.stdout.lower())
            self.assertIn("setup", result.stdout.lower())

    def test_template_markers_exit_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            write_identity(
                tmp_root,
                "# core/identity.md\n\n## Basics\n\n"
                "**Name:** {{FOUNDER_NAME}}\n"
                "**Role:** Founder\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("setup", result.stdout.lower())

    def test_not_set_marker_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            write_identity(
                tmp_root,
                "# core/identity.md\n\n## Basics\n\n"
                "**Name:** Jane Doe\n"
                "**Role:** Founder\n"
                "**Location:** London\n\n"
                "## Positioning\n\n"
                "- one-line: [NOT SET]\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 0, msg=result.stdout)
            self.assertIn("ready", result.stdout.lower())

    def test_fill_marker_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            write_identity(
                tmp_root,
                "# core/identity.md\n\n## Basics\n\n"
                "**Name:** [FILL]\n"
                "**Role:** Founder\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("setup", result.stdout.lower())

    def test_real_content_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            write_identity(
                tmp_root,
                "# core/identity.md\n\n## Basics\n\n"
                "**Name:** Jane Doe\n"
                "**Role:** Founder / CEO\n"
                "**Location:** London\n"
                "**Team size:** solo\n"
                "**Time zone:** GMT\n\n"
                "## Background\n\n"
                "Ten years in fintech operations. Built a payments platform before this.\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 0, msg=result.stdout)
            self.assertIn("ready", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
