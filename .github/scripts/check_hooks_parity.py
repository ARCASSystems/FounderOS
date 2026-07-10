#!/usr/bin/env python3
"""Hooks-parity guard (dispatcher model, v1.42+).

The OS used to ship every hook as a .sh/.ps1 pair and register both halves in
settings.json, so a plain Windows box (no bash) or a plain Linux box (no
PowerShell) printed an interpreter-not-found error on every fire, and the Stop
handlers ran in an unguaranteed order. v1.42 replaced that with ONE cross
platform Python dispatcher: `scripts/hooks/dispatch.py <Event>`, one settings
entry per event. Python is a hard prerequisite, so there is no shell to be
missing and the dispatcher runs Stop work in a fixed order.

This guard enforces the dispatcher model instead of the old pairing:

1. `scripts/hooks/dispatch.py` exists.
2. Every one of the six hook events is wired in settings.json with EXACTLY one
   command, and that command calls the dispatcher with the matching event name.
3. The set of events settings.json wires equals the set of events the
   dispatcher actually handles (its EVENTS table) - neither can wire or handle
   an event the other does not.
4. No retired .sh/.ps1 hook remains in .claude/hooks/ (only the
   session_start_brief.py helper the dispatcher calls is allowed).

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
DISPATCHER = ROOT / "scripts" / "hooks" / "dispatch.py"
DISPATCHER_REF = "scripts/hooks/dispatch.py"

# The six events the OS wires. All must be present, none extra.
CANONICAL_EVENTS = {
    "PreToolUse",
    "SessionStart",
    "UserPromptSubmit",
    "PreCompact",
    "Stop",
    "PostToolUse",
}

# Non-dispatcher files that are allowed to live in .claude/hooks/ (Python helpers
# the dispatcher calls at runtime). Anything else there is a retired shell hook
# or stray file and fails the guard.
ALLOWED_HELPERS = {"session_start_brief.py"}


def fail(messages: list[str]) -> None:
    print("HOOKS-PARITY GUARD FAILED")
    print()
    for m in messages:
        print(f"- {m}")
    sys.exit(1)


def dispatcher_events(text: str) -> set[str]:
    """Extract the event names the dispatcher's EVENTS table handles."""
    m = re.search(r"EVENTS\s*=\s*\{(.*?)\}", text, re.DOTALL)
    if not m:
        return set()
    return set(re.findall(r'"(\w+)"\s*:', m.group(1)))


def main() -> None:
    problems: list[str] = []

    if not DISPATCHER.is_file():
        fail([f"dispatcher missing: {DISPATCHER_REF}"])
    if not SETTINGS.is_file():
        fail([f"settings file missing: {SETTINGS}"])

    try:
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception as exc:
        fail([f"could not parse {SETTINGS}: {exc}"])

    events = settings.get("hooks", {})
    wired: set[str] = set(events.keys())

    # --- Check 2: one dispatcher command per event, matching arg ----------- #
    for event, groups in events.items():
        cmds = [h.get("command", "") for g in groups for h in g.get("hooks", [])]
        if len(cmds) != 1:
            problems.append(
                f"{event}: expected exactly one dispatcher command, found {len(cmds)}"
            )
            continue
        cmd = cmds[0]
        if DISPATCHER_REF not in cmd:
            problems.append(f"{event}: command does not call {DISPATCHER_REF}: {cmd!r}")
            continue
        if not re.search(rf"dispatch\.py\"?\s+{re.escape(event)}\b", cmd):
            problems.append(
                f"{event}: dispatcher command does not pass the matching event name: {cmd!r}"
            )

    # --- Check 3a: every canonical event is wired ------------------------- #
    for event in sorted(CANONICAL_EVENTS - wired):
        problems.append(f"{event}: canonical hook event is not wired in settings.json")
    for event in sorted(wired - CANONICAL_EVENTS):
        problems.append(f"{event}: settings.json wires an event outside the canonical set")

    # --- Check 3b: settings events == dispatcher-handled events ----------- #
    handled = dispatcher_events(DISPATCHER.read_text(encoding="utf-8"))
    if not handled:
        problems.append("could not read the dispatcher EVENTS table from dispatch.py")
    else:
        for event in sorted(wired - handled):
            problems.append(
                f"{event}: wired in settings.json but dispatch.py has no handler for it"
            )
        for event in sorted(handled - wired):
            problems.append(
                f"{event}: dispatch.py handles it but settings.json does not wire it"
            )

    # --- Check 4: no retired shell hooks left behind ---------------------- #
    if HOOKS_DIR.is_dir():
        for p in sorted(HOOKS_DIR.iterdir()):
            if not p.is_file():
                continue
            if p.suffix in {".sh", ".ps1"}:
                problems.append(
                    f".claude/hooks/{p.name} is a retired shell hook - the dispatcher "
                    f"replaced the .sh/.ps1 pairs; remove it"
                )
            elif p.name not in ALLOWED_HELPERS and p.suffix == ".py":
                problems.append(
                    f".claude/hooks/{p.name} is an unexpected hook file - add it to "
                    f"ALLOWED_HELPERS in this guard if the dispatcher calls it on purpose"
                )

    if problems:
        fail(problems)

    print(
        f"hooks-parity: OK (dispatcher wires {len(wired)} events, "
        f"one command each, no retired shell hooks remain)"
    )


if __name__ == "__main__":
    main()
