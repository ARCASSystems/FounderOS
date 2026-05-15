"""Tests for scripts/check-private-names.py — the WS1 pre-commit privacy guard.

All tests drive the script as a subprocess so they exercise the real exit codes
and stderr output. The PRIVATE_NAME_PATTERNS_FILE env var is used as the test
seam to inject a temp patterns file without touching the real
scripts/private-name-patterns.txt (which is gitignored and operator-specific).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check-private-names.py"


def _run_hook(
    *args: str,
    patterns_file: Path | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if patterns_file is not None:
        env["PRIVATE_NAME_PATTERNS_FILE"] = str(patterns_file)
    else:
        # Ensure the default path is absent so test 5 is deterministic.
        env.pop("PRIVATE_NAME_PATTERNS_FILE", None)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        env=env,
        cwd=str(cwd) if cwd else None,
    )


def _make_temp_git_repo(tmp: Path) -> Path:
    """Initialise a minimal git repo in tmp/repo."""
    repo = tmp / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=True, capture_output=True, cwd=str(repo),
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        check=True, capture_output=True, cwd=str(repo),
    )
    return repo


def _make_patterns_file(tmp: Path, patterns: list[str]) -> Path:
    f = tmp / "patterns.txt"
    f.write_text("\n".join(patterns) + "\n", encoding="utf-8")
    return f


class PrivateNameHookTests(unittest.TestCase):

    def test_staged_exits_1_when_diff_matches(self) -> None:
        """--staged exits 1 when a staged file contains a pattern match."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            repo = _make_temp_git_repo(tmp)
            patterns_file = _make_patterns_file(tmp, [r"\bSecretPerson\b"])

            secret_file = repo / "test.txt"
            secret_file.write_text("Hello SecretPerson, hope you are well.\n", encoding="utf-8")
            subprocess.run(["git", "add", "test.txt"], check=True, capture_output=True, cwd=str(repo))

            result = _run_hook("--staged", patterns_file=patterns_file, cwd=repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("BLOCKED", result.stderr)
            self.assertIn("SecretPerson", result.stderr)

    def test_staged_exits_0_when_diff_clean(self) -> None:
        """--staged exits 0 when staged diff contains no pattern match."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            repo = _make_temp_git_repo(tmp)
            patterns_file = _make_patterns_file(tmp, [r"\bSecretPerson\b"])

            clean_file = repo / "test.txt"
            clean_file.write_text("Hello world, this file is clean.\n", encoding="utf-8")
            subprocess.run(["git", "add", "test.txt"], check=True, capture_output=True, cwd=str(repo))

            result = _run_hook("--staged", patterns_file=patterns_file, cwd=repo)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr.strip(), "")

    def test_message_exits_1_when_commit_message_matches(self) -> None:
        """--message exits 1 when commit message contains a pattern match."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            patterns_file = _make_patterns_file(tmp, [r"\bSecretPerson\b"])
            msg_file = tmp / "COMMIT_EDITMSG"
            msg_file.write_text("fix: update config for SecretPerson's team\n", encoding="utf-8")

            result = _run_hook("--message", str(msg_file), patterns_file=patterns_file)

            self.assertEqual(result.returncode, 1)
            self.assertIn("BLOCKED", result.stderr)
            self.assertIn("SecretPerson", result.stderr)

    def test_message_exits_0_when_commit_message_clean(self) -> None:
        """--message exits 0 when commit message has no pattern match."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            patterns_file = _make_patterns_file(tmp, [r"\bSecretPerson\b"])
            msg_file = tmp / "COMMIT_EDITMSG"
            msg_file.write_text("fix: update config for the team\n", encoding="utf-8")

            result = _run_hook("--message", str(msg_file), patterns_file=patterns_file)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr.strip(), "")

    def test_exits_0_silently_when_patterns_file_absent(self) -> None:
        """Script exits 0 silently when the patterns file does not exist.

        This is the operator-not-yet-installed case. Contributors without the
        file should never be blocked.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            repo = _make_temp_git_repo(tmp)
            # No patterns_file argument — PRIVATE_NAME_PATTERNS_FILE not set.
            # Default path (scripts/private-name-patterns.txt) is gitignored and
            # absent in CI, so the hook must pass silently.
            absent_patterns = tmp / "does_not_exist.txt"  # guaranteed absent
            result = _run_hook("--staged", patterns_file=absent_patterns, cwd=repo)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "")
            self.assertEqual(result.stderr.strip(), "")


if __name__ == "__main__":
    unittest.main()
