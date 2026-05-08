"""Tests for scripts/memory-diff.py."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "memory-diff.py"


def run(repo: Path, fake_home: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    env["USERPROFILE"] = str(fake_home)
    cmd = [sys.executable, str(SCRIPT), str(repo)]
    return subprocess.run(cmd, text=True, capture_output=True, env=env)


def make_repo(root: Path) -> Path:
    repo = root / "founder-os"
    repo.mkdir()
    (repo / "CLAUDE.md").write_text("# Founder OS\n", encoding="utf-8")
    (repo / "clients").mkdir()
    return repo


def make_memory_dir(home: Path, slug: str = "Users-jane-founder-os") -> Path:
    memory = home / ".claude" / "projects" / slug / "memory"
    memory.mkdir(parents=True)
    return memory


class MemoryDiffTests(unittest.TestCase):
    def test_no_clients_folder_exits_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = tmp_path / "founder-os"
            repo.mkdir()
            (repo / "CLAUDE.md").write_text("# Founder OS\n", encoding="utf-8")
            home = tmp_path / "home"
            home.mkdir()
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_no_memory_dir_exits_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = make_repo(tmp_path)
            (repo / "clients" / "acme").mkdir()
            (repo / "clients" / "acme" / "intel.md").write_text("intel", encoding="utf-8")
            home = tmp_path / "home"
            home.mkdir()
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_uncovered_slug_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = make_repo(tmp_path)
            (repo / "clients" / "acme").mkdir()
            (repo / "clients" / "acme" / "intel.md").write_text("intel", encoding="utf-8")
            home = tmp_path / "home"
            memory = make_memory_dir(home)
            (memory / "MEMORY.md").write_text(
                "# Memory Index\n\n- [Other](project_other.md)\n", encoding="utf-8"
            )
            (memory / "project_other.md").write_text(
                "---\nname: other\n---\n\nUnrelated content.\n", encoding="utf-8"
            )
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertIn("Active client folders without memory entry", result.stdout)
            self.assertIn("clients/acme/", result.stdout)

    def test_covered_via_memory_index_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = make_repo(tmp_path)
            (repo / "clients" / "acme").mkdir()
            (repo / "clients" / "acme" / "intel.md").write_text("intel", encoding="utf-8")
            home = tmp_path / "home"
            memory = make_memory_dir(home)
            (memory / "MEMORY.md").write_text(
                "# Memory Index\n\n- [Acme work](project_acme.md) - context for acme\n",
                encoding="utf-8",
            )
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_covered_via_project_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = make_repo(tmp_path)
            (repo / "clients" / "acme-corp").mkdir()
            (repo / "clients" / "acme-corp" / "intel.md").write_text("intel", encoding="utf-8")
            home = tmp_path / "home"
            memory = make_memory_dir(home)
            (memory / "MEMORY.md").write_text("# Memory Index\n", encoding="utf-8")
            (memory / "project_acme_corp_notes.md").write_text(
                "---\nname: acme corp notes\n---\n\nNotes here.\n", encoding="utf-8"
            )
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_covered_via_project_first_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = make_repo(tmp_path)
            (repo / "clients" / "jane-doe").mkdir()
            (repo / "clients" / "jane-doe" / "intel.md").write_text("intel", encoding="utf-8")
            home = tmp_path / "home"
            memory = make_memory_dir(home)
            (memory / "MEMORY.md").write_text("# Memory Index\n", encoding="utf-8")
            (memory / "project_jane_intro.md").write_text(
                "---\nname: jane intro\n---\n\nFirst meeting context.\n",
                encoding="utf-8",
            )
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_empty_clients_folder_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = make_repo(tmp_path)
            (repo / "clients" / "ghost").mkdir()
            home = tmp_path / "home"
            memory = make_memory_dir(home)
            (memory / "MEMORY.md").write_text("# Memory Index\n", encoding="utf-8")
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_slug_match_handles_hyphenated_folder_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = make_repo(tmp_path)
            (repo / "clients" / "acme").mkdir()
            (repo / "clients" / "acme" / "intel.md").write_text("intel", encoding="utf-8")
            home = tmp_path / "home"
            # Slug uses the hyphenated `founder-os` form (the public-OS shape).
            memory = make_memory_dir(home, slug="c--Users-jane-founder-os")
            (memory / "MEMORY.md").write_text("# Memory Index\n", encoding="utf-8")
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertIn("clients/acme/", result.stdout)

    def test_slug_match_handles_unhyphenated_folder_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = make_repo(tmp_path)
            (repo / "clients" / "acme").mkdir()
            (repo / "clients" / "acme" / "intel.md").write_text("intel", encoding="utf-8")
            home = tmp_path / "home"
            # Slug uses the unhyphenated `founderos` form.
            memory = make_memory_dir(home, slug="Users-jane-founderos")
            (memory / "MEMORY.md").write_text("# Memory Index\n", encoding="utf-8")
            result = run(repo, home)
            self.assertEqual(result.returncode, 0)
            self.assertIn("clients/acme/", result.stdout)


if __name__ == "__main__":
    unittest.main()
