import os
import shutil
import subprocess
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


if __name__ == "__main__":
    unittest.main()
