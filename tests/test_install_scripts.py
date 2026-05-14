"""
Static tests for install.sh and uninstall.sh.
Checks shell syntax, content guards, and natural-language surface requirements.
End-to-end execution tests live in tests/test_e2e_critical_paths.py (Session 3 / W6).
"""
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from tests.test_session_hooks import bash_path

REPO_ROOT = Path(__file__).parent.parent
INSTALL_SH = REPO_ROOT / "install.sh"
UNINSTALL_SH = REPO_ROOT / "uninstall.sh"


def _bash_available() -> bool:
    try:
        result = subprocess.run(
            ["bash", "--version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


BASH_AVAILABLE = _bash_available()
BASH_BIN = shutil.which("bash") or "bash"
require_bash = unittest.skipUnless(BASH_AVAILABLE, "bash not available in this environment")


class InstallShellSyntaxTests(unittest.TestCase):
    """Verify scripts parse without errors under bash -n."""

    @require_bash
    def test_install_sh_parses(self):
        result = subprocess.run(
            [BASH_BIN, "-n", bash_path(BASH_BIN, INSTALL_SH)],
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"bash -n install.sh failed:\n{result.stderr.decode()}",
        )

    @require_bash
    def test_uninstall_sh_parses(self):
        result = subprocess.run(
            [BASH_BIN, "-n", bash_path(BASH_BIN, UNINSTALL_SH)],
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"bash -n uninstall.sh failed:\n{result.stderr.decode()}",
        )


class InstallContentTests(unittest.TestCase):
    """Verify install.sh content guards - static analysis of the script body."""

    def setUp(self):
        self.install_text = INSTALL_SH.read_text(encoding="utf-8")
        self.uninstall_text = UNINSTALL_SH.read_text(encoding="utf-8")

    def test_install_sh_does_not_require_env_vars(self):
        """Script must not reference API_KEY or other required env vars."""
        self.assertNotIn("API_KEY", self.install_text)
        self.assertNotIn("ANTHROPIC_API_KEY", self.install_text)
        self.assertNotIn("OPENAI_API_KEY", self.install_text)

    def test_install_sh_does_not_require_paid_keys(self):
        """No paid-key references in the install script."""
        forbidden = ["API_KEY", "SECRET_KEY", "PAID_KEY", "STRIPE_"]
        for token in forbidden:
            self.assertNotIn(
                token,
                self.install_text,
                f"install.sh references '{token}' - paid keys must not be required",
            )

    def test_install_sh_prints_natural_language_next_step(self):
        """Script must end with a 'Say ...' natural-language instruction."""
        self.assertIn("Say", self.install_text)
        self.assertIn("set up FounderOS", self.install_text)

    def test_install_sh_has_dry_run_flag(self):
        """Script must support --dry-run for W6 smoke tests."""
        self.assertIn("--dry-run", self.install_text)

    def test_install_sh_has_help_flag(self):
        self.assertIn("--help", self.install_text)

    def test_uninstall_sh_preserves_user_data_paths(self):
        """uninstall.sh must explicitly name user data directories as preserved."""
        for preserved in ["core", "cadence", "context", "brain"]:
            self.assertIn(
                preserved,
                self.uninstall_text,
                f"uninstall.sh does not mention preserved path '{preserved}'",
            )

    def test_uninstall_sh_lists_before_removing(self):
        """uninstall.sh must print an inventory before asking for confirmation."""
        # The listing section must appear before the confirmation prompt in the file.
        list_marker = "The following will be removed"
        confirm_marker = "Proceed with removal"
        list_pos = self.uninstall_text.find(list_marker)
        confirm_pos = self.uninstall_text.find(confirm_marker)
        self.assertGreater(list_pos, -1, "uninstall.sh missing inventory section")
        self.assertGreater(confirm_pos, -1, "uninstall.sh missing confirmation prompt")
        self.assertLess(
            list_pos,
            confirm_pos,
            "uninstall.sh must list files BEFORE asking for confirmation",
        )

    def test_uninstall_sh_user_data_preserved_language(self):
        """Final output must include language about user data being preserved."""
        self.assertIn("preserved", self.uninstall_text.lower())


class CadenceTemplatePlaceholderTests(unittest.TestCase):
    """Cadence templates must not ship raw {{PLACEHOLDER}} tokens.

    {{DATE}} in daily-anchors.md is the sole exception - the setup wizard
    substitutes it with today's date at install time (see setup SKILL.md).
    All other {{...}} tokens must be replaced with [NOT SET] so founders do
    not see broken-looking files on first run.
    """

    CADENCE_FILES = [
        "templates/cadence/daily-anchors.md",
        "templates/cadence/quarterly-sprints.md",
        "templates/cadence/annual-targets.md",
    ]

    def _read(self, rel_path: str) -> str:
        return (REPO_ROOT / rel_path).read_text(encoding="utf-8")

    def test_no_raw_placeholders_in_daily_anchors(self):
        content = self._read("templates/cadence/daily-anchors.md")
        # Strip the one legitimate setup-time substitution variable
        content_without_date = content.replace("{{DATE}}", "")
        self.assertNotIn(
            "{{",
            content_without_date,
            "templates/cadence/daily-anchors.md contains raw {{PLACEHOLDER}} tokens other than {{DATE}}",
        )

    def test_no_raw_placeholders_in_quarterly_sprints(self):
        content = self._read("templates/cadence/quarterly-sprints.md")
        self.assertNotIn(
            "{{",
            content,
            "templates/cadence/quarterly-sprints.md contains raw {{PLACEHOLDER}} tokens",
        )

    def test_no_raw_placeholders_in_annual_targets(self):
        content = self._read("templates/cadence/annual-targets.md")
        self.assertNotIn(
            "{{",
            content,
            "templates/cadence/annual-targets.md contains raw {{PLACEHOLDER}} tokens",
        )


class TemplateScriptPresenceTests(unittest.TestCase):
    """Assert that all seven helper scripts have a templates/scripts/ mirror."""

    def _template_path(self, name: str) -> Path:
        return REPO_ROOT / "templates" / "scripts" / name

    def test_menu_py_template_exists(self):
        path = self._template_path("menu.py")
        self.assertTrue(
            path.exists(),
            "templates/scripts/menu.py is missing - setup cannot copy it to the founder's scripts/",
        )

    def test_observation_rollup_py_template_exists(self):
        path = self._template_path("observation-rollup.py")
        self.assertTrue(
            path.exists(),
            "templates/scripts/observation-rollup.py is missing - setup cannot copy it to the founder's scripts/",
        )

    def test_all_seven_template_scripts_exist(self):
        required = [
            "wiki-build.py",
            "query.py",
            "brain-snapshot.py",
            "brain-pass-log.py",
            "memory-diff.py",
            "menu.py",
            "observation-rollup.py",
        ]
        for name in required:
            with self.subTest(script=name):
                path = self._template_path(name)
                self.assertTrue(
                    path.exists(),
                    f"templates/scripts/{name} is missing",
                )


if __name__ == "__main__":
    unittest.main()
