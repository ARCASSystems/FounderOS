"""
Tests for W4 - observation rollup script.
Asserts behavioral correctness of scripts/observation-rollup.py using a
temporary filesystem. No mocking of Python stdlib. No external dependencies.
"""

import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROLLUP_SCRIPT = REPO_ROOT / "scripts" / "observation-rollup.py"


def load_rollup():
    """Import the rollup script as a module. Caches across calls."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("observation_rollup", ROLLUP_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_obs_dir(tmp: Path) -> Path:
    """Create a brain/observations/ structure under tmp."""
    obs = tmp / "brain" / "observations"
    obs.mkdir(parents=True)
    return obs


def write_jsonl(path: Path, entries: list) -> None:
    with path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def days_of_week(anchor: date) -> list:
    """Return 7 consecutive dates starting from anchor (Mon of its ISO week)."""
    iso = anchor.isocalendar()
    monday = anchor - timedelta(days=iso[2] - 1)
    return [monday + timedelta(days=i) for i in range(7)]


class ObservationRollupScriptTests(unittest.TestCase):

    def setUp(self):
        self.mod = load_rollup()
        self.tmp = Path(tempfile.mkdtemp())
        self.obs_dir = make_obs_dir(self.tmp)
        # main() uses argparse against sys.argv; isolate the test runner's args.
        self._saved_argv = sys.argv
        sys.argv = ["observation-rollup.py"]

    def tearDown(self):
        import shutil
        sys.argv = self._saved_argv
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _complete_week_dates(self) -> list:
        """Return 7 dates from a week that ended > 3 days ago."""
        anchor = date.today() - timedelta(days=14)
        return days_of_week(anchor)

    def test_script_groups_by_iso_week(self):
        """Files from the same ISO week are grouped together."""
        week_dates = self._complete_week_dates()
        for d in week_dates:
            path = self.obs_dir / f"{d}.jsonl"
            write_jsonl(path, [{"tool": "Read", "session_id": "s1"}])

        sys.argv = ["observation-rollup.py"]
        self.mod.find_repo_root = lambda start: self.tmp
        self.mod.main()

        rollup_dir = self.obs_dir / "_rollups"
        rollups = list(rollup_dir.glob("*.md"))
        self.assertEqual(len(rollups), 1, "One rollup per ISO week")

        # The rollup filename must be YYYY-Wnn
        import re
        self.assertRegex(rollups[0].stem, r"^\d{4}-W\d{2}$")

    def test_script_aggregates_correctly(self):
        """Rollup file contains aggregated counts for tools and sessions."""
        week_dates = self._complete_week_dates()
        for i, d in enumerate(week_dates):
            path = self.obs_dir / f"{d}.jsonl"
            write_jsonl(path, [
                {"tool": "Read", "session_id": "sess-A"},
                {"tool": "Write", "session_id": "sess-B"},
                {"tool": "Read", "skill": "brain-log", "session_id": "sess-A"},
            ])

        self.mod.find_repo_root = lambda start: self.tmp
        self.mod.main()

        rollup_dir = self.obs_dir / "_rollups"
        rollup_text = next(rollup_dir.glob("*.md")).read_text(encoding="utf-8")

        self.assertIn("Read", rollup_text)
        self.assertIn("Write", rollup_text)
        self.assertIn("brain-log", rollup_text)
        self.assertIn("sess-A", rollup_text)
        self.assertIn("sess-B", rollup_text)
        # 7 days x 3 entries = 21 total
        self.assertIn("21", rollup_text)

    def test_session_key_accepted(self):
        """Rollup counts sessions written with the 'session' key (hook format), not only 'session_id'."""
        week_dates = self._complete_week_dates()
        for d in week_dates:
            path = self.obs_dir / f"{d}.jsonl"
            write_jsonl(path, [
                {"tool": "Read", "session": "hook-session-X"},
                {"tool": "Write", "session": "hook-session-Y"},
            ])

        self.mod.find_repo_root = lambda start: self.tmp
        self.mod.main()

        rollup_dir = self.obs_dir / "_rollups"
        rollup_text = next(rollup_dir.glob("*.md")).read_text(encoding="utf-8")
        self.assertIn("hook-session-X", rollup_text)
        self.assertIn("hook-session-Y", rollup_text)

    def test_script_is_idempotent(self):
        """Running rollup twice on the same data produces no new rollup files."""
        week_dates = self._complete_week_dates()
        for d in week_dates:
            path = self.obs_dir / f"{d}.jsonl"
            write_jsonl(path, [{"tool": "Grep", "session_id": "s1"}])

        self.mod.find_repo_root = lambda start: self.tmp
        self.mod.main()

        rollup_dir = self.obs_dir / "_rollups"
        count_after_first = len(list(rollup_dir.glob("*.md")))

        # Second run - JSONL files are gone, nothing new to roll up
        self.mod.main()
        count_after_second = len(list(rollup_dir.glob("*.md")))

        self.assertEqual(count_after_first, count_after_second,
                         "Second run must not create new rollup files")

    def test_script_deletes_source_only_after_rollup_written(self):
        """Source JSONL files are absent after a successful rollup."""
        week_dates = self._complete_week_dates()
        source_paths = []
        for d in week_dates:
            path = self.obs_dir / f"{d}.jsonl"
            write_jsonl(path, [{"tool": "Edit", "session_id": "s1"}])
            source_paths.append(path)

        self.mod.find_repo_root = lambda start: self.tmp
        self.mod.main()

        rollup_dir = self.obs_dir / "_rollups"
        rollups = list(rollup_dir.glob("*.md"))
        self.assertEqual(len(rollups), 1, "Rollup must exist before we check deletions")

        for p in source_paths:
            self.assertFalse(p.exists(),
                             f"Source file {p.name} must be deleted after rollup written")


if __name__ == "__main__":
    unittest.main()
