# -*- coding: utf-8 -*-
"""
hands.py - take an action, behind the confirm gate.

Copied into the gitignored voice/ folder by skills/add-hands/setup.py. Reads
voice/hands-config.json to know which actions are enabled and which class each is in.

The gate is the whole design:
  - auto    (open, note): safe, reversible, local. Runs with no confirmation.
  - confirm (run):        irreversible. OFF unless enabled in the config, and even then it
                          stops for an explicit --yes and prints the command first.
  - not built (send, post, computer-use): refused with a plain message. They are not improvised.

Python standard library only. No pip installs. It makes no network calls of its own; the
open action can open a URL, which hands off to your browser (that is the point of "open a link").

Usage:
    python voice/hands.py open .                        # open a file, folder, app, or link
    python voice/hands.py note "what just happened"     # append a line to brain/log.md
    python voice/hands.py run "git status"              # shows the command, refuses without --yes
    python voice/hands.py run "git status" --yes        # runs it - the yes is the gate
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

VOICE_DIR = Path(__file__).resolve().parent
ROOT = VOICE_DIR.parent

NOT_BUILT = {"send", "post", "computer-use", "computer_use", "control", "click", "type"}

# The <private> exclusion tag (rules/operating-rules.md): a note can carry a <private>...</private>
# block the user does not want written. Strip every such block before persisting, case-insensitive.
PRIVATE_BLOCK = re.compile(r"<private>.*?</private>", re.IGNORECASE | re.DOTALL)


def strip_private(text):
    """Remove <private>...</private> blocks. Returns the cleaned text (may be empty)."""
    return PRIVATE_BLOCK.sub("", text).strip()


def load_config():
    cfg = VOICE_DIR / "hands-config.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    # Safe fallback: only the auto handlers, run off.
    return {"handlers": {"open": {"class": "auto", "enabled": True},
                         "note": {"class": "auto", "enabled": True},
                         "run": {"class": "confirm", "enabled": False}}}


def handler_cfg(config, name):
    return config.get("handlers", {}).get(name, {})


def do_open(target):
    """Open a file, folder, app, or URL with the OS opener. Reversible and local."""
    if not target:
        print("hands: open needs something to open (a path or a URL).", file=sys.stderr)
        return 1
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(target)  # noqa: S606 - the documented Windows opener
        elif system == "Darwin":
            subprocess.run(["open", target])
        else:
            subprocess.run(["xdg-open", target])
    except (OSError, FileNotFoundError) as exc:
        print("hands: could not open '" + target + "' (" + str(exc) + ").", file=sys.stderr)
        return 1
    print("hands: opened " + target + " (auto: safe, local).")
    return 0


def do_note(text):
    """Append a dated line to brain/log.md. Reversible (you can delete the line)."""
    if not text:
        print("hands: note needs some text.", file=sys.stderr)
        return 1
    cleaned = strip_private(text)
    if not cleaned:
        print("hands: the whole note was tagged <private> - nothing written.")
        return 0
    if cleaned != text.strip():
        print("hands: stripped a <private> block from the note before writing.")
    text = cleaned
    log = ROOT / "brain" / "log.md"
    created = not log.exists()
    log.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = "- " + stamp + " " + text.strip() + "  #hands\n"
    with log.open("a", encoding="utf-8") as fh:
        fh.write(line)
    where = "created brain/log.md and added" if created else "appended to brain/log.md"
    print("hands: " + where + " a note (auto: reversible). Delete the line to undo.")
    return 0


def do_run(command, yes, enabled):
    """Run a local command - the confirm-class example. Gated on enabled AND an explicit yes."""
    if not command:
        print("hands: run needs a command.", file=sys.stderr)
        return 1
    if not enabled:
        print("hands: the command runner is OFF. Enable handlers.run.enabled in")
        print("       voice/hands-config.json if you want it. It will still ask every time.")
        return 1
    print("hands: this is a confirm-class action. It will run, on your machine:")
    print("       " + command)
    if not yes:
        print("hands: refused - no explicit yes. Re-run with --yes to confirm. The OS does not")
        print("       supply the yes for you; that is the gate.")
        return 1
    print("hands: confirmed (--yes). Running it.")
    return subprocess.run(command, shell=True).returncode


def main():
    ap = argparse.ArgumentParser(description="Take an action behind the confirm gate.")
    ap.add_argument("action", help="open | note | run  (send / post / computer-use are not built)")
    ap.add_argument("args", nargs="*", help="the target, text, or command for the action")
    ap.add_argument("--yes", action="store_true", help="explicit confirmation for a confirm-class action")
    args = ap.parse_args()

    action = args.action.lower()
    payload = " ".join(args.args).strip()
    config = load_config()

    if action in NOT_BUILT:
        print("hands: '" + action + "' is not built yet. When it is, it arrives in the confirm")
        print("       class, behind an explicit yes - never auto-run. The OS will not improvise it.")
        return 1

    cfg = handler_cfg(config, action)
    if not cfg:
        print("hands: unknown action '" + action + "'. Known: open, note, run.", file=sys.stderr)
        return 1
    if not cfg.get("enabled", False) and action != "run":
        print("hands: '" + action + "' is disabled in voice/hands-config.json.", file=sys.stderr)
        return 1

    if action == "open":
        return do_open(payload)
    if action == "note":
        return do_note(payload)
    if action == "run":
        return do_run(payload, args.yes, cfg.get("enabled", False))
    print("hands: unhandled action '" + action + "'.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
