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
        if (cand / "templates" / "scripts").is_dir():
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
        named = []
        for h in hits:
            manifest = h / ".claude-plugin" / "plugin.json"
            try:
                if json.loads(manifest.read_text(encoding="utf-8")).get("name") == "founder-os":
                    named.append(h)
            except (OSError, ValueError):
                continue
        if named:
            return named[0]
        if hits:
            return hits[0]
    return None


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
            "dispatch.py" in (h.get("command") or "") and event in (h.get("command") or "")
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


def render(report: dict) -> str:
    out = ["INSTALL CHECK - what a script can prove about this folder", ""]
    for c in report["checks"]:
        out.append(f"[{c['status'].upper()}] {c['name']}: {c['detail']}")
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
