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


def _bash_is_mingw_or_msys() -> bool:
    """Probe bash for its uname -s output.

    The bash session-start hook exits early on MINGW*/MSYS*/CYGWIN* by design
    because the PowerShell variant is the canonical writer on Windows. When the
    bash hook is muted by the platform guard, tip-and-brief assertions made
    against bash stdout cannot pass. Skip the bash-hook-output suite in that
    environment; the PowerShell parse smoke-test still covers the .ps1 variant.
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
    name = result.stdout.strip().upper()
    return name.startswith(("MINGW", "MSYS", "CYGWIN"))


BASH_HOOK_MUTED_BY_PLATFORM_GUARD = _bash_is_mingw_or_msys()


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


@unittest.skipIf(
    BASH_HOOK_MUTED_BY_PLATFORM_GUARD,
    "bash session-start hook exits early on MINGW/MSYS/CYGWIN by design "
    "(PowerShell .ps1 is the canonical writer on Windows). Tip-output "
    "assertions need a bash where the platform guard does not fire.",
)
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
        recent_lines = [f"- log-{recent}-{i:03d} #used-{cap} did the thing"
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

    def test_tip_ignores_untagged_planning_mentions(self) -> None:
        """A line saying to run a capability later is not a use."""
        from datetime import date, timedelta
        today = date.today()
        capabilities = [
            "decision-framework",
            "priority-triage",
            "forcing-questions",
            "weekly-review",
            "brain-pass",
            "knowledge-capture",
            "ingest",
            "bottleneck-diagnostic",
            "strategic-analysis",
        ]
        entries = self._seasoned_log_entries(today, count=10, span_days=35)
        recent = (today - timedelta(days=1)).isoformat()
        recent_lines = [f"- log-{recent}-{i:03d} #used-{cap} did the thing"
                        for i, cap in enumerate(capabilities)]
        recent_lines.append("- I should run audit later when I have time.")
        entries.append((recent, recent_lines))
        body = self._build_log_body(entries)
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), body)
            output = self._run_hook(hook)
            self.assertIn('Tip: Say "audit the OS"', output)

    def test_tip_counts_acted_tag_with_capability_name(self) -> None:
        """#acted lines count only when they name the capability."""
        from datetime import date, timedelta
        today = date.today()
        entries = self._seasoned_log_entries(today, count=12, span_days=45)
        recent = (today - timedelta(days=1)).isoformat()
        entries.append((recent, ["- #acted audit completed the weekly check."]))
        body = self._build_log_body(entries)
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_install(Path(tmp), body)
            output = self._run_hook(hook)
            self.assertIn("=== end brief ===", output)


@unittest.skipIf(
    BASH_HOOK_MUTED_BY_PLATFORM_GUARD,
    "bash session-start hook exits early on MINGW/MSYS/CYGWIN by design "
    "(PowerShell .ps1 is the canonical writer on Windows). Rollup-output "
    "assertions need a bash where the platform guard does not fire.",
)
class SessionStartObservationRollupTests(unittest.TestCase):
    """Tests for the v1.22 W4 observation-rollup section of the SessionStart brief.

    The hook must:
      1. Report the current count of weekly rollup summaries.
      2. Surface a nudge when JSONL files older than 10 days exist AND
         observations are enabled.
    Regression target: passing a Git Bash POSIX path (/c/...) to a Windows
    Python interpreter must still produce correct glob results.
    """

    def _make_install(self, tmp: Path) -> Path:
        (tmp / "core").mkdir(parents=True)
        (tmp / "brain" / "observations" / "_rollups").mkdir(parents=True)
        (tmp / ".claude" / "hooks").mkdir(parents=True)
        (tmp / "core" / "identity.md").write_text("# identity\n", encoding="utf-8")
        target = tmp / ".claude" / "hooks" / "session-start-brief.sh"
        target.write_bytes(SESSION_START_HOOK.read_bytes())
        return target

    def _run_hook(self, hook_path: Path) -> str:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is not on PATH")
        env = os.environ.copy()
        env["FOUNDER_OS_OBSERVATIONS"] = "1"
        if os.name == "nt":
            existing = env.get("WSLENV", "")
            env["WSLENV"] = "FOUNDER_OS_OBSERVATIONS" + (":" + existing if existing else "")
        result = subprocess.run(
            [bash, bash_path(bash, hook_path)],
            text=True,
            capture_output=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_rollup_count_reported_when_enabled(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            hook = self._make_install(tmp)
            # Drop two rollup files so the count is non-zero
            (tmp / "brain" / "observations" / "_rollups" / "2026-W15.md").write_text("rollup\n")
            (tmp / "brain" / "observations" / "_rollups" / "2026-W16.md").write_text("rollup\n")
            out = self._run_hook(hook)
            self.assertIn("Observations: enabled", out)
            self.assertIn("Rollups: 2", out)

    def test_stale_jsonl_nudge_fires(self):
        """Old JSONLs must surface the rollup nudge - regression for Windows path bug."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            hook = self._make_install(tmp)
            from datetime import date, timedelta
            today = date.today()
            # 3 files older than 10 days
            for offset in (15, 20, 30):
                stale = today - timedelta(days=offset)
                (tmp / "brain" / "observations" / f"{stale.isoformat()}.jsonl").write_text("{}\n")
            out = self._run_hook(hook)
            self.assertIn("older than 10 days", out,
                          f"Stale-JSONL nudge must fire when observations enabled. Got:\n{out}")
            self.assertIn("roll up observations", out)

    def test_no_nudge_when_jsonls_are_fresh(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            hook = self._make_install(tmp)
            from datetime import date
            (tmp / "brain" / "observations" / f"{date.today().isoformat()}.jsonl").write_text("{}\n")
            out = self._run_hook(hook)
            self.assertNotIn("older than 10 days", out)


class PowerShellComplianceInitOrderTests(unittest.TestCase):
    """F21 regression: $todayDt must be initialized before the compliance block.

    Before the fix, $todayDt was initialized at the Review Due section (near
    the bottom of the script) while the compliance block referenced it near
    the top. PowerShell silently treats uninitialized vars as $null, so the
    compliance entries never surfaced for Windows users.
    """

    @classmethod
    def setUpClass(cls):
        cls.ps = powershell_bin()

    def _skip_if_no_ps(self):
        if not self.ps:
            self.skipTest("PowerShell (pwsh/powershell) is not on PATH")

    def _make_ps_install(self, tmp: Path) -> Path:
        (tmp / "core").mkdir(parents=True)
        (tmp / "context").mkdir(parents=True)
        (tmp / "brain").mkdir(parents=True)
        (tmp / ".claude" / "hooks").mkdir(parents=True)
        (tmp / "core" / "identity.md").write_text("# identity\n", encoding="utf-8")
        target = tmp / ".claude" / "hooks" / "session-start-brief.ps1"
        hook_src = REPO_ROOT / ".claude" / "hooks" / "session-start-brief.ps1"
        target.write_bytes(hook_src.read_bytes())
        return target

    def _run_ps_hook(self, hook_path: Path) -> str:
        result = subprocess.run(
            [self.ps, "-NoProfile", "-File", str(hook_path)],
            text=True,
            capture_output=True,
        )
        return result.stdout + result.stderr

    def test_compliance_overdue_surfaces_in_output(self):
        """An overdue compliance entry must appear in the SessionStart output."""
        self._skip_if_no_ps()
        from datetime import date, timedelta
        today = date.today()
        overdue_date = (today - timedelta(days=5)).isoformat()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            hook = self._make_ps_install(tmp)
            compliance_content = (
                f"## {overdue_date} - Test overdue filing\n"
                f"- Status: OPEN\n"
                f"- Details: This entry is overdue by 5 days.\n"
            )
            (tmp / "context" / "compliance.md").write_text(compliance_content, encoding="utf-8")
            output = self._run_ps_hook(hook)
            self.assertIn(
                "OVERDUE",
                output,
                f"Overdue compliance entry must surface in output.\nGot:\n{output}",
            )

    def test_compliance_upcoming_surfaces_in_output(self):
        """An upcoming compliance entry (due today) must appear in the output."""
        self._skip_if_no_ps()
        from datetime import date, timedelta
        today = date.today()
        upcoming_date = (today + timedelta(days=10)).isoformat()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            hook = self._make_ps_install(tmp)
            compliance_content = (
                f"## {upcoming_date} - Test upcoming filing\n"
                f"- Status: OPEN\n"
                f"- Details: This entry is due in 10 days.\n"
            )
            (tmp / "context" / "compliance.md").write_text(compliance_content, encoding="utf-8")
            output = self._run_ps_hook(hook)
            self.assertIn(
                "deadline",
                output.lower(),
                f"Upcoming compliance entry (within 30 days) must surface in output.\nGot:\n{output}",
            )

    def test_no_compliance_output_when_file_missing(self):
        """When context/compliance.md does not exist, the hook must not error."""
        self._skip_if_no_ps()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            hook = self._make_ps_install(tmp)
            output = self._run_ps_hook(hook)
            self.assertIn(
                "=== end brief ===",
                output,
                "Hook must complete cleanly even without compliance.md",
            )
            self.assertNotIn("OVERDUE", output)


class WelcomeBannerTests(unittest.TestCase):
    """Tests for the v1.23 SessionStart welcome banner.

    The banner fires when core/identity.md is missing AND a Founder OS
    marker is present (one of: templates/bootloader-claude-md.md,
    .claude/settings.json, or CLAUDE.md). Closes the silent-Day-0 failure
    where a fresh install saw nothing on first session open.
    """

    def _make_pre_setup_install(self, tmp: Path, marker: str) -> Path:
        """Build a layout that looks like a fresh install pre-setup.

        Marker selects which Founder OS signal exists:
          - "claude_md": CLAUDE.md at repo root
          - "bootloader": templates/bootloader-claude-md.md
          - "settings_json": .claude/settings.json
        """
        (tmp / ".claude" / "hooks").mkdir(parents=True)
        if marker == "claude_md":
            (tmp / "CLAUDE.md").write_text("# Founder OS\n", encoding="utf-8")
        elif marker == "bootloader":
            (tmp / "templates").mkdir()
            (tmp / "templates" / "bootloader-claude-md.md").write_text(
                "# bootloader\n", encoding="utf-8"
            )
        elif marker == "settings_json":
            (tmp / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
        target = tmp / ".claude" / "hooks" / "session-start-brief.sh"
        target.write_bytes(SESSION_START_HOOK.read_bytes())
        return target

    def _run_hook(self, hook_path: Path) -> str:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is not on PATH")
        if _bash_is_mingw_or_msys():
            self.skipTest(
                "bash hook intentionally muted on MINGW/MSYS - PowerShell variant covers"
            )
        result = subprocess.run(
            [bash, bash_path(bash, hook_path)],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_banner_fires_when_identity_missing_and_claude_md_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._make_pre_setup_install(Path(tmp), "claude_md")
            out = self._run_hook(hook)
            self.assertIn("Welcome to Founder OS", out)
            self.assertIn("set up Founder OS", out)
            self.assertNotIn("=== end brief ===", out)

    def test_banner_does_not_fire_when_identity_present(self):
        """When core/identity.md exists, the banner block must be skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "core").mkdir()
            (root / "core" / "identity.md").write_text("# identity\n", encoding="utf-8")
            (root / "brain").mkdir()
            (root / "brain" / "log.md").write_text("# Brain log\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text("# Founder OS\n", encoding="utf-8")
            (root / ".claude" / "hooks").mkdir(parents=True)
            target = root / ".claude" / "hooks" / "session-start-brief.sh"
            target.write_bytes(SESSION_START_HOOK.read_bytes())
            out = self._run_hook(target)
            self.assertNotIn("Welcome to Founder OS", out)
            self.assertIn("=== end brief ===", out)


if __name__ == "__main__":
    unittest.main()
