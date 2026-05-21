"""
Byte-parity test for templates/scripts/ vs scripts/.

Every .py file in templates/scripts/ that has a matching name in scripts/
must be byte-identical. After v1.27 F38 consolidated the wiki-layer walk
into scripts/_common.py, no per-script parity comment is needed and the
allow-list is empty - strict byte equality applies.

When this test fails, the diff is printed in the failure message so the drift
is obvious. Fresh-install bugs in v1.25.2 traced back to silent drift between
these pairs; this test prevents recurrence.
"""
import difflib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LIVE_DIR = REPO_ROOT / "scripts"
TEMPLATE_DIR = REPO_ROOT / "templates" / "scripts"

# Strict byte equality. No exceptions after v1.27 F38.
ALLOWED_LINE_DIFFS: dict[str, set[int]] = {}


class TemplateScriptsParityTests(unittest.TestCase):
    """Every script in templates/scripts/ that exists in scripts/ must match byte-for-byte
    (with one whitelisted line for the parity comment in wiki-build.py)."""

    def test_all_template_scripts_match_live(self):
        template_pys = sorted(TEMPLATE_DIR.glob("*.py"))
        self.assertGreater(len(template_pys), 0, "no .py files found under templates/scripts/")

        for template_path in template_pys:
            name = template_path.name
            live_path = LIVE_DIR / name
            with self.subTest(script=name):
                self.assertTrue(
                    live_path.exists(),
                    f"{name} exists in templates/scripts/ but not in scripts/ — "
                    f"every template helper must have a live counterpart.",
                )
                template_bytes = template_path.read_bytes()
                live_bytes = live_path.read_bytes()

                if template_bytes == live_bytes:
                    continue

                allowed = ALLOWED_LINE_DIFFS.get(name, set())
                template_lines = template_bytes.decode("utf-8").splitlines(keepends=True)
                live_lines = live_bytes.decode("utf-8").splitlines(keepends=True)
                self.assertEqual(
                    len(template_lines),
                    len(live_lines),
                    f"{name}: line count differs between live and template",
                )

                offending = []
                for idx, (t_line, l_line) in enumerate(zip(template_lines, live_lines), start=1):
                    if t_line != l_line and idx not in allowed:
                        offending.append((idx, t_line.rstrip("\n"), l_line.rstrip("\n")))

                if offending:
                    diff = "\n".join(
                        difflib.unified_diff(
                            live_lines,
                            template_lines,
                            fromfile=f"scripts/{name}",
                            tofile=f"templates/scripts/{name}",
                            lineterm="",
                        )
                    )
                    msg_lines = [
                        f"{name}: {len(offending)} line(s) drift between live and template:",
                    ]
                    for idx, t_line, l_line in offending[:5]:
                        msg_lines.append(f"  line {idx}:")
                        msg_lines.append(f"    live:     {l_line}")
                        msg_lines.append(f"    template: {t_line}")
                    msg_lines.append("Full diff:")
                    msg_lines.append(diff)
                    self.fail("\n".join(msg_lines))

    def test_all_live_scripts_present_in_template(self):
        """Every helper script in scripts/ that is part of the user-facing payload
        must be mirrored in templates/scripts/. Hard-coded list because not every
        script in scripts/ is part of the fresh-install payload (some are repo-internal)."""
        required_in_template = {
            "_common.py",
            "brain-pass-log.py",
            "brain-snapshot.py",
            "check-brand-voice-ready.py",
            "check-identity-ready.py",
            "check-log-has-history.py",
            "check-private-names.py",
            "check-voice-ready.py",
            "list-brands.py",
            "memory-diff.py",
            "menu.py",
            "observation-rollup.py",
            "query.py",
            "user-prompt-capture.py",
            "wiki-build.py",
        }
        present = {p.name for p in TEMPLATE_DIR.glob("*.py")}
        missing = required_in_template - present
        self.assertFalse(
            missing,
            f"templates/scripts/ is missing required helpers: {sorted(missing)}",
        )


if __name__ == "__main__":
    unittest.main()
