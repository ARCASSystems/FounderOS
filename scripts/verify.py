#!/usr/bin/env python3
"""verify.py - prove an install is complete instead of assuming it.

Why this exists: v1.53.1 shipped five defects that all passed CI, because CI
checks the repo and nothing checks an INSTALL. The health-check skill could not
catch them either - its own text said "enumerate dynamically, do not hardcode a
list", and a check that derives its expectations from whatever is on disk
cannot notice that something is missing from disk. Deletion was undetectable at
any model quality. Detection needs a contract that exists independently of the
folder being checked, and a comparison a script performs, not a model.

The contract is DERIVED, never hand-authored. A hand-maintained manifest is how
"thirty-two Python helpers" went stale the moment the thirty-third shipped. The
source of truth already exists: `templates/scripts/` is what the setup wizard
copies into a founder's install, so its file list IS the list of scripts every
install must hold. This script reads that list from the engine and compares.

Two consumers, one derivation:
  - CI (.github/scripts/check_install_completeness.py) imports run_checks() and
    asserts the repo itself satisfies the contract before anything ships - the
    repo is an install, and a release that fails its own verifier would tell
    every founder their install is broken.
  - The `verify` skill runs it against THIS INSTALLED FOLDER and translates the
    JSON into plain language. The script owns falsifiable; the prose owns
    readable.

Engine resolution mirrors the setup command: the working folder when it carries
`templates/scripts/` (git clone, curl, ZIP), else `${CLAUDE_PLUGIN_ROOT}`, else
a search of `~/.claude/plugins/` - never one hardcoded plugin path, because
plugin managers move their layout between versions and a wrong guess reports a
healthy install as broken.

Standard library only. Read-only: writes nothing, fixes nothing.

Usage:
  python scripts/verify.py            plain-text report
  python scripts/verify.py --json     machine-readable, for the skill
  python scripts/verify.py --root X   check an install other than this one
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shlex
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

HOOK_EVENTS = ("SessionStart", "PreToolUse", "UserPromptSubmit",
               "PreCompact", "Stop", "PostToolUse")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def resolve_engine(root: Path) -> Path | None:
    """The folder holding the shipped `templates/scripts/` this install is
    measured against. None when no engine is reachable - the caller reports
    that honestly rather than guessing."""
    if (root / "templates" / "scripts").is_dir():
        return root
    env = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip()
    if env:
        cand = Path(env)
        if (cand / "templates" / "scripts").is_dir() and _is_founder_os(cand):
            return cand
    plugins = Path.home() / ".claude" / "plugins"
    if plugins.is_dir():
        hits: list[Path] = []
        try:
            hits = sorted(
                (p.parent.parent for p in plugins.glob("**/templates/scripts")),
                key=lambda p: p.stat().st_mtime, reverse=True,
            )
        except OSError:
            hits = []
        # Identity is required, never preferred. Any plugin can ship a
        # templates/scripts folder, and measuring this install against someone
        # else's contract produces a confident answer about the wrong product -
        # worse than the honest "cannot verify" that no engine returns.
        for h in hits:
            manifest = h / ".claude-plugin" / "plugin.json"
            try:
                if json.loads(manifest.read_text(encoding="utf-8")).get("name") == "founder-os":
                    return h
            except (OSError, ValueError):
                continue
    return None


def _is_founder_os(candidate: Path) -> bool:
    """Whether this folder is the Founder OS engine, by its own manifest."""
    manifest = candidate / ".claude-plugin" / "plugin.json"
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("name") == "founder-os"
    except (OSError, ValueError):
        return False


def required_scripts(engine: Path) -> list[str]:
    """The install contract's script half, derived from what setup copies."""
    src = engine / "templates" / "scripts"
    return sorted(p.name for p in src.glob("*.py"))


def _check(name: str, status: str, detail: str, **extra) -> dict:
    return {"name": name, "status": status, "detail": detail, **extra}


def _scripts_complete(root: Path, engine: Path | None) -> dict:
    if engine is None:
        return _check(
            "scripts-complete", "warn",
            "cannot verify - the shipped script list was not found on this machine, "
            "so there is nothing to compare this install against",
            missing=[],
        )
    manifest = required_scripts(engine)
    have = root / "scripts"
    missing = [n for n in manifest if not (have / n).is_file()]
    if missing:
        return _check(
            "scripts-complete", "fail",
            f"{len(missing)} of {len(manifest)} shipped scripts are missing from scripts/: "
            + ", ".join(missing),
            missing=missing,
        )
    return _check("scripts-complete", "pass",
                  f"{len(manifest)}/{len(manifest)} shipped scripts present", missing=[])


def _scripts_current(root: Path, engine: Path | None) -> dict:
    """Whether every shipped helper in this install is the one that shipped.

    Presence is not currency. A helper left behind by an update, or edited by
    hand, is syntactically perfect and silently wrong - which is the exact shape
    of every defect the v1.53.x releases fixed: the repo had the fix and an
    install did not. Names alone cannot see that; bytes can.

    Skipped when the engine IS this folder, where the comparison is a file
    against itself."""
    if engine is None:
        return _check("scripts-current", "warn",
                      "cannot verify - the shipped files were not found on this "
                      "machine, so there is nothing to compare this install against",
                      stale=[])
    if engine.resolve() == root.resolve():
        return _check("scripts-current", "pass",
                      "this folder holds the shipped files themselves", stale=[])
    src = engine / "templates" / "scripts"
    dst = root / "scripts"
    stale = []
    for name in required_scripts(engine):
        a, b = src / name, dst / name
        if not b.is_file():
            continue    # absence is scripts-complete's finding, not this one
        try:
            if a.read_bytes() != b.read_bytes():
                stale.append(name)
        except OSError:
            stale.append(name)
    if stale:
        return _check(
            "scripts-current", "fail",
            f"{len(stale)} of the OS's own files do not match the version that "
            "shipped, so they are out of date or damaged: " + ", ".join(stale),
            stale=stale)
    return _check("scripts-current", "pass",
                  "every one of the OS's own files matches the version that shipped",
                  stale=[])


def _scripts_parse(root: Path) -> dict:
    scripts_dir = root / "scripts"
    if not scripts_dir.is_dir():
        return _check("scripts-parse", "fail",
                      "the scripts folder is missing entirely - no helper can run",
                      errors=[])
    targets = sorted(scripts_dir.glob("*.py")) + sorted((scripts_dir / "hooks").glob("*.py"))
    errors = []
    for path in targets:
        try:
            ast.parse(path.read_bytes(), str(path.name))
        except SyntaxError as exc:
            errors.append({"file": path.name, "error": f"line {exc.lineno}: {exc.msg}"})
        except OSError as exc:
            errors.append({"file": path.name, "error": str(exc)})
    if errors:
        names = ", ".join(e["file"] for e in errors)
        return _check("scripts-parse", "fail",
                      f"{len(errors)} of {len(targets)} scripts cannot run: {names}",
                      errors=errors)
    return _check("scripts-parse", "pass",
                  f"{len(targets)}/{len(targets)} scripts parse cleanly", errors=[])


def _hook_dispatcher(root: Path) -> dict:
    if (root / "scripts" / "hooks" / "dispatch.py").is_file():
        return _check("hook-dispatcher", "pass", "the hook dispatcher is present")
    return _check("hook-dispatcher", "fail",
                  "scripts/hooks/dispatch.py is missing - every session event "
                  "(the brief, the undo snapshot, the auto-save) is broken")


def _runs_dispatcher(hook: dict, event: str) -> bool:
    """Whether this entry actually runs the dispatcher for this event.

    Substring matching passed a command that merely mentioned the dispatcher and
    the event while running something else entirely - the check confirmed the
    words, not the wiring. This reads the command as arguments: the dispatcher
    must be the script being run, and the event must be an argument to it, not
    a word inside some other flag's value."""
    if hook.get("type") != "command":
        return False
    command = hook.get("command") or ""
    if not isinstance(command, str) or not command.strip():
        return False
    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        return False
    parts = [p.strip('"').strip("'") for p in parts]
    for i, part in enumerate(parts):
        norm = part.replace("\\", "/")
        # The dispatcher must be the script being RUN. Its full shipped path is
        # the only accepted shape: a bare "dispatch.py" sitting anywhere in the
        # line is satisfied by --label dispatch.py, which names the dispatcher
        # while running something else.
        if not norm.endswith("scripts/hooks/dispatch.py"):
            continue
        # a token immediately after a flag is that flag's value, not the program
        if i > 0 and parts[i - 1].startswith("-"):
            continue
        # the event must be the argument handed to it, not a word further down
        # the line inside some other flag's value
        rest = parts[i + 1:]
        if rest and rest[0] == event:
            return True
    return False


def _hooks_wired(root: Path) -> dict:
    settings = root / ".claude" / "settings.json"
    if not settings.is_file():
        return _check("hooks-wired", "warn",
                      "no .claude/settings.json here - hooks are not wired in this "
                      "folder (they are opt-in; setup writes this file)",
                      missing_events=list(HOOK_EVENTS))
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _check("hooks-wired", "warn",
                      ".claude/settings.json could not be read, so hook wiring "
                      "cannot be confirmed", missing_events=[])
    hooks = data.get("hooks", {}) if isinstance(data, dict) else {}
    missing = []
    for event in HOOK_EVENTS:
        entries = hooks.get(event) or []
        wired = any(
            _runs_dispatcher(h, event)
            for entry in entries if isinstance(entry, dict)
            for h in (entry.get("hooks") or []) if isinstance(h, dict)
        )
        if not wired:
            missing.append(event)
    if not missing:
        return _check("hooks-wired", "pass",
                      f"{len(HOOK_EVENTS)}/{len(HOOK_EVENTS)} events wired to the dispatcher",
                      missing_events=[])
    return _check("hooks-wired", "warn",
                  f"{len(HOOK_EVENTS) - len(missing)}/{len(HOOK_EVENTS)} events wired - "
                  "not wired: " + ", ".join(missing),
                  missing_events=missing)


def _version_marker(root: Path) -> dict:
    vfile = root / "VERSION"
    if not vfile.is_file():
        return _check("version-marker", "warn",
                      "no VERSION file - updates cannot tell what this install has; "
                      "running an update restores it", value=None)
    value = vfile.read_text(encoding="utf-8").strip()
    if not SEMVER_RE.match(value):
        return _check("version-marker", "warn",
                      f"VERSION holds '{value}', which does not look like a version; "
                      "running an update rewrites it", value=value)
    return _check("version-marker", "pass", f"install records v{value}", value=value)


def run_checks(root: Path) -> dict:
    root = Path(root).resolve()
    engine = resolve_engine(root)
    checks = [
        _scripts_complete(root, engine),
        _scripts_current(root, engine),
        _scripts_parse(root),
        _hook_dispatcher(root),
        _hooks_wired(root),
        _version_marker(root),
    ]
    worst = "pass"
    if any(c["status"] == "warn" for c in checks):
        worst = "warn"
    if any(c["status"] == "fail" for c in checks):
        worst = "fail"
    return {
        "root": str(root),
        "engine": str(engine) if engine else None,
        "checks": checks,
        "result": worst,
    }


# The JSON keys are for the skill. A person reading the plain output gets the
# thing being checked in their own words - no internal names, no paths.
CHECK_LABELS = {
    "scripts-complete": "All of the OS's own files are here",
    "scripts-current": "Those files are the version that shipped",
    "scripts-parse": "None of them are damaged",
    "hook-dispatcher": "The part that runs things automatically is in place",
    "hooks-wired": "It is switched on for this folder",
    "version-marker": "This install knows which version it is",
}


def render(report: dict) -> str:
    out = ["INSTALL CHECK - what this folder can prove about itself", ""]
    for c in report["checks"]:
        label = CHECK_LABELS.get(c["name"], c["name"])
        out.append(f"[{c['status'].upper()}] {label}")
        out.append(f"        {c['detail']}")
    out.append("")
    if report["result"] == "fail":
        out.append("Something above is broken. The fastest fix for a missing or "
                   "damaged file is to run an update - it refreshes the OS's own "
                   "files and never touches yours.")
    elif report["result"] == "warn":
        out.append("Nothing is broken. The lines above marked WARN are things this "
                   "folder does not have yet, with what turns each on.")
    else:
        out.append("Everything this script can prove, it proved. All present.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Prove this install is complete.")
    p.add_argument("--root", default=str(REPO_ROOT))
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    report = run_checks(Path(a.root))
    print(json.dumps(report, ensure_ascii=True, indent=2) if a.json else render(report))
    return 1 if report["result"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
