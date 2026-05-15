"""Tests for scripts/check-log-has-history.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check-log-has-history.py"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), "--root", str(root)]
    return subprocess.run(cmd, text=True, capture_output=True)


def write_log(root: Path, body: str) -> None:
    (root / "brain").mkdir(parents=True, exist_ok=True)
    (root / "brain" / "log.md").write_text(body, encoding="utf-8")


class CheckLogHasHistoryTests(unittest.TestCase):
    def test_missing_or_undated_file_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            # File missing entirely.
            result = run(tmp_root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("no dated entries", result.stdout.lower())

            # File present, only template prose.
            write_log(
                tmp_root,
                "# brain/log.md\n\n"
                "> Running log of observations and actions.\n\n"
                "## How to use\n\nAppend dated entries as work happens.\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("no dated entries", result.stdout.lower())

    def test_dated_entry_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            write_log(
                tmp_root,
                "# brain/log.md\n\n"
                "## How to use\n\nAppend dated entries.\n\n"
                "### 2026-05-15\n\n"
                "- #acted [M] shipped v1.24 voice gate scripts\n",
            )
            result = run(tmp_root)
            self.assertEqual(result.returncode, 0, msg=result.stdout)
            self.assertIn("dated entries", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
