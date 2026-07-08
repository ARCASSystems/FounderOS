#!/usr/bin/env python3
"""Hooks-parity guard.

The OS promises that every hook runs on a plain Windows machine (PowerShell,
no bash, no git-bash) AND on macOS/Linux (bash). That promise is structural:
every hook ships as a .sh/.ps1 pair, and settings.json registers both halves.
This guard makes CI enforce the pairing instead of trusting it.

Checks:
1. Every .sh in .claude/hooks/ has a .ps1 sibling, and vice versa.
2. Every hook command in .claude/settings.json points at a file that exists.
3. For every registered .sh there is a registered .ps1 twin in the same hook
   event, and vice versa - a hook wired for one shell only is a silent gap on
   the other platform.

Pure stdlib. Exit 0 clean, exit 1 with a plain report on any violation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HOOKS_DIR = ROOT / ".claude" / "hooks"
SETTINGS = ROOT / ".claude" / "settings.json"

# Shared helpers that are deliberately single-file (no shell pair needed).
PAIR_EXEMPT = {"session_start_brief.py"}


def fail(messages: list[str]) -> None:
    print("HOOKS-PARITY GUARD FAILED")
    print()
    for m in messages:
        print(f"- {m}")
    sys.exit(1)


def main() -> None:
    problems: list[str] = []

    if not HOOKS_DIR.is_dir():
        fail([f"hooks directory missing: {HOOKS_DIR}"])
    if not SETTINGS.is_file():
        fail([f"settings file missing: {SETTINGS}"])

    # --- Check 1: on-disk .sh/.ps1 pairing -------------------------------- #
    sh_files = {p.stem for p in HOOKS_DIR.glob("*.sh")}
    ps1_files = {p.stem for p in HOOKS_DIR.glob("*.ps1")}
    for stem in sorted(sh_files - ps1_files):
        problems.append(f".claude/hooks/{stem}.sh has no PowerShell twin ({stem}.ps1)")
    for stem in sorted(ps1_files - sh_files):
        problems.append(f".claude/hooks/{stem}.ps1 has no bash twin ({stem}.sh)")

    unexpected = {
        p.name
        for p in HOOKS_DIR.iterdir()
        if p.is_file() and p.suffix not in {".sh", ".ps1"} and p.name not in PAIR_EXEMPT
    }
    for name in sorted(unexpected):
        problems.append(
            f".claude/hooks/{name} is neither a .sh/.ps1 hook nor a listed shared "
            f"helper - add it to PAIR_EXEMPT in this guard if it is intentional"
        )

    # --- Checks 2 + 3: settings.json registration ------------------------- #
    try:
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception as exc:
        fail([f"could not parse {SETTINGS}: {exc}"])

    hook_ref = re.compile(r"\.claude/hooks/([A-Za-z0-9_.-]+)")

    events = settings.get("hooks", {})
    for event, groups in events.items():
        for group in groups:
            registered: set[str] = set()
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                m = hook_ref.search(cmd)
                if not m:
                    problems.append(
                        f"{event}: command does not reference .claude/hooks/: {cmd!r}"
                    )
                    continue
                fname = m.group(1)
                registered.add(fname)
                if not (HOOKS_DIR / fname).is_file():
                    problems.append(
                        f"{event}: registered hook file does not exist: .claude/hooks/{fname}"
                    )

            stems_sh = {f[:-3] for f in registered if f.endswith(".sh")}
            stems_ps1 = {f[:-4] for f in registered if f.endswith(".ps1")}
            for stem in sorted(stems_sh - stems_ps1):
                problems.append(
                    f"{event}: {stem}.sh is registered but {stem}.ps1 is not - "
                    f"the hook is silent on Windows-without-bash"
                )
            for stem in sorted(stems_ps1 - stems_sh):
                problems.append(
                    f"{event}: {stem}.ps1 is registered but {stem}.sh is not - "
                    f"the hook is silent on macOS/Linux"
                )

    if problems:
        fail(problems)

    n_pairs = len(sh_files & ps1_files)
    print(f"hooks-parity: OK ({n_pairs} .sh/.ps1 pairs, all registered hooks exist, both shells wired)")


if __name__ == "__main__":
    main()
