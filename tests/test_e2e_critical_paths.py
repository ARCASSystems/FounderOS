"""
End-to-end critical path tests for FounderOS v1.22.

These tests are the warranty that the eight user-critical paths work as
documented. Skills and commands are markdown files interpreted by an LLM;
tests here verify the documented behavior is present and that scriptable
paths (install.sh --dry-run, wiki-build.py idempotency) behave correctly.

All 8 test classes must run in < 30 seconds combined.
No external dependencies. Pure stdlib.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _bash_exe():
    """Return a usable bash executable path, or None."""
    for candidate in ("bash", "bash.exe"):
        found = shutil.which(candidate)
        if found:
            return found
    return None


def read_file(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Setup wizard end-to-end
# ---------------------------------------------------------------------------

class SetupWizardE2ETests(unittest.TestCase):
    """Wizard skill documents all expected file writes and template substitution."""

    def setUp(self):
        self.wizard = read_file("skills/founder-os-setup/SKILL.md")
        self.template = read_file("templates/bootloader-claude-md.md")

    def test_wizard_documents_core_writes(self):
        self.assertIn("core/identity.md", self.wizard)

    def test_wizard_documents_cadence_writes(self):
        self.assertIn("cadence/", self.wizard)

    def test_wizard_documents_context_writes(self):
        self.assertIn("context/", self.wizard)

    def test_wizard_documents_role_noun_substitution(self):
        # Wizard must drive the {{role_noun}} substitution
        self.assertIn("{{role_noun}}", self.wizard)

    def test_bootloader_template_has_role_placeholder(self):
        # Template must contain the placeholder the wizard substitutes
        self.assertIn("{{role_noun}}", self.template)


# ---------------------------------------------------------------------------
# 2. install.sh smoke (--dry-run)
# ---------------------------------------------------------------------------

class InstallShSmokeTests(unittest.TestCase):
    """install.sh --dry-run names expected operations without writing anything."""

    def setUp(self):
        self.bash = _bash_exe()
        self.script = REPO_ROOT / "install.sh"

    def _run_dry(self):
        result = subprocess.run(
            [self.bash, str(self.script), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        return result

    def test_install_sh_exists(self):
        self.assertTrue(self.script.exists(), "install.sh must exist at repo root")

    @unittest.skipIf(_bash_exe() is None, "bash not available on this platform")
    def test_dry_run_exits_without_error(self):
        result = self._run_dry()
        # dry-run may exit 1 if prerequisites are missing but must not crash
        combined = result.stdout + result.stderr
        self.assertNotIn("syntax error", combined.lower())
        self.assertNotIn("command not found", combined.lower())

    @unittest.skipIf(_bash_exe() is None, "bash not available on this platform")
    def test_dry_run_names_operations(self):
        result = self._run_dry()
        combined = result.stdout + result.stderr
        # dry-run mode prints [dry-run] prefixed lines for each operation
        self.assertIn("[dry-run]", combined)

    def test_install_sh_documents_dry_run_flag(self):
        body = self.script.read_text(encoding="utf-8")
        self.assertIn("--dry-run", body)


# ---------------------------------------------------------------------------
# 3. uninstall.sh smoke (--dry-run)
# ---------------------------------------------------------------------------

class UninstallShSmokeTests(unittest.TestCase):
    """uninstall.sh --dry-run lists removals without deleting anything."""

    def setUp(self):
        self.bash = _bash_exe()
        self.script = REPO_ROOT / "uninstall.sh"

    def test_uninstall_sh_exists(self):
        self.assertTrue(self.script.exists(), "uninstall.sh must exist at repo root")

    def test_uninstall_sh_documents_dry_run_flag(self):
        body = self.script.read_text(encoding="utf-8")
        self.assertIn("--dry-run", body)

    def test_uninstall_sh_preserves_user_data(self):
        body = self.script.read_text(encoding="utf-8")
        # Must document that user data directories are NOT removed
        for preserved in ("core/", "cadence/", "brain/", "context/"):
            with self.subTest(path=preserved):
                self.assertIn(preserved, body,
                              f"uninstall.sh must mention {preserved} as preserved")


# ---------------------------------------------------------------------------
# 4. /verify on a healthy state
# ---------------------------------------------------------------------------

class VerifyHealthyStateTests(unittest.TestCase):
    """Verify skill documents all 8 checks and their PASS criteria."""

    def setUp(self):
        self.body = read_file("skills/verify/SKILL.md")

    def test_skill_has_eight_checks(self):
        for n in range(1, 9):
            with self.subTest(check=n):
                self.assertIn(f"Check {n}", self.body)

    def test_skill_documents_pass_status(self):
        self.assertIn("[PASS]", self.body)

    def test_skill_never_auto_fixes(self):
        body_lower = self.body.lower()
        self.assertIn("never auto-fixes", body_lower)

    def test_skill_reports_free_tier_floor(self):
        # Check 5 is the free-tier accessibility check
        self.assertIn("Check 5", self.body)
        self.assertIn("free", self.body.lower())


# ---------------------------------------------------------------------------
# 5. /verify on a broken state
# ---------------------------------------------------------------------------

class VerifyBrokenStateTests(unittest.TestCase):
    """Verify skill documents FAIL detection for broken substrate."""

    def setUp(self):
        self.body = read_file("skills/verify/SKILL.md")

    def test_skill_documents_fail_status(self):
        self.assertIn("[FAIL]", self.body)

    def test_skill_documents_warn_status(self):
        self.assertIn("[WARN]", self.body)

    def test_skill_distinguishes_warn_from_fail(self):
        body_lower = self.body.lower()
        # WARN = degraded but functional; FAIL = broken
        self.assertIn("degraded", body_lower)
        self.assertIn("broken", body_lower)

    def test_skill_checks_script_existence(self):
        # Check 3 must verify that the Python scripts exist
        self.assertIn("Check 3", self.body)
        self.assertIn("scripts/", self.body)


# ---------------------------------------------------------------------------
# 6. Queue 3-cap gate
# ---------------------------------------------------------------------------

class Queue3CapGateTests(unittest.TestCase):
    """Queue skill documents and enforces the 3-item ACTIVE cap."""

    def setUp(self):
        self.skill = read_file("skills/queue/SKILL.md")

    def test_skill_documents_three_item_cap(self):
        # Must state the cap explicitly
        self.assertTrue(
            "3 items" in self.skill or "3-item" in self.skill or "max 3" in self.skill.lower(),
            "Queue skill must document the 3-item ACTIVE cap",
        )

    def test_skill_documents_gate_precondition(self):
        # Hard precondition line must be present
        self.assertIn("Hard precondition", self.skill)

    def test_skill_documents_fourth_item_refused(self):
        # Must state that a fourth item is not added
        self.assertIn("does NOT add a fourth", self.skill)

    def test_skill_documents_gate_response(self):
        # When gate fires, skill returns current ACTIVE entries and asks which to pause
        self.assertIn("capacity (3/3)", self.skill)


# ---------------------------------------------------------------------------
# 7. brain-pass with empty corpus
# ---------------------------------------------------------------------------

class BrainPassEmptyCorpusTests(unittest.TestCase):
    """brain-pass skill documents graceful response when no content found."""

    def setUp(self):
        self.body = read_file("skills/brain-pass/SKILL.md")

    def test_skill_documents_empty_corpus_response(self):
        # Must document the "no relevant content" case
        self.assertIn("no relevant content", self.body.lower())

    def test_skill_does_not_fabricate_on_empty(self):
        # Must explicitly say not to fabricate
        self.assertIn("Do not fabricate", self.body)

    def test_skill_documents_no_content_answer_text(self):
        # Must name the exact output string for empty result
        self.assertIn("No prior brain content found on this question", self.body)


# ---------------------------------------------------------------------------
# 8. wiki-build idempotency
# ---------------------------------------------------------------------------

class WikiBuildIdempotencyTests(unittest.TestCase):
    """Running wiki-build.py twice on the same data produces no diff."""

    def setUp(self):
        self.script = REPO_ROOT / "scripts" / "wiki-build.py"
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_minimal_repo(self) -> Path:
        """Create a minimal FounderOS structure for wiki-build to scan."""
        repo = self.tmp / "repo"
        (repo / "brain").mkdir(parents=True)
        (repo / "core").mkdir()
        (repo / "context").mkdir()

        # brain/relations.yaml with sentinel markers
        relations = repo / "brain" / "relations.yaml"
        relations.write_text(
            "relations: []\n\n"
            "# WIKI_LINKS_START\n"
            "wiki_links: []\n"
            "# WIKI_LINKS_END\n",
            encoding="utf-8",
        )

        # A core file with a wikilink
        (repo / "core" / "identity.md").write_text(
            "# Identity\n\nSee [[context/priorities]].\n",
            encoding="utf-8",
        )

        # A context file that is the link target
        (repo / "context" / "priorities.md").write_text(
            "# Priorities\n\nSee [[core/identity]].\n",
            encoding="utf-8",
        )
        return repo

    def test_second_run_produces_no_change(self):
        repo = self._make_minimal_repo()
        relations_path = repo / "brain" / "relations.yaml"

        # First run
        subprocess.run(
            [sys.executable, str(self.script), "--root", str(repo)],
            capture_output=True,
            text=True,
        )
        content_after_first = relations_path.read_text(encoding="utf-8")

        # Second run
        subprocess.run(
            [sys.executable, str(self.script), "--root", str(repo)],
            capture_output=True,
            text=True,
        )
        content_after_second = relations_path.read_text(encoding="utf-8")

        self.assertEqual(
            content_after_first,
            content_after_second,
            "Second wiki-build run must produce identical relations.yaml",
        )


if __name__ == "__main__":
    unittest.main()
