"""Behavioral tests for scripts/menu.py.

The menu engine reads state files and scores capabilities. These tests run
the script against fixture roots and assert on stdout. No LLM call, no
network, deterministic with --today override.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MENU_SCRIPT = REPO_ROOT / "scripts" / "menu.py"

CLOSING_LINE = (
    "These are tailored to your current state. Say any of the natural-language "
    "phrases above. Or ask Claude anything in plain English - most of FounderOS "
    "routes by what you say, not what you type."
)

DAY_ONE_PHRASES = [
    "set up my voice profile",
    "set up my brand profile",
    "what should I focus on next",
    "what's on for today",
    "ingest this",
]

# Skills that exist but have NO command file. Menu MUST NOT emit a slash form
# for these. They render natural-language only.
SKILL_ONLY_CAPABILITIES = ["weekly-review", "priority-triage", "pre-send-check"]


def run_menu(root: Path, today: str = "2026-05-10") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MENU_SCRIPT), "--root", str(root), "--today", today],
        capture_output=True,
        text=True,
        timeout=15,
    )


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class MenuScriptExists(unittest.TestCase):
    def test_script_exists_and_executable(self) -> None:
        self.assertTrue(MENU_SCRIPT.is_file(), "scripts/menu.py must exist")

    def test_script_help_works(self) -> None:
        r = subprocess.run(
            [sys.executable, str(MENU_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("--root", r.stdout)
        self.assertIn("--today", r.stdout)

    def test_no_llm_or_network_imports(self) -> None:
        src = MENU_SCRIPT.read_text(encoding="utf-8")
        for forbidden in (
            "import openai",
            "import anthropic",
            "import requests",
            "import httpx",
            "import urllib.request",
        ):
            self.assertNotIn(forbidden, src, f"menu.py must not contain '{forbidden}'")


class ZeroStateMenu(unittest.TestCase):
    def test_zero_state_returns_day_one_set(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            r = run_menu(Path(td))
            self.assertEqual(r.returncode, 0, f"stderr: {r.stderr}")
            for phrase in DAY_ONE_PHRASES:
                self.assertIn(phrase, r.stdout, f"Day-1 phrase missing: {phrase}")

    def test_zero_state_returns_at_least_five_rows(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            r = run_menu(Path(td))
            rows = [ln for ln in r.stdout.splitlines() if ln.lstrip().startswith("- ")]
            self.assertGreaterEqual(len(rows), 5)
            self.assertLessEqual(len(rows), 7)

    def test_zero_state_includes_closing_line_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            r = run_menu(Path(td))
            self.assertIn(CLOSING_LINE, r.stdout)


class CapabilityCommandMap(unittest.TestCase):
    """Skills without command files MUST NOT render a /founder-os: slash form."""

    def test_zero_state_does_not_invent_skill_only_slash_commands(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            r = run_menu(Path(td))
            for cap in SKILL_ONLY_CAPABILITIES:
                self.assertNotIn(
                    f"/founder-os:{cap}",
                    r.stdout,
                    f"menu invented nonexistent slash command for {cap}",
                )
                self.assertNotIn(
                    f"/{cap}",
                    r.stdout,
                    f"menu invented bare slash command for {cap}",
                )

    def test_populated_state_does_not_invent_skill_only_slash_commands(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_file(root / "core" / "voice-profile.yml", "voice: present\n")
            write_file(root / "core" / "brand-profile.yml", "brand: present\n")
            write_file(
                root / "cadence" / "weekly-commitments.md",
                "## Week of 2026-05-04\n- ship v1.20.1\n",
            )
            write_file(
                root / "brain" / "log.md",
                "\n".join(
                    f"### 2026-05-{d:02d} entry seed line" for d in range(1, 11)
                ),
            )
            write_file(root / "context" / "priorities.md", "## Week 3+ stalled item\n")
            r = run_menu(root)
            self.assertEqual(r.returncode, 0, f"stderr: {r.stderr}")
            for cap in SKILL_ONLY_CAPABILITIES:
                self.assertNotIn(f"/founder-os:{cap}", r.stdout)


class PopulatedStateMenu(unittest.TestCase):
    def test_populated_returns_five_to_seven_rows(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_file(root / "core" / "voice-profile.yml", "voice: present\n")
            write_file(
                root / "cadence" / "weekly-commitments.md",
                "## Week of 2026-05-04\n- thing\n",
            )
            r = run_menu(root)
            self.assertEqual(r.returncode, 0, f"stderr: {r.stderr}")
            rows = [ln for ln in r.stdout.splitlines() if ln.lstrip().startswith("- ")]
            self.assertGreaterEqual(len(rows), 5)
            self.assertLessEqual(len(rows), 7)

    def test_populated_includes_closing_line(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_file(root / "core" / "voice-profile.yml", "voice: present\n")
            r = run_menu(root)
            self.assertIn(CLOSING_LINE, r.stdout)

    def test_missing_snapshot_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_file(
                root / "brain" / "log.md",
                "### 2026-05-09 something\n### 2026-05-08 other thing\n",
            )
            r = run_menu(root)
            self.assertEqual(r.returncode, 0, f"stderr: {r.stderr}")
            self.assertIn(CLOSING_LINE, r.stdout)


class MenuOutputHygiene(unittest.TestCase):
    BANNED = [
        "leverage", "seamless", "robust", "comprehensive", "holistic",
        "transformative", "streamline", "optimize", "utilize", "delve",
        "navigate", "ecosystem", "landscape", "unlock", "facilitate",
    ]

    def test_no_banned_phrases_in_zero_state_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            r = run_menu(Path(td))
            lower = r.stdout.lower()
            for word in self.BANNED:
                self.assertNotRegex(
                    lower,
                    rf"\b{word}\b",
                    f"menu output contains banned word: {word}",
                )

    def test_no_em_or_en_dashes_in_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            r = run_menu(Path(td))
            self.assertNotIn("—", r.stdout, "em dash in menu output")
            self.assertNotIn("–", r.stdout, "en dash in menu output")


class SkillFileSurface(unittest.TestCase):
    """The SKILL.md is the user-facing surface. Verify it points to the script
    and does not contain the broken 'model is the engine' language."""

    def test_skill_invokes_script(self) -> None:
        skill = (REPO_ROOT / "skills" / "menu" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("scripts/menu.py", skill)

    def test_skill_does_not_say_model_is_engine(self) -> None:
        skill = (REPO_ROOT / "skills" / "menu" / "SKILL.md").read_text(encoding="utf-8")
        lower = skill.lower()
        self.assertNotIn("model is the menu engine", lower)
        self.assertNotIn("model running this skill is the menu engine", lower)


if __name__ == "__main__":
    unittest.main()
