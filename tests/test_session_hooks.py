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

    def _build_log_body(self, entries: list[tuple[str, list[str]]]) -> str:
        """Render a log body from (iso-date, [body lines]) tuples.

        Each tuple becomes a `### <date> ...` heading plus its body lines.
        Mirrors the entry format the fresh-install gate looks for.
        """
        out = ["# Brain log", ""]
        for idx, (iso, lines) in enumerate(entries):
            out.append(f"### {iso} entry-{idx:03d}")
            out.extend(lines)
            out.append("")
        return "\n".join(out) + "\n"

    def _seasoned_log_entries(
        self,
        today,
        *,
        count: int = 12,
        span_days: int = 45,
    ) -> list[tuple[str, list[str]]]:
        """Build a log spanning >= 30 days with >= 10 entries.

        Default is 12 entries spread across 45 days, which clears both gates
        (entries >= 10, span >= 30).
        """
        from datetime import timedelta
        entries: list[tuple[str, list[str]]] = []
        # Earliest first so min(date) maths is obvious.
        earliest = today - timedelta(days=span_days)
        # Spread `count` entries linearly between earliest and today.
        for i in range(count):
            offset = (span_days * i) // max(count - 1, 1)
            d = (earliest + timedelta(days=offset)).isoformat()
            entries.append((d, [f"- log-{d}-{i:03d} routine work"]))
        return entries

    def test_tip_omitted_on_fresh_install_empty_log(self) -> None:
        """Fresh install (empty log, no state) must omit the Tip line.

        v1.20.0 surfaced a Tip on day 1, contradicting the plan's intent of
        only pitching capabilities to operators with enough history that the
        pitch can match current state. v1.20.1 gates Tip on >= 10 entries
        AND >= 30 days of span.
        """
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), "# Brain log\n")
            output = self._run_hook(hook)
            self.assertIn("=== end brief ===", output)
            self.assertNotIn(
                "Tip:",
                output,
                "Tip must be omitted on fresh install (empty log).",
            )

    def test_tip_omitted_when_log_under_ten_entries(self) -> None:
        """Log with < 10 entries (regardless of span) omits Tip."""
        from datetime import date, timedelta
        today = date.today()
        # Five entries spread across 60 days. Span passes, count fails.
        entries = []
        for i in range(5):
            d = (today - timedelta(days=60 - i * 12)).isoformat()
            entries.append((d, [f"- log-{d}-{i:03d} sparse work"]))
        body = self._build_log_body(entries)
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), body)
            output = self._run_hook(hook)
            self.assertIn("=== end brief ===", output)
            self.assertNotIn(
                "Tip:",
                output,
                "Tip must be omitted when log has fewer than 10 entries.",
            )

    def test_tip_omitted_when_all_capabilities_recently_used(self) -> None:
        """Seasoned log but every capability touched within 14 days => no tip."""
        from datetime import date, timedelta
        today = date.today()
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
        # Seasoned base log: 10 routine entries spanning 35 days. Plus a
        # recent entry (yesterday) where every capability is mentioned, so
        # the per-capability "last used" is within 14 days.
        entries = self._seasoned_log_entries(today, count=10, span_days=35)
        recent = (today - timedelta(days=1)).isoformat()
        recent_lines = [f"- log-{recent}-{i:03d} #used:{cap} did the thing"
                        for i, cap in enumerate(capabilities)]
        entries.append((recent, recent_lines))
        body = self._build_log_body(entries)
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), body)
            output = self._run_hook(hook)
            self.assertIn("=== end brief ===", output)
            self.assertNotIn(
                "Tip:",
                output,
                "Tip must be omitted when every capability was used in the "
                "last 14 days, even if the log is seasoned.",
            )

    def test_tip_surfaces_when_log_seasoned_and_capability_idle(self) -> None:
        """Seasoned log + a capability not used in 14+ days => Tip surfaces."""
        from datetime import date
        today = date.today()
        # Seasoned log with no capability mentions => every capability is
        # "never used", but the gate passes so they count as eligible.
        entries = self._seasoned_log_entries(today, count=12, span_days=45)
        body = self._build_log_body(entries)
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), body)
            output = self._run_hook(hook)
            tip_lines = [line for line in output.splitlines()
                         if line.startswith("Tip:")]
            self.assertEqual(
                len(tip_lines),
                1,
                "Exactly one Tip line is expected when log is seasoned and "
                "an eligible capability exists.",
            )
            tip = tip_lines[0]
            # Natural-language phrasing: never slash-command-first, never the
            # frequency-of-use anti-pattern.
            self.assertNotRegex(
                tip,
                r"^Tip:\s*/",
                "Tip line must not lead with a slash command.",
            )
            self.assertNotRegex(
                tip,
                r"You haven't run",
                "Tip must use the natural-language pattern, not the "
                "frequency-of-use anti-pattern.",
            )
            self.assertRegex(
                tip,
                r'"[^"]+"',
                "Tip should contain a quoted natural-language phrase the "
                "operator can say to Claude.",
            )


if __name__ == "__main__":
    unittest.main()
