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
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "user-prompt-capture.py"


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
        prompt = "I had a call with Aqsa this morning about the new role."
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


if __name__ == "__main__":
    unittest.main()
