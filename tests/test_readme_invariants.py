"""README and VERSION count invariants.

Three tests that fail when README claims drift from filesystem reality.

Test 1: The 'N skills, N commands, N tests' pattern in README.md must match
        the actual counts on disk.
Test 2: The first ## version header in CHANGELOG.md must match VERSION file.
Test 3: If CLAUDE.md or AGENTS.md also contain the pattern, they must match
        the same counts. Skipped silently when neither contains the pattern.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_COUNTS_PATTERN = re.compile(r"(\d+) skills,\s*(\d+) commands,\s*(\d+) tests")


def _filesystem_counts() -> tuple[int, int, int]:
    """Return (skill_count, command_count, test_count) from the filesystem."""
    skill_count = len(list((REPO_ROOT / "skills").glob("*/SKILL.md")))
    command_count = len(list((REPO_ROOT / ".claude" / "commands").glob("*.md")))
    test_count = unittest.TestLoader().discover(str(REPO_ROOT / "tests")).countTestCases()
    return skill_count, command_count, test_count


class ReadmeInvariantTests(unittest.TestCase):

    def test_readme_counts_match_filesystem(self) -> None:
        """README 'N skills, N commands, N tests' must match disk reality."""
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        match = _COUNTS_PATTERN.search(readme)
        self.assertIsNotNone(
            match,
            "README.md must contain a 'N skills, N commands, N tests' line",
        )
        readme_skills = int(match.group(1))
        readme_commands = int(match.group(2))
        readme_tests = int(match.group(3))

        actual_skills, actual_commands, actual_tests = _filesystem_counts()

        self.assertEqual(
            readme_skills,
            actual_skills,
            f"README says {readme_skills} skills but found {actual_skills} SKILL.md files",
        )
        self.assertEqual(
            readme_commands,
            actual_commands,
            f"README says {readme_commands} commands but found {actual_commands} command files",
        )
        self.assertEqual(
            readme_tests,
            actual_tests,
            f"README says {readme_tests} tests but loader finds {actual_tests}",
        )

    def test_version_matches_changelog(self) -> None:
        """VERSION file must match the first ## v... header in CHANGELOG.md."""
        version_file = REPO_ROOT / "VERSION"
        changelog_file = REPO_ROOT / "CHANGELOG.md"

        self.assertTrue(version_file.exists(), "VERSION file must exist at repo root")
        self.assertTrue(changelog_file.exists(), "CHANGELOG.md must exist at repo root")

        version = version_file.read_text(encoding="utf-8").strip()
        changelog = changelog_file.read_text(encoding="utf-8")

        header_match = re.search(r"^## v(\S+)", changelog, re.MULTILINE)
        self.assertIsNotNone(
            header_match,
            "CHANGELOG.md must contain at least one '## v...' header",
        )
        changelog_version = header_match.group(1).split(" ")[0].lstrip("v")

        self.assertEqual(
            version,
            changelog_version,
            f"VERSION={version!r} does not match first CHANGELOG header v{changelog_version!r}",
        )

    def test_claude_md_counts_match_filesystem_if_present(self) -> None:
        """CLAUDE.md / AGENTS.md count claims must match filesystem if the
        pattern exists. Skipped silently if neither file contains it."""
        target_files = [
            REPO_ROOT / "CLAUDE.md",
            REPO_ROOT / "AGENTS.md",
        ]
        found_pattern = False
        for target in target_files:
            if not target.exists():
                continue
            text = target.read_text(encoding="utf-8")
            match = _COUNTS_PATTERN.search(text)
            if match is None:
                continue
            found_pattern = True
            claimed_skills = int(match.group(1))
            claimed_commands = int(match.group(2))
            claimed_tests = int(match.group(3))
            actual_skills, actual_commands, actual_tests = _filesystem_counts()
            self.assertEqual(
                claimed_skills,
                actual_skills,
                f"{target.name} says {claimed_skills} skills but found {actual_skills}",
            )
            self.assertEqual(
                claimed_commands,
                actual_commands,
                f"{target.name} says {claimed_commands} commands but found {actual_commands}",
            )
            self.assertEqual(
                claimed_tests,
                actual_tests,
                f"{target.name} says {claimed_tests} tests but loader finds {actual_tests}",
            )

        if not found_pattern:
            self.skipTest(
                "Neither CLAUDE.md nor AGENTS.md contains the counts pattern — skipping"
            )


if __name__ == "__main__":
    unittest.main()
