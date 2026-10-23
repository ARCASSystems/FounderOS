# -*- coding: utf-8 -*-
"""
hands.py - take an action, behind the confirm gate.

Copied into the gitignored voice/ folder by skills/add-hands/setup.py. Reads
voice/hands-config.json to know which actions are enabled and which class each is in.

The gate is the whole design:
  - auto    (open a folder or a web link, note): safe, reversible, local. No confirmation.
  - confirm (open a file or an app): opening one can run a program, so it prints what it
                          will open and stops for an explicit --yes.
  - confirm (run):        irreversible. OFF unless enabled in the config, and even then it
                          stops for an explicit --yes and prints the command first.
  - not built (send, post, computer-use): refused with a plain message. They are not improvised.

Python standard library only. No pip installs. It makes no network calls of its own; the
open action can open a URL, which hands off to your browser (that is the point of "open a link").

Usage:
    python voice/hands.py open .                        # open a folder or a web link
    python voice/hands.py open report.pdf --yes         # a file or app: shown first, needs --yes
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


def load_redactor():
    """The OS's own password and key filter, scripts/_common.py in the install this voice/
    folder sits in (setup copies hands.py to <root>/voice/, the helpers live in <root>/scripts/).
    Loaded by path so nothing else in scripts/ is put on the import path. None when it is not
    there: then a note is not written at all, the same rule rant capture follows."""
    src = ROOT / "scripts" / "_common.py"
    if not src.is_file():
        return None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("founderos_common_for_hands", src)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.redact_secrets
    except Exception:
        return None


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


WEB_LINK = re.compile(r"^https?://\S+$", re.IGNORECASE)


def open_class(target):
    """Which gate an open target goes through.

    "auto" only for a folder that exists or a web link: opening those shows something and
    runs nothing. Everything else is "confirm". The opener runs whatever it is handed, so a
    .bat, .exe, .cmd, .ps1, shortcut or script would RUN on open, and a document can carry
    macros. A file, an app, or any other kind of link therefore stops for an explicit yes."""
    if WEB_LINK.match(target):
        return "auto"
    if Path(target).expanduser().is_dir():
        return "auto"
    return "confirm"


def _launch(target):
    system = platform.system()
    if system == "Windows":
        os.startfile(target)  # noqa: S606 - the documented Windows opener
        return 0
    return subprocess.run(["open" if system == "Darwin" else "xdg-open", target]).returncode


def do_open(target, yes=False):
    """Open a folder or a web link (auto), or a file or app (confirm: shown first, needs --yes)."""
    if not target:
        print("hands: open needs something to open (a folder, a file or a web link).", file=sys.stderr)
        return 1
    gate = open_class(target)
    if gate == "auto":
        if not WEB_LINK.match(target):
            # An absolute path never starts with "-", so the opener cannot read it as an option.
            target = str(Path(target).expanduser().resolve())
        label = "auto: safe, local"
    else:
        path = Path(target).expanduser()
        if path.exists():
            target = str(path.resolve())
        print("hands: this is a confirm-class action. Opening a file or an app can run a program")
        print("       (a .bat, .exe or script runs as soon as it opens). It will open:")
        print("       " + target)
        if not yes:
            print("hands: refused - no explicit yes. Re-run with --yes to confirm. Folders and web")
            print("       links open without asking; files and apps always ask.")
            return 1
        label = "confirmed (--yes)"
    try:
        rc = _launch(target)
    except OSError as exc:
        print("hands: could not open '" + target + "' (" + str(exc) + ").", file=sys.stderr)
        return 1
    if rc != 0:
        print("hands: the opener could not open '" + target + "'.", file=sys.stderr)
        return 1
    print("hands: opened " + target + " (" + label + ").")
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
    # brain/log.md is tracked and backed up, so a pasted password or key never reaches it.
    redact = load_redactor()
    if redact is None:
        print("hands: the password and key filter (scripts/_common.py) is missing, so the note was",
              file=sys.stderr)
        print("       not written. Run the Founder OS update to put it back.", file=sys.stderr)
        return 1
    hidden = redact(cleaned)
    if hidden != cleaned:
        print("hands: hid what looked like a password or key before writing the note.")
    text = hidden
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
    # Print UTF-8 whatever the console's codepage: an Arabic folder name raised
    # UnicodeEncodeError on a Windows pipe instead of showing what would open.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
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
        return do_open(payload, args.yes)
    if action == "note":
        return do_note(payload)
    if action == "run":
        return do_run(payload, args.yes, cfg.get("enabled", False))
    print("hands: unhandled action '" + action + "'.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
