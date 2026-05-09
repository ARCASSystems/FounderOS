import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_ROOT = REPO_ROOT / ".claude" / "hooks"
SESSION_BASH_HOOKS = [
    HOOK_ROOT / "session-start-brief.sh",
    HOOK_ROOT / "session-close-revenue-check.sh",
]
SESSION_POWERSHELL_HOOKS = [
    HOOK_ROOT / "session-start-brief.ps1",
    HOOK_ROOT / "session-close-revenue-check.ps1",
]
SESSION_START_HOOK = HOOK_ROOT / "session-start-brief.sh"




def bash_path(bash: str, path: Path) -> str:
    if os.name != "nt":
        return str(path)
    env = os.environ.copy()
    env["TARGET_PATH"] = str(path)
    # WSLENV with /p tells the WSL launcher to translate the Windows path into
    # POSIX form (/mnt/c/...) when bash reads $TARGET_PATH. Without it, an env
    # var set on the Windows side does not cross into WSL bash; the variable
    # arrives empty and the probe returns "." (its cwd), which then fails as a
    # non-existent script path. Has no effect on git-bash.
    existing = env.get("WSLENV", "")
    env["WSLENV"] = "TARGET_PATH/p" + (":" + existing if existing else "")
    probe = subprocess.run(
        [
            bash,
            "-lc",
            'if command -v cygpath >/dev/null 2>&1; then '
            'cygpath -u "$TARGET_PATH"; '
            'else echo "$TARGET_PATH"; fi',
        ],
        text=True,
        capture_output=True,
        env=env,
    )
    converted = probe.stdout.strip()
    if probe.returncode == 0 and converted and converted != ".":
        return converted
    # Last-resort manual conversion. WSL bash lives at C:\Windows\System32\
    # bash.exe and reads /mnt/<drive>/; git-bash and MSYS2 use /<drive>/.
    path_text = str(path)
    if len(path_text) > 2 and path_text[1] == ":":
        drive = path_text[0].lower()
        rest = path_text[3:].replace("\\", "/")
        if "system32" in bash.lower():
            return f"/mnt/{drive}/{rest}"
        return f"/{drive}/{rest}"
    return path_text

def powershell_bin() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def powershell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class SessionHookSmokeTests(unittest.TestCase):
    def test_bash_session_hooks_parse(self) -> None:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is not on PATH")

        for hook in SESSION_BASH_HOOKS:
            with self.subTest(hook=hook.name):
                result = subprocess.run(
                    [bash, "-n", bash_path(bash, hook)],
                    text=True,
                    capture_output=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)

    def test_powershell_session_hooks_parse(self) -> None:
        ps = powershell_bin()
        if not ps:
            self.skipTest("PowerShell is not on PATH")

        for hook in SESSION_POWERSHELL_HOOKS:
            with self.subTest(hook=hook.name):
                hook_literal = powershell_single_quote(str(hook))
                command = "\n".join(
                    [
                        "$tokens = $null",
                        "$errors = $null",
                        f"[System.Management.Automation.Language.Parser]::ParseFile({hook_literal}, [ref]$tokens, [ref]$errors) | Out-Null",
                        "if ($errors.Count -gt 0) {",
                        "  $errors | ForEach-Object { Write-Output $_.Message }",
                        "  exit 1",
                        "}",
                    ]
                ) + "\n"
                result = subprocess.run(
                    [ps, "-NoProfile", "-Command", command],
                    text=True,
                    capture_output=True,
                )

                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class SessionStartTipTests(unittest.TestCase):
    """Tests for the v1.20 SessionStart Tip line.

    The tip rotates a natural-language hint about an underused capability.
    Surfaces only when there is at least one capability not invoked in 14+ days.
    Omitted entirely when no eligible tip exists (no fresh-install false
    positive).
    """

    def _make_install(self, tmp: Path, log_body: str) -> Path:
        """Build a minimal Founder OS install layout the hook will accept."""
        (tmp / "core").mkdir(parents=True)
        (tmp / "brain").mkdir(parents=True)
        (tmp / ".claude" / "hooks").mkdir(parents=True)
        # Hook bails out if core/identity.md is missing.
        (tmp / "core" / "identity.md").write_text("# identity\n", encoding="utf-8")
        (tmp / "brain" / "log.md").write_text(log_body, encoding="utf-8")
        # Copy the hook script into the synthetic repo so its path resolution
        # ($REPO/../..) lands on tmp.
        target = tmp / ".claude" / "hooks" / "session-start-brief.sh"
        target.write_bytes(SESSION_START_HOOK.read_bytes())
        return target

    def _run_hook(self, hook_path: Path) -> str:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is not on PATH")
        result = subprocess.run(
            [bash, bash_path(bash, hook_path)],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_tip_present_when_no_recent_invocations(self) -> None:
        """Empty log => every capability is "never used" => tip surfaces."""
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), "# Brain log\n")
            output = self._run_hook(hook)
            self.assertIn("Tip:", output)
            # Tip uses natural-language phrasing, never slash-command-first.
            tip_line = next(
                (line for line in output.splitlines() if line.startswith("Tip:")),
                "",
            )
            self.assertNotRegex(
                tip_line,
                r"^Tip:\s*/",
                "Tip line must not lead with a slash command",
            )
            self.assertNotRegex(
                tip_line,
                r"You haven't run",
                "Tip must use the natural-language pattern, not the "
                "frequency-of-use anti-pattern",
            )

    def test_tip_omitted_when_all_capabilities_recently_used(self) -> None:
        """Every capability touched within the last day => no eligible tip."""
        # Use yesterday so the hook's "today" math is stable across runs.
        from datetime import date, timedelta
        recent = (date.today() - timedelta(days=1)).isoformat()
        capabilities = [
            "decision-framework",
            "priority-triage",
            "forcing-questions",
            "weekly-review",
            "audit",
            "brain-pass",
            "knowledge-capture",
            "ingest",
            "bottleneck-diagnostic",
            "strategic-analysis",
        ]
        body_lines = [f"## {recent}", ""]
        for cap in capabilities:
            body_lines.append(f"- log-{recent}-001 #used:{cap} did the thing")
        body = "\n".join(body_lines) + "\n"
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), body)
            output = self._run_hook(hook)
            # Brief still renders end markers, just no Tip line.
            self.assertIn("=== end brief ===", output)
            self.assertNotIn(
                "Tip:",
                output,
                "Tip line must be omitted when all capabilities used within "
                "the last 14 days",
            )

    def test_tip_uses_natural_language_phrasing(self) -> None:
        """The tip must lead with a natural-language phrase, not a command."""
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), "# Brain log\n")
            output = self._run_hook(hook)
            tip_lines = [line for line in output.splitlines() if line.startswith("Tip:")]
            self.assertEqual(
                len(tip_lines),
                1,
                "Exactly one Tip line is expected when eligible",
            )
            tip = tip_lines[0]
            # Pattern: contains a quoted natural-language phrase.
            self.assertRegex(
                tip,
                r'"[^"]+"',
                "Tip should contain a quoted natural-language phrase the "
                "operator can say to Claude",
            )


if __name__ == "__main__":
    unittest.main()
