import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUERY_SCRIPT = REPO_ROOT / "scripts" / "query.py"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "query-corpus"


def run_query(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(QUERY_SCRIPT), "--root", str(FIXTURE_ROOT), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


class QueryCliTests(unittest.TestCase):
    def test_bare_index_matches_explicit_index(self) -> None:
        bare = run_query("outreach", "stalled")
        explicit = run_query("--mode", "index", "outreach", "stalled")

        self.assertEqual(bare.returncode, 0)
        self.assertEqual(explicit.returncode, 0)
        self.assertEqual(bare.stdout, explicit.stdout)

    def test_index_caps_results_and_shows_id(self) -> None:
        result = run_query("outreach", "stalled")

        self.assertEqual(result.returncode, 0)
        rows = re.findall(r"^\d+\. ", result.stdout, flags=re.MULTILINE)
        self.assertGreaterEqual(len(rows), 1)
        self.assertLessEqual(len(rows), 10)
        self.assertIn("(id: flag-2026-05-04-001)", result.stdout)

    def test_timeline_is_chronological_and_windowed(self) -> None:
        result = run_query("--mode", "timeline", "--anchor", "CLAUDE.md")

        self.assertEqual(result.returncode, 0)
        dates = re.findall(r"^(2026-\d{2}-\d{2}) - ", result.stdout, flags=re.MULTILINE)
        self.assertGreaterEqual(len(dates), 2)
        self.assertEqual(dates, sorted(dates))
        self.assertIn("2026-05-04 - brain/flags.md", result.stdout)
        self.assertNotIn("2026-04-20 - brain/patterns.md", result.stdout)
        self.assertNotIn("tests/hidden.md", result.stdout)

    def test_full_mode_resolves_frontmatter_and_heading_ids(self) -> None:
        result = run_query(
            "--mode",
            "full",
            "--ids",
            "know-2026-05-08-001,flag-2026-05-04-001",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("=== know-2026-05-08-001 (brain/knowledge/sales.md) ===", result.stdout)
        self.assertIn("Signals from early outreach live here.", result.stdout)
        self.assertIn("=== flag-2026-05-04-001 (brain/flags.md) ===", result.stdout)
        self.assertIn("Pipeline follow-up stalled after the first outreach pass.", result.stdout)

    def test_punctuation_guard_exits_two(self) -> None:
        result = run_query("?")

        self.assertEqual(result.returncode, 2)
        self.assertIn("No searchable tokens", result.stdout)

    def test_no_argument_usage_exits_two(self) -> None:
        result = run_query()

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: python scripts/query.py <question>", result.stdout)


if __name__ == "__main__":
    unittest.main()
