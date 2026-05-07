"""Tests for scripts/brain-pass-log.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "brain-pass-log.py"
FIXED_NOW = "2026-05-08T14:30:00+00:00"


def run(*args: str, root: Path, enabled: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("FOUNDER_OS_OBSERVATIONS", None)
    if enabled:
        env["FOUNDER_OS_OBSERVATIONS"] = "1"
    cmd = [sys.executable, str(SCRIPT), "--root", str(root), "--now", FIXED_NOW, *args]
    return subprocess.run(cmd, text=True, capture_output=True, env=env)


class BrainPassLogTests(unittest.TestCase):
    def test_writes_one_jsonl_line_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run(
                "--question", "what blocks the launch?",
                "--confidence", "high",
                "--ids-cited", "log-2026-05-04-001,flag-2026-05-02-001",
                "--files-read", "4",
                "--has-gaps", "yes",
                root=root,
            )
            self.assertEqual(result.returncode, 0)
            target = root / "brain" / "observations" / "2026-05-08.jsonl"
            self.assertTrue(target.exists())
            lines = target.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            payload = json.loads(lines[0])
            self.assertEqual(payload["type"], "brain_pass")
            self.assertEqual(payload["question"], "what blocks the launch?")
            self.assertEqual(payload["confidence"], "high")
            self.assertEqual(payload["files_read"], 4)
            self.assertEqual(payload["ids_cited"], ["log-2026-05-04-001", "flag-2026-05-02-001"])
            self.assertTrue(payload["has_gaps"])
            self.assertTrue(payload["timestamp"].startswith("2026-05-08T14:30:00"))

    def test_no_op_when_env_var_unset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run(
                "--question", "anything",
                "--confidence", "high",
                root=root,
                enabled=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            target = root / "brain" / "observations" / "2026-05-08.jsonl"
            self.assertFalse(target.exists())

    def test_appends_subsequent_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for q in ["first question", "second question"]:
                result = run("--question", q, "--confidence", "medium", root=root)
                self.assertEqual(result.returncode, 0)
            target = root / "brain" / "observations" / "2026-05-08.jsonl"
            lines = target.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            payloads = [json.loads(line) for line in lines]
            self.assertEqual(payloads[0]["question"], "first question")
            self.assertEqual(payloads[1]["question"], "second question")

    def test_invalid_confidence_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run(
                "--question", "anything",
                "--confidence", "bogus",
                root=root,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("--confidence must be one of", result.stderr)
            target = root / "brain" / "observations" / "2026-05-08.jsonl"
            self.assertFalse(target.exists())

    def test_question_truncated_at_280_chars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            long_q = "x" * 400
            result = run(
                "--question", long_q,
                "--confidence", "low",
                root=root,
            )
            self.assertEqual(result.returncode, 0)
            target = root / "brain" / "observations" / "2026-05-08.jsonl"
            payload = json.loads(target.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(len(payload["question"]), 280)


if __name__ == "__main__":
    unittest.main()
