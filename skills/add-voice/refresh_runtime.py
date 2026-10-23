# -*- coding: utf-8 -*-
"""
refresh_runtime.py - "update my voice runtime": bring your voice/ copies up to date.

voice/ is your folder, gitignored. The setup scripts copy runtime files into it once, and an
update of Founder OS refreshes only the templates under skills/. So a fix that ships in a
template (the Host and Origin check on the voice servers, for one) does not reach you until
the copy in voice/ is replaced. This does that, for every runtime file you already have:

  voice/server.py, voice/index.html     the Tier-0 voice loop       (skills/add-voice/runtime/)
  voice/live_server.py, voice/live.html the realtime voice          (skills/add-voice/realtime/)
  voice/say.py                          the mouth                   (skills/add-mouth/runtime/)
  voice/hands.py                        the hands                   (skills/add-hands/runtime/)

It never adds a runtime file you did not install, and it never touches a settings file
(config.json, realtime-config.json, mouth-config.json, hands-config.json, persona.md) or a
log. Before it replaces a copy, it keeps the old one beside it as <name>.<date>.bak (for
example server.py.2026-10-23.bak), because it cannot tell an older version from one you
changed by hand. No pip install, no network. Python standard library only.

Usage:
    python skills/add-voice/refresh_runtime.py
"""

import filecmp
import shutil
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
SKILLS_DIR = SKILL_DIR.parent

# (template under skills/, name in voice/, what it is). Every file in the four template
# folders (TEMPLATE_DIRS) must be listed here. The maintainer tests fail when one is not, so a
# new runtime file cannot ship without a way to refresh it.
RUNTIME_FILES = (
    ("add-voice/runtime/server.py", "server.py", "voice server"),
    ("add-voice/runtime/index.html", "index.html", "voice page"),
    ("add-voice/realtime/live_server.py", "live_server.py", "realtime voice server"),
    ("add-voice/realtime/live.html", "live.html", "realtime voice page"),
    ("add-mouth/runtime/say.py", "say.py", "mouth"),
    ("add-hands/runtime/hands.py", "hands.py", "hands"),
)
TEMPLATE_DIRS = ("add-voice/runtime", "add-voice/realtime", "add-mouth/runtime", "add-hands/runtime")


def find_repo_root(start):
    cur = start
    for _ in range(8):
        if (cur / "skills").is_dir() and (cur / "CLAUDE.md").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return SKILL_DIR.parent.parent


def keep_old_copy(dst, today=None):
    """Copy dst to <name>.<date>.bak beside it, never over an earlier backup, and return the
    backup's path. The .bak ending means nothing runs or serves it by mistake."""
    stamp = (today or date.today()).isoformat()
    bak = dst.with_name(dst.name + "." + stamp + ".bak")
    n = 2
    while bak.exists():
        bak = dst.with_name(dst.name + "." + stamp + "-" + str(n) + ".bak")
        n += 1
    shutil.copy2(str(dst), str(bak))
    return bak


def refresh(root, skills_dir=SKILLS_DIR):
    """Copy each template over its voice/ copy when that copy exists and differs.
    Returns a list of (status, name, label) with status copied / current / missing-template /
    not-installed, plus a ("kept", backup name, name it backs up) row for every old copy kept."""
    voice = Path(root) / "voice"
    results = []
    for rel, name, label in RUNTIME_FILES:
        src = Path(skills_dir) / rel
        dst = voice / name
        if not dst.exists():
            results.append(("not-installed", name, label))
            continue
        if not src.exists():
            results.append(("missing-template", name, label))
            continue
        if filecmp.cmp(str(src), str(dst), shallow=False):
            results.append(("current", name, label))
            continue
        bak = keep_old_copy(dst)
        shutil.copy2(str(src), str(dst))
        results.append(("copied", name, label))
        results.append(("kept", bak.name, name))
    return results


def main():
    root = find_repo_root(SKILL_DIR)
    voice = root / "voice"
    if not voice.is_dir():
        print("No voice/ folder here, so there is nothing to update. Say 'add voice' to set it up.")
        return 0
    results = refresh(root)
    print("Update my voice runtime - " + str(voice))
    for status, name, label in results:
        if status == "copied":
            print("  copied     " + name + "  (" + label + ", newer version)")
        elif status == "kept":
            print("  kept       " + name + "  (your old " + label + ", in case you had changed it)")
        elif status == "current":
            print("  current    " + name + "  (" + label + ", already up to date)")
        elif status == "missing-template":
            print("  MISSING    " + name + "  (the template is not in this install - run the Founder OS update first)")
    skipped = [name for status, name, _ in results if status == "not-installed"]
    if skipped:
        print("  Not installed, so not added: " + ", ".join(skipped))
    kept = [p.name for p in sorted(voice.glob("*.json"))]
    if kept:
        print("  Your settings were not touched: " + ", ".join(kept))
    if any(status == "copied" for status, _, _ in results):
        print("Restart any voice server that is running (close its window and start it again).")
        print("A server that is already running keeps the old code until then.")
    else:
        print("Nothing to copy. Your voice runtime is already up to date.")
    return 1 if any(status == "missing-template" for status, _, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
