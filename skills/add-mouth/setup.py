# -*- coding: utf-8 -*-
"""
setup.py - wire a mouth (text-to-speech) onto THIS machine ("Add a mouth").

The background installer the add-mouth skill runs. It does the three jobs the capability
scaffold calls for, tailored to the user's machine:

  1. INSTALL  - the default (OS-native speech) needs NO pip install and NO key. It detects
                which mouths this machine can use right now: the OS-native voice (almost
                always), Piper (only if on PATH), ElevenLabs (only if a key is in .env).
  2. WIRE     - writes voice/mouth-config.json (the chosen engine, voice, locality) and
                copies the say helper into the gitignored voice/ folder.
  3. REFERENCE- points at references/mouth-options.md (the exact install and the cost and
                locality trade per engine) so the choice is correct for THIS user.

Accessibility floor: the default mouth speaks through the tools your operating system
already ships, on no extra subscription and no key. Piper is a free local upgrade;
ElevenLabs is the one paid option, never selected unless the user asks.

Reads:  the skill's runtime/ template (say.py) next to this file; .env for an ElevenLabs key.
Writes: <repo-root>/voice/  (say.py, mouth-config.json) - gitignored, yours.

No pip installs. Python standard library only.

Usage:
    python skills/add-mouth/setup.py                  # wire the OS-native default
    python skills/add-mouth/setup.py --engine piper    # wire Piper (must be on PATH)
    python skills/add-mouth/setup.py --engine elevenlabs --voice Rachel
"""

import argparse
import json
import os
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
RUNTIME_SRC = SKILL_DIR / "runtime"


def find_repo_root(start):
    """Walk up to the Founder OS repo root (the folder holding skills/ and CLAUDE.md)."""
    cur = start
    for _ in range(8):
        if (cur / "skills").is_dir() and (cur / "CLAUDE.md").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return SKILL_DIR.parent.parent


def os_native_tool():
    """Return (label, local?) for the operating system's built-in speech, if any."""
    system = platform.system()
    if system == "Windows":
        return "Windows SAPI (System.Speech)", True
    if system == "Darwin":
        return "macOS say", True
    # Linux: prefer spd-say, then espeak / espeak-ng.
    for tool in ("spd-say", "espeak-ng", "espeak"):
        if shutil.which(tool):
            return "Linux " + tool, True
    return None, True


def read_env_key(root, name):
    """Read a single key from <root>/.env without importing anything. Returns value or None."""
    env = root / ".env"
    if not env.exists():
        return None
    try:
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'") or None
    except OSError:
        return None
    return None


def main():
    ap = argparse.ArgumentParser(description="Wire a mouth (text-to-speech) for the OS.")
    ap.add_argument("--engine", choices=["os", "piper", "elevenlabs"], default="os",
                    help="os = the machine's built-in voice (default, no key); piper = free local upgrade; elevenlabs = paid")
    ap.add_argument("--voice", default=None, help="a voice name the chosen engine offers")
    args = ap.parse_args()

    print("Add a mouth - default is your machine's built-in voice (no key, no paid service)")
    print("-" * 58)

    if sys.version_info < (3, 8):
        print("FAIL: Python 3.8+ needed. Found " + sys.version.split()[0])
        return 1
    print("OK   Python " + sys.version.split()[0] + " - the default mouth needs no pip install.")

    root = find_repo_root(SKILL_DIR)

    # 1. INSTALL detection - what can this machine do right now.
    native_label, _ = os_native_tool()
    piper_path = shutil.which("piper")
    eleven_key = read_env_key(root, "ELEVENLABS_API_KEY")

    if native_label:
        print("OK   OS-native voice available: " + native_label + " (fully local, no key).")
    else:
        print("WARN No OS-native speech tool found. On Linux install espeak-ng or speech-dispatcher.")
    print(("OK   " if piper_path else "--   ") + "Piper " + ("found on PATH (free, fully local)." if piper_path else "not on PATH (free local upgrade - see references/mouth-options.md)."))
    print(("OK   " if eleven_key else "--   ") + "ElevenLabs key " + ("present in .env (paid, not local)." if eleven_key else "not set (paid option - 'connect elevenlabs' if you want it)."))

    # Resolve the engine against what is actually available; never silently pick paid.
    engine = args.engine
    local = True
    if engine == "piper" and not piper_path:
        print("\nNOTE Piper is not on PATH yet. Wiring the OS-native default instead; add Piper")
        print("     per references/mouth-options.md, then re-run with --engine piper.")
        engine = "os"
    if engine == "elevenlabs" and not eleven_key:
        print("\nNOTE No ElevenLabs key in .env. Wiring the OS-native default instead. Run")
        print("     'connect elevenlabs' (or python scripts/connect.py set-secret ELEVENLABS_API_KEY)")
        print("     then re-run with --engine elevenlabs. ElevenLabs is paid and not local.")
        engine = "os"
    if engine == "elevenlabs":
        local = False

    if engine == "os" and not native_label:
        print("\nFAIL: no OS-native speech tool and no working upgrade. Install one (espeak-ng on")
        print("      Linux), or add Piper, then re-run.")
        return 1

    # 2. WIRE
    voice_dir = root / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)

    say_src = RUNTIME_SRC / "say.py"
    if not say_src.exists():
        print("FAIL: missing runtime template " + str(say_src))
        return 1
    shutil.copy2(say_src, voice_dir / "say.py")
    print("OK   Copied the say helper into " + str(voice_dir / "say.py"))

    config = {
        "engine": engine,
        "voice": args.voice,
        "local": local,
        "os_native_label": native_label,
        "created": datetime.now(timezone.utc).isoformat(),
        "note": "Mouth config. engine=os uses your machine's built-in voice (free, local). "
                "piper is free and local; elevenlabs is paid and sends text to ElevenLabs. "
                "See skills/add-mouth/references/mouth-options.md.",
    }
    (voice_dir / "mouth-config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    locality = "local" if local else "NOT local (text goes to ElevenLabs)"
    print("OK   Wrote voice/mouth-config.json (engine: " + engine + ", " + locality + ").")

    # 3. REFERENCE + next steps
    print("")
    print("Done. To use it:")
    print('  1. Speak a line:      python voice/say.py "your three priorities today are ..."')
    print("  2. Read piped text:   echo \"read this back\" | python voice/say.py")
    print('  3. Render to a file:  python voice/say.py --out brief.wav "save this instead of speaking"')
    print("     (OS-native and Piper write .wav, .aiff on macOS; only ElevenLabs writes .mp3.)")
    print("")
    if engine == "elevenlabs":
        print("Cost note: ElevenLabs is a paid service and your text is sent to it to synthesize.")
        print("That is a deliberate choice. The OS-native and Piper voices stay free and local.")
    else:
        print("This mouth is free and runs on your machine. Your text does not leave it.")
    print("Full options and the per-engine trade: skills/add-mouth/references/mouth-options.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
