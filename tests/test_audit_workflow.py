"""Smoke tests for .github/scripts/audit.py + format_issue.py.

The audit workflow runs on a weekly cron (and on manual dispatch). These tests
lock the two new behaviors that the cron mode depends on:

1. `audit.py --since` exposes the date-window argument the workflow passes.
2. `format_issue.py` switches to a digest header when scan_window is present
   in the findings JSON, instead of the per-commit header.

Neither script has a public API, so the tests run them as subprocesses against
synthetic inputs.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = REPO_ROOT / ".github" / "scripts" / "audit.py"
FORMAT_SCRIPT = REPO_ROOT / ".github" / "scripts" / "format_issue.py"


class AuditSinceFlagTests(unittest.TestCase):
    def test_help_documents_since_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT), "--help"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--since", result.stdout)
        self.assertIn("7 days ago", result.stdout)


class FormatIssueDigestHeaderTests(unittest.TestCase):
    def _run_with_findings(self, findings: dict) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            findings_path = Path(tmp) / "audit_findings.json"
            findings_path.write_text(json.dumps(findings), encoding="utf-8")
            env = os.environ.copy()
            env["AUDIT_FINDINGS_PATH"] = str(findings_path)
            result = subprocess.run(
                [sys.executable, str(FORMAT_SCRIPT)],
                capture_output=True, text=True, check=False, env=env,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            return result.stdout

    def test_digest_header_used_when_scan_window_present(self) -> None:
        body = self._run_with_findings({
            "commit": "0" * 40,
            "actor": "ARCASSystems",
            "ref": "refs/heads/main",
            "scan_window": {"since": "7 days ago", "commits_scanned": 12},
            "changed_files": ["README.md"],
            "touched_high_impact": ["README.md"],
            "leakage_findings": [],
            "has_findings": True,
        })
        self.assertIn("Weekly digest", body)
        self.assertIn("7 days ago", body)
        self.assertIn("12 commit(s) scanned", body)
        self.assertNotIn("actor **", body)

    def test_per_commit_header_used_when_no_scan_window(self) -> None:
        body = self._run_with_findings({
            "commit": "abcdef1234567890" + "0" * 24,
            "actor": "ARCASSystems",
            "ref": "refs/heads/main",
            "changed_files": ["README.md"],
            "touched_high_impact": ["README.md"],
            "leakage_findings": [],
            "has_findings": True,
        })
        self.assertIn("abcdef12", body)
        self.assertIn("actor **ARCASSystems**", body)
        self.assertNotIn("Weekly digest", body)


if __name__ == "__main__":
    unittest.main()
