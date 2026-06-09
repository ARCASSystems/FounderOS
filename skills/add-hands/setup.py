# -*- coding: utf-8 -*-
"""
setup.py - wire the action handlers ("Add hands") onto THIS machine, behind a confirm gate.

The background installer the add-hands skill runs. It does the three jobs the capability
scaffold calls for:

  1. INSTALL  - nothing to install. The default hands (open things, save a note) use tools
                your machine already has. No key, no paid service, no pip install.
  2. WIRE     - writes voice/hands-config.json (the action classes and which are enabled)
                and copies the action dispatcher (hands.py) into the gitignored voice/.
  3. REFERENCE- points at references/hands-and-the-confirm-gate.md (the gate, the classes,
                what is not built yet) so the owner knows exactly what the hands can do.

The confirm gate is the whole point. By default only the Auto class (open, note) is enabled.
The Confirm class (run a command) is wired but OFF; the owner turns it on deliberately, and
even then it stops for an explicit yes every time. Sending, posting, and computer control are
not built - the dispatcher refuses them rather than pretending.

Reads:  the skill's runtime/ template (hands.py) next to this file.
Writes: <repo-root>/voice/  (hands.py, hands-config.json) - gitignored, yours.

No pip installs. Python standard library only.

Usage:
    python skills/add-hands/setup.py            # wire the safe default hands
    python skills/add-hands/setup.py --enable-run   # also enable the gated command runner
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
RUNTIME_SRC = SKILL_DIR / "runtime"


def find_repo_root(start):
    cur = start
    for _ in range(8):
        if (cur / "skills").is_dir() and (cur / "CLAUDE.md").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return SKILL_DIR.parent.parent


def main():
    ap = argparse.ArgumentParser(description="Wire the action handlers behind a confirm gate.")
    ap.add_argument("--enable-run", action="store_true",
                    help="enable the gated command runner (still stops for an explicit yes each time)")
    args = ap.parse_args()

    print("Add hands - safe actions run freely; irreversible ones ask first")
    print("-" * 58)

    if sys.version_info < (3, 8):
        print("FAIL: Python 3.8+ needed. Found " + sys.version.split()[0])
        return 1
    print("OK   Python " + sys.version.split()[0] + " - the default hands need no pip install and no key.")

    root = find_repo_root(SKILL_DIR)
    voice_dir = root / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)

    hands_src = RUNTIME_SRC / "hands.py"
    if not hands_src.exists():
        print("FAIL: missing runtime template " + str(hands_src))
        return 1
    shutil.copy2(hands_src, voice_dir / "hands.py")
    print("OK   Copied the action dispatcher into " + str(voice_dir / "hands.py"))

    config = {
        "handlers": {
            "open": {"class": "auto", "enabled": True,
                     "note": "open a file, folder, app, or link - reversible, local"},
            "note": {"class": "auto", "enabled": True,
                     "note": "append a line to brain/log.md - reversible"},
            "run": {"class": "confirm", "enabled": bool(args.enable_run),
                    "note": "run a local command - irreversible, OFF by default, needs an explicit --yes"},
        },
        "not_built": {
            "send": "sending a message is not built - it will arrive in the confirm class, gated",
            "post": "posting is not built - it will arrive in the confirm class, gated",
            "computer_use": "controlling your screen is not built - a later capability, gated when it lands",
        },
        "created": datetime.now(timezone.utc).isoformat(),
        "note": "Action gate. auto = safe/reversible/local, runs freely. confirm = irreversible, "
                "needs an explicit --yes and is shown first. Set handlers.run.enabled true to allow "
                "the command runner. See skills/add-hands/references/hands-and-the-confirm-gate.md.",
    }
    (voice_dir / "hands-config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print("OK   Wrote voice/hands-config.json.")
    print("     Auto (no confirm):  open, note")
    print("     Confirm (asks first): run  -> " + ("ENABLED (still asks every time)" if args.enable_run else "OFF (turn on in hands-config.json when you want it)"))
    print("     Not built: send, post, computer-use (the dispatcher refuses these honestly)")

    print("")
    print("Done. To use it:")
    print("  1. Open something:  python voice/hands.py open .")
    print('  2. Save a note:     python voice/hands.py note "what just happened"')
    if args.enable_run:
        print('  3. Run a command:   python voice/hands.py run "git status" --yes   (the yes is the gate)')
    else:
        print("  3. The command runner is OFF. Enable it in voice/hands-config.json if you want it;")
        print("     it then stops for an explicit --yes every time and shows the command first.")
    print("")
    print("Nothing irreversible happens without your explicit yes. Sending, posting, and screen")
    print("control are not built - the OS will say so rather than pretend.")
    print("Full detail: skills/add-hands/references/hands-and-the-confirm-gate.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
