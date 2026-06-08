# -*- coding: utf-8 -*-
"""
setup.py - wire the Tier-0 voice capability onto THIS machine ("Add voice").

This is the background installer the add-voice skill runs. It does the three jobs the
capability scaffold calls for, tailored to the user's machine:

  1. INSTALL  - Tier 0 needs NO pip install and NO API key. It checks Python and the
                reasoning CLI you already run the OS in, and says plainly what (if
                anything) is missing. The local-first STT upgrade (faster-whisper) and
                the realtime upgrade (Tier 1) are documented, not forced.
  2. WIRE     - creates a local, gitignored voice/ runtime folder, copies the voice page
                and server into it, and writes voice/config.json bound to this machine
                (port, repo root, the detected brain command).
  3. REFERENCE- points at the skill's reference docs (the voice-model disclaimer, the
                tier map, troubleshooting) so the setup is correct for THIS user.

Accessibility floor: the default install works end-to-end on the one subscription you
already run the OS in, with no extra key. The brain answers through that CLI (`claude -p`
by default); your browser hears and speaks. Nothing here phones home.

Reads:  the skill's runtime/ templates next to this file.
Writes: <repo-root>/voice/  (server.py, index.html, config.json) - gitignored, yours.

No pip installs. Python standard library only (shutil, json, argparse, pathlib, sys).

Usage:
    python skills/add-voice/setup.py            # wire it, print next steps
    python skills/add-voice/setup.py --port 8800
    python skills/add-voice/setup.py --start    # wire, then start the server now
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
RUNTIME_SRC = SKILL_DIR / "runtime"

# Reasoning CLIs we know how to drive with no API key, best-known invocation each.
# Claude Code is the public OS's primary runtime, so it is preferred. We only WRITE a
# brain command we are confident about; for the others we wire the documented form and
# tell the user to confirm it, rather than silently shipping a wrong command.
CLI_CANDIDATES = [
    ("claude", ["claude", "-p"], True),    # confirmed: claude -p "<prompt>" prints the reply
    ("codex", ["codex", "exec"], False),   # documented form - verify before relying on it
    ("gemini", ["gemini", "-p"], False),   # documented form - verify before relying on it
]


def find_repo_root(start):
    """Walk up to the Founder OS repo root (the folder holding skills/ and CLAUDE.md)."""
    cur = start
    for _ in range(8):
        if (cur / "skills").is_dir() and (cur / "CLAUDE.md").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    # add-voice lives at <root>/skills/add-voice, so two up is the root.
    return SKILL_DIR.parent.parent


def detect_brain():
    """Return (argv, confirmed, name) for the first reasoning CLI found on PATH."""
    for name, argv, confirmed in CLI_CANDIDATES:
        if shutil.which(name):
            return argv, confirmed, name
    return None, False, None


def main():
    ap = argparse.ArgumentParser(description="Wire the Tier-0 voice capability.")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--start", action="store_true", help="start the server after wiring")
    args = ap.parse_args()

    print("Add voice - Tier 0 (default, no extra key, no paid service)")
    print("-" * 58)

    # 1. INSTALL checks
    if sys.version_info < (3, 8):
        print("FAIL: Python 3.8+ needed. Found " + sys.version.split()[0])
        return 1
    print("OK   Python " + sys.version.split()[0] + " - Tier 0 needs no pip install.")

    brain_argv, confirmed, brain_name = detect_brain()
    if brain_argv is None:
        print("WARN No reasoning CLI (claude / codex / gemini) found on PATH.")
        print("     Ears and save-to-brain will work; conversational answers will not")
        print("     until one is on PATH. Defaulting the brain command to 'claude -p'.")
        brain_argv = ["claude", "-p"]
    elif confirmed:
        print("OK   Brain command: " + " ".join(brain_argv) + " (no API key - uses your subscription).")
    else:
        print("OK   Found '" + brain_name + "'. Wired as: " + " ".join(brain_argv))
        print("     Verify this invocation answers a prompt; adjust voice/config.json if not.")

    # 2. WIRE
    root = find_repo_root(SKILL_DIR)
    voice_dir = root / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)

    for fname in ("server.py", "index.html"):
        src = RUNTIME_SRC / fname
        if not src.exists():
            print("FAIL: missing runtime template " + str(src))
            return 1
        shutil.copy2(src, voice_dir / fname)
    print("OK   Copied the voice page and server into " + str(voice_dir))

    config = {
        "tier": 0,
        "port": args.port,
        "root": str(root),
        "brain_cmd": brain_argv,
        "created": datetime.now(timezone.utc).isoformat(),
        "note": "Tier 0 - browser STT/TTS + reasoning CLI, no extra key. See skills/add-voice/references/tiers.md to go local-first or realtime.",
    }
    (voice_dir / "config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print("OK   Wrote voice/config.json (port " + str(args.port) + ", bound to this machine).")

    # 3. REFERENCE pointer
    refs = SKILL_DIR / "references"
    print("OK   Reference docs: " + str(refs))
    print("     - voice-model-disclaimer.md  (which model, what it costs, what it gets you)")
    print("     - tiers.md                   (go fully-local, or add realtime on a free key)")
    print("     - troubleshooting.md         (server not running, long-session errors, no key)")

    # Next steps - a numbered checklist, not a wall.
    url = "http://127.0.0.1:" + str(args.port) + "/"
    print("")
    print("Done. To use it:")
    print("  1. Start the server:  python voice/server.py")
    print("  2. It opens " + url + " in your browser.")
    print("  3. Hold the Talk button, speak, release. The OS answers out loud.")
    print("  4. 'Save last to brain' appends what you said to brain/log.md.")
    print("")
    print("Honest note: in Chrome/Edge the browser sends your audio to the browser vendor")
    print("to transcribe. No key, no cost, but not fully local. Go local-first with the")
    print("faster-whisper upgrade in references/tiers.md. Your brain files stay on disk.")

    if args.start:
        print("\nStarting the server now...")
        subprocess.run([sys.executable, str(voice_dir / "server.py"), "--port", str(args.port)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
