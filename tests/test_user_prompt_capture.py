"""Tests for scripts/user-prompt-capture.py - the v1.23 UserPromptSubmit hook.

Unit tests load detection functions via importlib (the script has a hyphen
in its name so a plain `import` does not work). End-to-end tests drive the
script through subprocess with a JSON envelope on stdin and assert against
disk state plus stdout.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "user-prompt-capture.py"
HOOK_BASH = REPO_ROOT / ".claude" / "hooks" / "user-prompt-capture.sh"
HOOK_POWERSHELL = REPO_ROOT / ".claude" / "hooks" / "user-prompt-capture.ps1"


def _powershell_bin() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _bash_is_windows_shell() -> bool:
    """Probe bash for MINGW*/MSYS*/CYGWIN* uname.

    The bash wrapper exits 0 immediately on Windows shells (the PowerShell
    variant is canonical there). Invocation tests need to know whether to
    expect output or a silent platform-guard exit.
    """
    bash = shutil.which("bash")
    if not bash:
        return False
    try:
        result = subprocess.run(
            [bash, "-c", "uname -s"],
            text=True,
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode != 0:
        return False
    return result.stdout.strip().upper().startswith(("MINGW", "MSYS", "CYGWIN"))


BASH_WRAPPER_MUTED = _bash_is_windows_shell()


def _bash_is_wsl() -> bool:
    """Probe bash for the WSL kernel marker.

    WSL2 bash uname -r contains 'microsoft' in the kernel version string.
    WSL bash cannot read Windows-mounted paths reliably during these
    wrapper tests, so the affected cases are skipped on WSL.
    """
    bash = shutil.which("bash")
    if not bash:
        return False
    try:
        result = subprocess.run(
            [bash, "-c", "uname -r"],
            text=True,
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode != 0:
        return False
    return "microsoft" in result.stdout.lower()


BASH_IS_WSL = _bash_is_wsl()


def _load_module():
    spec = importlib.util.spec_from_file_location("user_prompt_capture", SCRIPT)
    assert spec is not None and spec.loader is not None, "could not load capture script"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UPC = _load_module()


def _make_install(tmp: Path) -> Path:
    """Build a minimal Founder OS install layout the script will accept.

    The find_repo_root() guard requires CLAUDE.md OR core/identity.md to
    exist. We ship CLAUDE.md so the script proceeds past the guard.
    """
    repo = tmp / "founder-os"
    repo.mkdir()
    (repo / "CLAUDE.md").write_text("# Founder OS\n", encoding="utf-8")
    (repo / "brain" / "rants").mkdir(parents=True)
    return repo


def _run_capture(repo: Path, prompt: str | None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(repo)
    if prompt is None:
        stdin = ""
    else:
        stdin = json.dumps({"prompt": prompt})
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=stdin,
        text=True,
        capture_output=True,
        env=env,
    )


# ---------------------------------------------------------------------------
# detect_shape unit tests
# ---------------------------------------------------------------------------


class DetectShapeTests(unittest.TestCase):
    def test_short_question_returns_none(self):
        self.assertIsNone(UPC.detect_shape("What is the weather today?"))

    def test_preference_phrase_returns_preference(self):
        self.assertEqual(
            UPC.detect_shape("From now on never ask me before logging a meeting."),
            "preference",
        )

    def test_status_update_returns_status_update(self):
        self.assertEqual(
            UPC.detect_shape("I just finished the proposal for the new client."),
            "status-update",
        )

    def test_named_entity_with_meeting_verb_returns_named_entity(self):
        prompt = "I had a call with Sarah this morning about the new role."
        self.assertEqual(UPC.detect_shape(prompt), "named-entity")

    def test_long_first_person_dump_returns_rant(self):
        body = (
            "I am so tired of this nonsense. Every single day I sit down "
            "and try to make progress on the OS and something blocks me. "
            "I cannot keep working like this. I am frustrated and exhausted. "
        ) * 8  # ~1500 chars, well above 800 threshold
        self.assertEqual(UPC.detect_shape(body), "rant")

    def test_empty_prompt_returns_none(self):
        self.assertIsNone(UPC.detect_shape(""))
        self.assertIsNone(UPC.detect_shape("   "))


# ---------------------------------------------------------------------------
# Named-entity stop-list + proximity tests (the M2 fix)
# ---------------------------------------------------------------------------


class NamedEntityFilterTests(unittest.TestCase):
    def test_stop_list_word_does_not_fire(self):
        """'I just called Python from my bash script' must not trigger."""
        prompt = "I just called Python from my bash script and it worked."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_brand_name_near_meeting_verb_does_not_fire(self):
        """'I had a call with Notion's API team' must not trigger."""
        prompt = "I had a call with Notion about their API limits."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_day_of_week_does_not_fire(self):
        prompt = "I called Monday morning to confirm the order."
        # Monday is in the stop-list; no other candidate name nearby.
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_real_name_near_verb_does_fire(self):
        """A real name near a meeting verb still fires."""
        prompt = "I had a call with Ahmed about logistics in Sharjah."
        self.assertEqual(UPC.detect_shape(prompt), "named-entity")

    def test_kinship_term_does_not_fire(self):
        """'I just called Mom yesterday' must not trigger a contact-capture."""
        for prompt in [
            "I just called Mom yesterday morning.",
            "I called Dad to confirm the time.",
            "I had a call with my Brother about the family business.",
        ]:
            self.assertIsNone(
                UPC.detect_shape(prompt),
                f"kinship term should not fire: {prompt!r}",
            )

    def test_department_name_does_not_fire(self):
        """Common internal-department names must not trigger."""
        for prompt in [
            "I spoke to Marketing yesterday about the campaign.",
            "I called Sales this morning to confirm pricing.",
            "I had a call with Engineering about the regression.",
        ]:
            self.assertIsNone(
                UPC.detect_shape(prompt),
                f"department name should not fire: {prompt!r}",
            )

    def test_holiday_or_occasion_does_not_fire(self):
        """'We met during Ramadan' is temporal context, not a meeting partner."""
        for prompt in [
            "We met during Ramadan last year.",
            "I called everyone before Christmas to wrap up.",
        ]:
            self.assertIsNone(
                UPC.detect_shape(prompt),
                f"holiday/occasion should not fire: {prompt!r}",
            )

    def test_name_far_from_verb_does_not_fire(self):
        """A capitalized word that is not near any meeting verb does not fire."""
        # Verb at start, name appears 200+ chars later in unrelated context.
        prompt = (
            "I called the office today. " + ("Some filler text. " * 20) +
            "Yesterday I read about Stephen Hawking's last paper."
        )
        # "called" near the start, "Stephen" far away, no other valid name nearby.
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_sentence_initial_verb_not_treated_as_name(self):
        """A capitalized meeting verb at sentence start (Called/Met/Spoke/
        Emailed/Messaged) overlaps the meeting-verb match on the same span.
        The candidate IS the verb, not a person name. Overlap rejection
        must skip these candidates."""
        for prompt in [
            "Called Mom yesterday.",
            "Called Engineering this morning.",
            "Met Finance about the budget.",
            "Spoke to Legal about the contract.",
            "Emailed Support about the bug.",
            "Messaged Product about the spec.",
        ]:
            self.assertIsNone(
                UPC.detect_shape(prompt),
                f"sentence-initial capitalized verb should not fire: {prompt!r}",
            )

    def test_may_is_treated_as_month(self):
        """'May' as a month name must not fire as a person mention."""
        prompt = "I met in May to discuss the offer."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_camelcase_brand_does_not_fire(self):
        """CamelCase brands ('GitHub', 'OpenAI', 'YouTube') must capture as
        a single token and resolve against the case-insensitive stop-list."""
        for prompt in [
            "I had a call with GitHub about repo limits.",
            "I emailed OpenAI about their API.",
            "I had a call with YouTube about my channel.",
        ]:
            self.assertIsNone(
                UPC.detect_shape(prompt),
                f"CamelCase brand should not fire: {prompt!r}",
            )

    def test_all_caps_acronym_does_not_fire(self):
        """All-caps acronyms (API, USA, UAE, JSON) are structurally excluded
        from candidate names by the regex's mandatory-lowercase lookahead."""
        for prompt in [
            "I had a call with JSON about parsing.",
            "I emailed about the API endpoint.",
            "I called my contact at the UAE office.",
        ]:
            self.assertIsNone(
                UPC.detect_shape(prompt),
                f"all-caps acronym should not fire: {prompt!r}",
            )


# ---------------------------------------------------------------------------
# Three-signal architecture tests (v1.23.1 AND-gate)
# ---------------------------------------------------------------------------


class ThreeSignalArchitectureTests(unittest.TestCase):
    """Validates the v1.23.1 three-signal AND-gate (A: preposition-mandatory
    verb, B: tight 30-char name coupling, C: first-person token).

    Test #6 (Dubai Chamber) is a known architectural gap: the architecture
    cannot reliably distinguish a city+institutional-noun compound from a
    person's first+last name without NER. It is handled by stop-listing
    institutional head nouns and applying a next-word peek. The test asserts
    None and documents the gap explicitly so future reviewers understand the
    trade-off.
    """

    def test_bare_called_no_preposition_does_not_fire(self) -> None:
        """Signal A fails: `called` alone has no preposition anchor."""
        prompt = "I just called Python from my bash script and it worked."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_brand_stop_listed_does_not_fire(self) -> None:
        """A+B+C all fire but stop-list catches Notion."""
        prompt = "I had a call with Notion about their API limits."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_bare_called_kinship_does_not_fire(self) -> None:
        """Signal A fails: `called` alone, no preposition."""
        prompt = "I called Mom yesterday morning."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_department_stop_listed_does_not_fire(self) -> None:
        """A+B+C fire; stop-list catches Marketing."""
        prompt = "I spoke to Marketing this morning about the campaign."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_temporal_preposition_not_meeting_verb(self) -> None:
        """Signal A fails: `during` is not in the with/to/from verb set."""
        prompt = "We met during Ramadan last year."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_institutional_compound_does_not_fire(self) -> None:
        """Known gap: 'Dubai Chamber' is a compound institutional name.

        The architecture handles this via next-word peek: 'Chamber' is
        stop-listed as an institutional head noun, so 'Dubai' is rejected
        when 'Chamber' immediately follows it. This does not require NER.
        """
        prompt = "I had a call with Dubai Chamber about membership."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_wordpress_stop_listed_does_not_fire(self) -> None:
        """A+B+C fire; stop-list catches Wordpress."""
        prompt = "I had a call with WordPress support yesterday."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_cloudflare_stop_listed_does_not_fire(self) -> None:
        """A+B+C fire; stop-list catches Cloudflare."""
        prompt = "I had a call with CloudFlare last week."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_paypal_stop_listed_does_not_fire(self) -> None:
        """A+B+C fire; stop-list catches Paypal."""
        prompt = "I had a call with PayPal customer service."
        self.assertIsNone(UPC.detect_shape(prompt))

    def test_generic_name_ahmed_fires(self) -> None:
        """A+B+C fire; Ahmed not in stop-list."""
        prompt = "I had a call with Ahmed yesterday."
        self.assertEqual(UPC.detect_shape(prompt), "named-entity")

    def test_generic_name_sarah_spoke_to_fires(self) -> None:
        """A+B+C fire; Sarah not in stop-list."""
        prompt = "I spoke to Sarah about the Sharjah office."
        self.assertEqual(UPC.detect_shape(prompt), "named-entity")

    def test_got_reply_from_fires(self) -> None:
        """A: got a reply from; B: Bilal; C: I — all three fire."""
        prompt = "I got a reply from Bilal this morning."
        self.assertEqual(UPC.detect_shape(prompt), "named-entity")


# ---------------------------------------------------------------------------
# End-to-end script behaviour
# ---------------------------------------------------------------------------


class CaptureScriptE2ETests(unittest.TestCase):
    def test_slash_command_prompt_bypasses(self):
        """Prompts starting with '/' must not emit any suggestion."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_install(Path(tmp))
            result = _run_capture(repo, "/menu")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "")

    def test_no_install_exits_silently(self):
        """Script with no CLAUDE_PROJECT_DIR exits silent with no stdout."""
        env = os.environ.copy()
        env.pop("CLAUDE_PROJECT_DIR", None)
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps({"prompt": "I'm frustrated about this build."}),
            text=True,
            capture_output=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")

    def test_malformed_json_envelope_exits_silently(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_install(Path(tmp))
            env = os.environ.copy()
            env["CLAUDE_PROJECT_DIR"] = str(repo)
            result = subprocess.run(
                [sys.executable, str(SCRIPT)],
                input="{not valid json",
                text=True,
                capture_output=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "")

    def test_rant_eager_capture_writes_to_disk(self):
        body = (
            "I am drowning in context switches. Every time I try to ship one "
            "thing another one falls behind. I am exhausted and I don't know "
            "how to keep this pace. " * 6
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_install(Path(tmp))
            result = _run_capture(repo, body)
            self.assertEqual(result.returncode, 0, result.stderr)
            today = datetime.now().strftime("%Y-%m-%d")
            rant_file = repo / "brain" / "rants" / f"{today}.md"
            self.assertTrue(rant_file.exists(), "rant file should be created on disk")
            text = rant_file.read_text(encoding="utf-8")
            self.assertIn("processed: false", text)
            self.assertIn("mode: unknown", text)
            self.assertIn("source: user-prompt-capture-hook", text)
            self.assertIn("rant-eager-captured", result.stdout)
            # The note must reference the rant via a repo-relative path. An
            # absolute path leaks the operator's local filesystem layout
            # into model context on every rant.
            self.assertIn("brain/rants/", result.stdout)
            self.assertNotIn(str(repo), result.stdout)

    def test_rant_prepend_preserves_prior_entry(self):
        """A second rant on the same date prepends, keeping the first body."""
        body1 = "I am so frustrated about everything. " * 30
        body2 = "Different topic entirely. I am stuck on a different problem. " * 25
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_install(Path(tmp))
            _run_capture(repo, body1)
            _run_capture(repo, body2)
            today = datetime.now().strftime("%Y-%m-%d")
            text = (repo / "brain" / "rants" / f"{today}.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Different topic entirely", text)
            self.assertIn("frustrated about everything", text)
            # New entry appears before the old one (prepended).
            self.assertLess(
                text.find("Different topic entirely"),
                text.find("frustrated about everything"),
                "newer entry should be prepended above older entry",
            )

    def test_private_tag_block_is_stripped(self):
        body = (
            "I am drowning in context switches. Every day this happens. " * 20 +
            "<private>This part has my credit card number 1234.</private>"
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_install(Path(tmp))
            _run_capture(repo, body)
            today = datetime.now().strftime("%Y-%m-%d")
            text = (repo / "brain" / "rants" / f"{today}.md").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("credit card", text)
            self.assertNotIn("1234", text)

    def test_named_entity_suggestion_does_not_write(self):
        """Named-entity is suggest-only - no file should be written."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_install(Path(tmp))
            result = _run_capture(
                repo, "I had a call with Ahmed about the new logistics setup."
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("named-entity", result.stdout)
            # No rant file should be created for a named-entity shape.
            today = datetime.now().strftime("%Y-%m-%d")
            self.assertFalse(
                (repo / "brain" / "rants" / f"{today}.md").exists(),
                "named-entity should not eager-write to rants",
            )


# ---------------------------------------------------------------------------
# Hook wrapper coverage (.sh + .ps1).
#
# settings.json wires the UserPromptSubmit hook through these wrappers, not
# through python directly. Prior coverage only invoked the .py file, so a
# wrapper that failed to forward stdin or resolve the repo root would ship
# unnoticed.
# ---------------------------------------------------------------------------


class WrapperParseTests(unittest.TestCase):
    def test_bash_wrapper_exists_and_parses(self) -> None:
        self.assertTrue(HOOK_BASH.exists(), f"missing wrapper: {HOOK_BASH}")
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is not on PATH")
        result = subprocess.run(
            [bash, "-n", str(HOOK_BASH)],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_powershell_wrapper_exists_and_parses(self) -> None:
        self.assertTrue(
            HOOK_POWERSHELL.exists(), f"missing wrapper: {HOOK_POWERSHELL}"
        )
        ps = _powershell_bin()
        if not ps:
            self.skipTest("PowerShell is not on PATH")
        # Parse-only check via [scriptblock]::Create. Errors return non-zero.
        check = (
            "$null = [System.Management.Automation.Language.Parser]::ParseFile("
            f"'{HOOK_POWERSHELL.as_posix()}', [ref]$null, [ref]$null)"
        )
        result = subprocess.run(
            [ps, "-NoProfile", "-NonInteractive", "-Command", check],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


@unittest.skipIf(
    BASH_IS_WSL,
    "WSL bash cannot reach Windows paths; production uses Git Bash MINGW",
)
class WrapperInvocationTests(unittest.TestCase):
    """End-to-end smoke: pipe a rant body through the wrapper and verify
    the rant is written via the python script the wrapper invokes."""

    def _rant_body(self) -> str:
        return (
            "I am drowning in context switches. Every time I try to ship one "
            "thing another one falls behind. I am exhausted and I don't know "
            "how to keep this pace. " * 6
        )

    def test_bash_wrapper_invocation(self) -> None:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is not on PATH")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_install(Path(tmp))
            env = os.environ.copy()
            env["CLAUDE_PROJECT_DIR"] = str(repo)
            result = subprocess.run(
                [bash, str(HOOK_BASH)],
                input=json.dumps({"prompt": self._rant_body()}),
                text=True,
                capture_output=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            if BASH_WRAPPER_MUTED:
                # Platform guard fires on git-bash / WSL on Windows shells.
                self.assertEqual(result.stdout.strip(), "")
                return
            self.assertIn("rant-eager-captured", result.stdout)
            self.assertIn("brain/rants/", result.stdout)
            self.assertNotIn(str(repo), result.stdout)
            today = datetime.now().strftime("%Y-%m-%d")
            self.assertTrue(
                (repo / "brain" / "rants" / f"{today}.md").exists(),
                "wrapper should write rant file via the python script",
            )

    def test_powershell_wrapper_invocation(self) -> None:
        ps = _powershell_bin()
        if not ps:
            self.skipTest("PowerShell is not on PATH")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_install(Path(tmp))
            env = os.environ.copy()
            env["CLAUDE_PROJECT_DIR"] = str(repo)
            result = subprocess.run(
                [
                    ps,
                    "-NoProfile",
                    "-NonInteractive",
                    "-File",
                    str(HOOK_POWERSHELL),
                ],
                input=json.dumps({"prompt": self._rant_body()}),
                text=True,
                capture_output=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("rant-eager-captured", result.stdout)
            self.assertIn("brain/rants/", result.stdout)
            self.assertNotIn(str(repo), result.stdout)
            today = datetime.now().strftime("%Y-%m-%d")
            self.assertTrue(
                (repo / "brain" / "rants" / f"{today}.md").exists(),
                "wrapper should write rant file via the python script",
            )


if __name__ == "__main__":
    unittest.main()
