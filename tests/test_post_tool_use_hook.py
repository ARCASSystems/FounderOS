import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_ROOT = REPO_ROOT / ".claude" / "hooks"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "hook-input"
BASH_HOOK = "post-tool-use-observation.sh"
POWERSHELL_HOOK = "post-tool-use-observation.ps1"

EXPECTED_INTENTS = {
    "edit.json": {
        "tool": "Edit",
        "file": "context/example.md",
        "intent": "edit context/example.md - Capture the next action before the meeting.",
    },
    "read.json": {
        "tool": "Read",
        "file": "context/example.md",
        "intent": "read context/example.md",
    },
    "bash.json": {
        "tool": "Bash",
        "file": "",
        "intent": "bash - python scripts/query.py \"outreach stalled\"",
    },
    "grep.json": {
        "tool": "Grep",
        "file": "",
        "intent": "grep stalled in brain",
    },
    "glob.json": {
        "tool": "Glob",
        "file": "",
        "intent": "glob brain/*.md",
    },
    "unknown.json": {
        "tool": "Inspect",
        "file": "",
        "intent": "Inspect",
    },
}


def powershell_bin() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def bash_bin() -> str | None:
    return shutil.which("bash")


def env_with_observations(value: str | None) -> dict[str, str]:
    env = os.environ.copy()
    if value is None:
        env.pop("FOUNDER_OS_OBSERVATIONS", None)
    else:
        env["FOUNDER_OS_OBSERVATIONS"] = value
    return env


@contextmanager
def temp_hook_repo(hook_name: str, block_observations: bool = False):
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        hook_dir = repo / ".claude" / "hooks"
        hook_dir.mkdir(parents=True)
        hook_path = hook_dir / hook_name
        shutil.copy2(HOOK_ROOT / hook_name, hook_path)

        if block_observations:
            brain_dir = repo / "brain"
            brain_dir.mkdir()
            (brain_dir / "observations").write_text("not a directory", encoding="utf-8")

        yield repo, hook_path


def observation_lines(repo: Path) -> list[str]:
    obs_dir = repo / "brain" / "observations"
    if not obs_dir.is_dir():
        return []
    lines: list[str] = []
    for path in sorted(obs_dir.glob("*.jsonl")):
        lines.extend(path.read_text(encoding="utf-8").splitlines())
    return lines


def observation_bytes(repo: Path) -> bytes:
    obs_dir = repo / "brain" / "observations"
    files = sorted(obs_dir.glob("*.jsonl")) if obs_dir.is_dir() else []
    if not files:
        return b""
    return files[0].read_bytes()


class PostToolUsePowerShellHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ps = powershell_bin()
        if not self.ps:
            self.skipTest("PowerShell is not on PATH")

    def run_hook(
        self,
        hook_path: Path,
        hook_input: str,
        observations: str | None = "1",
    ) -> subprocess.CompletedProcess[str]:
        env = env_with_observations(observations)
        return subprocess.run(
            [self.ps, "-NoProfile", "-File", str(hook_path)],
            input=hook_input,
            text=True,
            capture_output=True,
            env=env,
        )

    def test_gate_unset_writes_nothing(self) -> None:
        with temp_hook_repo(POWERSHELL_HOOK) as (repo, hook):
            result = self.run_hook(hook, (FIXTURE_ROOT / "read.json").read_text(), None)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(observation_lines(repo), [])

    def test_enabled_writes_utf8_without_bom_and_appends(self) -> None:
        payload = (FIXTURE_ROOT / "read.json").read_text(encoding="utf-8")

        with temp_hook_repo(POWERSHELL_HOOK) as (repo, hook):
            first = self.run_hook(hook, payload)
            second = self.run_hook(hook, payload)

            self.assertEqual(first.returncode, 0)
            self.assertEqual(second.returncode, 0)
            data = observation_bytes(repo)
            self.assertNotEqual(data[:3], b"\xef\xbb\xbf")

            lines = observation_lines(repo)
            self.assertEqual(len(lines), 2)
            for line in lines:
                entry = json.loads(line)
                self.assertEqual(entry["tool"], "Read")
                self.assertEqual(entry["file"], "context/example.md")
                self.assertEqual(entry["intent"], "read context/example.md")
                self.assertEqual(entry["session"], "session-test-001")

    def test_tool_intents(self) -> None:
        for fixture_name, expected in EXPECTED_INTENTS.items():
            with self.subTest(fixture=fixture_name):
                payload = (FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8")
                with temp_hook_repo(POWERSHELL_HOOK) as (repo, hook):
                    result = self.run_hook(hook, payload)

                    self.assertEqual(result.returncode, 0)
                    lines = observation_lines(repo)
                    self.assertEqual(len(lines), 1)
                    entry = json.loads(lines[0])
                    self.assertEqual(entry["tool"], expected["tool"])
                    self.assertEqual(entry["file"], expected["file"])
                    self.assertEqual(entry["intent"], expected["intent"])

    def test_privacy_truncates_and_strips_control_chars(self) -> None:
        payload = json.dumps(
            {
                "session_id": "session-test-001",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "context/example.md",
                    "new_string": "line one\nline two\t" + ("x" * 5000),
                },
            }
        )

        with temp_hook_repo(POWERSHELL_HOOK) as (repo, hook):
            result = self.run_hook(hook, payload)

            self.assertEqual(result.returncode, 0)
            raw_line = observation_lines(repo)[0]
            self.assertNotIn("\t", raw_line)
            entry = json.loads(raw_line)
            self.assertLessEqual(len(entry["intent"]), 120)
            self.assertNotRegex(entry["intent"], r"[\x00-\x1f\x7f]")

    def test_malformed_input_still_writes_valid_jsonl_when_enabled(self) -> None:
        payload = (FIXTURE_ROOT / "malformed.json").read_text(encoding="utf-8")

        with temp_hook_repo(POWERSHELL_HOOK) as (repo, hook):
            result = self.run_hook(hook, payload)

            self.assertEqual(result.returncode, 0)
            lines = observation_lines(repo)
            self.assertLessEqual(len(lines), 1)
            for line in lines:
                json.loads(line)

    def test_write_failure_fails_open(self) -> None:
        payload = (FIXTURE_ROOT / "edit.json").read_text(encoding="utf-8")

        with temp_hook_repo(POWERSHELL_HOOK, block_observations=True) as (repo, hook):
            result = self.run_hook(hook, payload)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(observation_lines(repo), [])


class PostToolUseBashHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bash = bash_bin()
        if not self.bash:
            self.skipTest("bash is not on PATH")

    def to_bash_path(self, path: Path) -> str:
        if os.name != "nt":
            return str(path)
        env = os.environ.copy()
        env["TARGET_PATH"] = str(path)
        result = subprocess.run(
            [self.bash, "-lc", 'command -v cygpath >/dev/null 2>&1 && cygpath -u "$TARGET_PATH"'],
            text=True,
            capture_output=True,
            env=env,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        path_text = str(path)
        if len(path_text) > 2 and path_text[1] == ":":
            drive = path_text[0].lower()
            rest = path_text[3:].replace("\\", "/")
            return f"/mnt/{drive}/{rest}"
        return path_text

    def make_uname_shim(self, repo: Path, value: str) -> Path:
        bin_dir = repo / "bin"
        bin_dir.mkdir()
        shim = bin_dir / "uname"
        shim.write_text(
            "#!/usr/bin/env bash\nprintf '%s\\n' \"$FAKE_UNAME\"\n",
            encoding="utf-8",
            newline="\n",
        )
        shim.chmod(0o755)
        return bin_dir

    def run_hook(
        self,
        hook_path: Path,
        hook_input: str,
        observations: str | None = "1",
        fake_uname: str | None = None,
        repo: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = env_with_observations(observations)
        script = self.to_bash_path(hook_path)

        if fake_uname:
            if repo is None:
                raise ValueError("repo is required when fake_uname is set")
            bin_dir = self.make_uname_shim(repo, fake_uname)
            env["FAKE_UNAME"] = fake_uname
            bin_path = self.to_bash_path(bin_dir)
            obs_cmd = "unset FOUNDER_OS_OBSERVATIONS"
            if observations is not None:
                obs_cmd = f"export FOUNDER_OS_OBSERVATIONS={shlex.quote(observations)}"
            fake_cmd = f"export FAKE_UNAME={shlex.quote(fake_uname)}"
            path_cmd = f"export PATH={shlex.quote(bin_path)}:\"$PATH\""
            probe = subprocess.run(
                [self.bash, "-lc", f"{fake_cmd}; {path_cmd}; uname -s"],
                text=True,
                capture_output=True,
            )
            if probe.stdout.strip() != fake_uname:
                self.skipTest("bash PATH uname shim is not active on this runner")
            return subprocess.run(
                [self.bash, "-lc", f"{obs_cmd}; {fake_cmd}; {path_cmd}; bash {shlex.quote(script)}"],
                input=hook_input,
                text=True,
                capture_output=True,
            )

        return subprocess.run(
            [self.bash, script],
            input=hook_input,
            text=True,
            capture_output=True,
            env=env,
        )

    def test_gate_unset_and_zero_write_nothing(self) -> None:
        payload = (FIXTURE_ROOT / "read.json").read_text(encoding="utf-8")

        for value in (None, "0"):
            with self.subTest(observations=value):
                with temp_hook_repo(BASH_HOOK) as (repo, hook):
                    result = self.run_hook(hook, payload, value)

                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(observation_lines(repo), [])

    def test_windows_platform_guard_writes_nothing(self) -> None:
        payload = (FIXTURE_ROOT / "read.json").read_text(encoding="utf-8")

        with temp_hook_repo(BASH_HOOK) as (repo, hook):
            result = self.run_hook(hook, payload, "1", "MINGW64_NT", repo)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(observation_lines(repo), [])

    def test_linux_path_writes_valid_jsonl(self) -> None:
        payload = (FIXTURE_ROOT / "read.json").read_text(encoding="utf-8")

        with temp_hook_repo(BASH_HOOK) as (repo, hook):
            result = self.run_hook(hook, payload, "1", "Linux", repo)

            self.assertEqual(result.returncode, 0)
            lines = observation_lines(repo)
            self.assertEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertEqual(entry["tool"], "Read")
            self.assertEqual(entry["file"], "context/example.md")
            self.assertEqual(entry["intent"], "read context/example.md")

    def test_tool_intents_on_linux_path(self) -> None:
        for fixture_name, expected in EXPECTED_INTENTS.items():
            with self.subTest(fixture=fixture_name):
                payload = (FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8")
                with temp_hook_repo(BASH_HOOK) as (repo, hook):
                    result = self.run_hook(hook, payload, "1", "Linux", repo)

                    self.assertEqual(result.returncode, 0)
                    lines = observation_lines(repo)
                    self.assertEqual(len(lines), 1)
                    entry = json.loads(lines[0])
                    self.assertEqual(entry["tool"], expected["tool"])
                    self.assertEqual(entry["file"], expected["file"])
                    self.assertEqual(entry["intent"], expected["intent"])

    def test_write_failure_fails_open_on_linux_path(self) -> None:
        payload = (FIXTURE_ROOT / "edit.json").read_text(encoding="utf-8")

        with temp_hook_repo(BASH_HOOK, block_observations=True) as (repo, hook):
            result = self.run_hook(hook, payload, "1", "Linux", repo)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(observation_lines(repo), [])

    def test_malformed_input_still_writes_valid_jsonl_on_linux_path(self) -> None:
        payload = (FIXTURE_ROOT / "malformed.json").read_text(encoding="utf-8")

        with temp_hook_repo(BASH_HOOK) as (repo, hook):
            result = self.run_hook(hook, payload, "1", "Linux", repo)

            self.assertEqual(result.returncode, 0)
            lines = observation_lines(repo)
            self.assertLessEqual(len(lines), 1)
            for line in lines:
                json.loads(line)

    def test_privacy_truncates_and_strips_control_chars_on_linux_path(self) -> None:
        payload = json.dumps(
            {
                "session_id": "session-test-001",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "context/example.md",
                    "new_string": "line one\nline two\t" + ("x" * 5000),
                },
            }
        )

        with temp_hook_repo(BASH_HOOK) as (repo, hook):
            result = self.run_hook(hook, payload, "1", "Linux", repo)

            self.assertEqual(result.returncode, 0)
            raw_line = observation_lines(repo)[0]
            self.assertNotIn("\t", raw_line)
            entry = json.loads(raw_line)
            self.assertLessEqual(len(entry["intent"]), 120)
            self.assertNotRegex(entry["intent"], r"[\x00-\x1f\x7f]")


if __name__ == "__main__":
    unittest.main()
