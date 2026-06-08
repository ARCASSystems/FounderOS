# -*- coding: utf-8 -*-
"""
setup_realtime.py - wire the Tier-1 REALTIME voice capability ("Add voice --realtime").

This is the opt-in upgrade that sits on top of Tier 0. Where Tier 0 needs no key and no
install, Tier 1 is a streaming conversation with a realtime model (Gemini Live), so it does
need two things, and it tells you BOTH up front - never after:

  1. A FREE Google AI Studio key. A free key carries a free daily quota on Flash models;
     heavy realtime use can move you onto paid per-token rates. (The disclaimer prints first.)
  2. Two Python packages: google-genai and websockets. This is a real install on your machine.

It does the three jobs the capability scaffold calls for, tailored to your machine:

  1. DISCLAIM  - print the cost + accuracy trade before doing anything (load-bearing, not boilerplate).
  2. INSTALL   - pip install google-genai + websockets (skippable with --no-install).
  3. WIRE      - copy the realtime page + bridge into the gitignored voice/ runtime, write
                 voice/realtime-config.json (model, voice, ports, key names, and the no-key
                 brain command inherited from Tier 0), and check whether a key is present.

Your brain stays local. Only the live conversation streams. Nothing here phones home except
the model call you opt into with your own key.

Reads:  realtime/ templates next to this file; voice/config.json (Tier-0, for the brain command).
Writes: <repo-root>/voice/ (live_server.py, live.html, realtime-config.json) - gitignored, yours.

Usage:
    python skills/add-voice/setup_realtime.py                 # disclaim, install, wire
    python skills/add-voice/setup_realtime.py --no-install     # wire only (deps already present)
    python skills/add-voice/setup_realtime.py --voice Puck --model gemini-live-2.5-flash-native-audio
    python skills/add-voice/setup_realtime.py --start          # wire, then start the server now
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
RUNTIME_SRC = SKILL_DIR / "realtime"

DEFAULT_MODEL = "gemini-2.5-flash-native-audio-latest"
DEFAULT_VOICE = "Aoede"

DISCLAIMER = """\
================  REALTIME VOICE - READ THIS BEFORE YOU INSTALL  ================
The model you talk to runs in the cloud. This is the one trade to understand:

  COST     A FREE Google AI Studio key has a free DAILY quota on Flash models.
           Realtime audio is billed per token past that quota (~$1 / 1M input
           tokens at time of writing). Heavy use can move a free key onto paid
           rates. The model you pick changes the cost - keep it on a Flash
           native-audio model unless you mean to spend.

  ACCURACY Realtime turn-taking is strong and sub-second. Accuracy still varies
           with accents, noise, and jargon, as any speech model does.

  PRIVACY  Your audio and the live conversation stream to Google to run the
           model. Your BRAIN - your markdown files and the answers read from
           them - stays on this machine. Only the conversation leaves.

If you would rather not stream audio or risk any cost, stop here and stay on
Tier 0 (no key, no install). Full detail: references/voice-model-disclaimer.md
================================================================================
"""


def find_repo_root(start):
    cur = start
    for _ in range(8):
        if (cur / "skills").is_dir() and (cur / "CLAUDE.md").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return SKILL_DIR.parent.parent  # skills/add-voice -> skills -> root


def detect_brain(root):
    """Inherit the no-key reasoning CLI Tier 0 detected; else probe PATH; else default claude -p."""
    cfg = root / "voice" / "config.json"
    if cfg.exists():
        try:
            cmd = json.loads(cfg.read_text(encoding="utf-8")).get("brain_cmd")
            if cmd:
                return cmd, "inherited from Tier-0 voice/config.json"
        except (ValueError, OSError):
            pass
    for name, argv in (("claude", ["claude", "-p"]), ("codex", ["codex", "exec"]), ("gemini", ["gemini", "-p"])):
        if shutil.which(name):
            return argv, "detected on PATH"
    return ["claude", "-p"], "default (no CLI found on PATH - confirm before relying on the brain)"


def key_present(root):
    """True if a Gemini key looks present in .env. Never prints or returns the value."""
    env = root / ".env"
    if not env.exists():
        return False
    for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY") and "=" in line:
            val = line.split("=", 1)[1].strip().strip('"').strip("'")
            if val and not val.lower().startswith("your"):
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Wire the Tier-1 realtime voice capability.")
    ap.add_argument("--no-install", action="store_true", help="skip pip install (deps already present)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    ap.add_argument("--http-port", type=int, default=8756)
    ap.add_argument("--ws-port", type=int, default=8757)
    ap.add_argument("--start", action="store_true", help="start the realtime server after wiring")
    args = ap.parse_args()

    # 1. DISCLAIM - before anything else.
    print(DISCLAIMER)

    if sys.version_info < (3, 9):
        print("FAIL: Python 3.9+ needed for the realtime SDK. Found " + sys.version.split()[0])
        return 1

    root = find_repo_root(SKILL_DIR)

    # 2. INSTALL
    if args.no_install:
        print("OK   Skipping pip install (--no-install). Assuming google-genai + websockets are present.")
    else:
        print("Installing google-genai + websockets (this is a real install on your machine)...")
        rc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "google-genai", "websockets"],
        ).returncode
        if rc != 0:
            print("WARN pip install did not finish cleanly. Re-run, or install manually:")
            print("       python -m pip install google-genai websockets")
            print("     Wiring will continue; the server needs these two packages to run.")
        else:
            print("OK   Installed google-genai + websockets.")

    # 3. WIRE
    voice_dir = root / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("live_server.py", "live.html"):
        src = RUNTIME_SRC / fname
        if not src.exists():
            print("FAIL: missing runtime template " + str(src))
            return 1
        shutil.copy2(src, voice_dir / fname)
    print("OK   Copied the realtime page and bridge into " + str(voice_dir))

    brain_cmd, brain_note = detect_brain(root)
    config = {
        "tier": 1,
        "model": args.model,
        "voice": args.voice,
        "http_port": args.http_port,
        "ws_port": args.ws_port,
        "key_names": ["GEMINI_API_KEY", "GEMINI_API_KEY2"],
        "brain_cmd": brain_cmd,
        "proactive_context": False,
        "created": datetime.now(timezone.utc).isoformat(),
        "note": "Tier 1 - Gemini Live realtime front + your no-key CLI as the back-brain. "
                "See skills/add-voice/references/realtime-architecture.md.",
    }
    (voice_dir / "realtime-config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print("OK   Wrote voice/realtime-config.json (model " + args.model + ", voice " + args.voice + ").")
    print("     Back-brain command: " + " ".join(brain_cmd) + "  (" + brain_note + ")")

    # Key check - guide, never store a key here (the connect flow owns that, stdin-only).
    if key_present(root):
        print("OK   A Google AI Studio key is present in .env.")
    else:
        print("WARN No Google AI Studio key found in .env. The OS ships no key - you add your own FREE one,")
        print("     and everything else is already wired so you only drop it in:")
        print("       1. Get your own free key: https://aistudio.google.com/apikey")
        print("       2. Say 'connect gemini', or run:")
        print("          python scripts/connect.py set-secret GEMINI_API_KEY   (paste the key on stdin)")
        print("       It is your key in your own Google account; it lands only in the gitignored .env.")

    print("")
    print("Done. To use it:")
    print("  1. Start the realtime server:  python voice/live_server.py")
    print("  2. It serves http://127.0.0.1:" + str(args.http_port) + "/live - open it.")
    print("  3. Tap the orb, allow the mic, and talk. Say 'thinking' to take the floor; it waits.")
    print("  4. Every turn is recorded locally to voice/live-log.md (gitignored).")
    print("  Token + latency report for a session:  python voice/live_server.py --summary")
    print("  Check which Live models your key exposes:  python voice/live_server.py --models")

    if args.start:
        if not key_present(root):
            print("\nNot starting - add a key first (see above), then: python voice/live_server.py")
            return 0
        print("\nStarting the realtime server now...")
        subprocess.run([sys.executable, str(voice_dir / "live_server.py")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
