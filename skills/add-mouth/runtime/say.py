# -*- coding: utf-8 -*-
"""
say.py - speak a line of text, or render it to an audio file, through the configured mouth.

Copied into the gitignored voice/ folder by skills/add-mouth/setup.py. Reads
voice/mouth-config.json to know which engine to use. Text comes from the command line or
from stdin (so any skill can pipe its output here).

Engines:
  os          your operating system's built-in voice - free, fully local, no key
              (Windows SAPI, macOS say, Linux spd-say / espeak)
  piper       Piper - free, fully local, better quality (must be on PATH)
  elevenlabs  ElevenLabs - paid, NOT local (text is sent to ElevenLabs); needs a key in .env

It always prints which engine spoke and whether that engine is local, so you are never
misled about where your text went. If the configured engine is missing, it falls back to the
OS-native voice with a plain message, never a traceback.

Python standard library only. No pip installs.

Usage:
    python voice/say.py "your three priorities today are ..."
    echo "read this back to me" | python voice/say.py
    python voice/say.py --out brief.wav "render this to a file instead of speaking"

The OS-native and Piper engines write WAV (AIFF on macOS); only ElevenLabs writes MP3.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

VOICE_DIR = Path(__file__).resolve().parent
ROOT = VOICE_DIR.parent


def load_config():
    cfg = VOICE_DIR / "mouth-config.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"engine": "os", "voice": None, "local": True}


def read_env_key(name):
    env = ROOT / ".env"
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


def speak_os(text, voice, out):
    """Speak (or render) with the operating system's built-in voice. Returns True on success."""
    system = platform.system()
    if system == "Windows":
        # System.Speech via PowerShell. Single-quote both the text and the path for PowerShell
        # (double any quote), so an apostrophe in either - C:\Users\O'Brien\, say - can neither
        # break the command nor inject.
        safe = text.replace("'", "''")
        if out:
            out_safe = str(out).replace("'", "''")
            ps = ("Add-Type -AssemblyName System.Speech; "
                  "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                  "$s.SetOutputToWaveFile('" + out_safe + "'); $s.Speak('" + safe + "'); $s.Dispose()")
        else:
            ps = ("Add-Type -AssemblyName System.Speech; "
                  "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('" + safe + "')")
        exe = shutil.which("pwsh") or shutil.which("powershell")
        if not exe:
            print("say: no PowerShell found for Windows speech.", file=sys.stderr)
            return False
        return subprocess.run([exe, "-NoProfile", "-Command", ps]).returncode == 0
    if system == "Darwin":
        cmd = ["say"]
        if voice:
            cmd += ["-v", voice]
        if out:
            cmd += ["-o", str(out)]
        cmd.append(text)
        return subprocess.run(cmd).returncode == 0
    # Linux
    if out:
        if shutil.which("espeak-ng") or shutil.which("espeak"):
            exe = shutil.which("espeak-ng") or shutil.which("espeak")
            return subprocess.run([exe, "-w", str(out), text]).returncode == 0
        print("say: rendering to a file on Linux needs espeak-ng or espeak.", file=sys.stderr)
        return False
    for exe in ("spd-say", "espeak-ng", "espeak"):
        if shutil.which(exe):
            return subprocess.run([exe, text]).returncode == 0
    print("say: no Linux speech tool found (install espeak-ng or speech-dispatcher).", file=sys.stderr)
    return False


def speak_piper(text, voice, out):
    """Render with Piper to a wav file, then play it if not asked to keep the file."""
    if not shutil.which("piper"):
        return False
    target = out or (VOICE_DIR / "_say.wav")
    model = voice  # a Piper voice is a model path; the user sets it in mouth-config.json
    cmd = ["piper", "--output_file", str(target)]
    if model:
        cmd += ["--model", str(model)]
    proc = subprocess.run(cmd, input=text.encode("utf-8"))
    if proc.returncode != 0:
        return False
    if not out:  # play it then leave the temp file in place (overwritten next time)
        _play(target)
    return True


def speak_elevenlabs(text, voice, out):
    """Synthesize with ElevenLabs (paid, NOT local) and save / play mp3. Needs a key in .env."""
    key = read_env_key("ELEVENLABS_API_KEY")
    if not key:
        print("say: ElevenLabs engine selected but no ELEVENLABS_API_KEY in .env.", file=sys.stderr)
        return False
    voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # a default public ElevenLabs voice id
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
    body = json.dumps({"text": text, "model_id": "eleven_monolingual_v1"}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("xi-api-key", key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "audio/mpeg")
    target = out or (VOICE_DIR / "_say.mp3")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            Path(target).write_bytes(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print("say: ElevenLabs request failed (" + str(exc) + ").", file=sys.stderr)
        return False
    if not out:
        _play(target)
    return True


def _play(path):
    """Best-effort local playback of a rendered audio file. Silent if no player is found."""
    system = platform.system()
    if system == "Windows":
        exe = shutil.which("pwsh") or shutil.which("powershell")
        if exe:
            path_safe = str(path).replace("'", "''")
            subprocess.run([exe, "-NoProfile", "-Command",
                            "(New-Object Media.SoundPlayer '" + path_safe + "').PlaySync()"])
        return
    if system == "Darwin":
        if shutil.which("afplay"):
            subprocess.run(["afplay", str(path)])
        return
    for player in ("aplay", "paplay", "ffplay"):
        if shutil.which(player):
            extra = ["-nodisp", "-autoexit"] if player == "ffplay" else []
            subprocess.run([player] + extra + [str(path)])
            return


def main():
    ap = argparse.ArgumentParser(description="Speak text, or render it to an audio file.")
    ap.add_argument("text", nargs="*", help="text to speak (omit to read from stdin)")
    ap.add_argument("--out", default=None, help="write audio to this file instead of speaking")
    args = ap.parse_args()

    text = " ".join(args.text).strip()
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    if not text:
        print("say: nothing to speak (pass text or pipe it in).", file=sys.stderr)
        return 1

    cfg = load_config()
    engine = cfg.get("engine", "os")
    voice = cfg.get("voice")
    out = Path(args.out).resolve() if args.out else None

    if out and engine in ("os", "piper") and out.suffix.lower() not in (".wav", ".aiff", ".aif", ""):
        print("say: the " + engine + " mouth writes WAV audio; the '" + out.suffix +
              "' extension is just the file name, not a conversion. Only ElevenLabs writes MP3.")

    handlers = {"os": speak_os, "piper": speak_piper, "elevenlabs": speak_elevenlabs}
    ok = handlers.get(engine, speak_os)(text, voice, out)

    if not ok and engine != "os":
        print("say: '" + engine + "' is not available right now - falling back to your machine's voice.")
        engine = "os"
        ok = speak_os(text, None, out)

    if not ok:
        print("say: could not speak. See skills/add-mouth/references/mouth-options.md.", file=sys.stderr)
        return 1

    local = engine in ("os", "piper")
    where = "on your machine (local)" if local else "via ElevenLabs (paid, not local)"
    action = "wrote " + str(out) if out else "spoke"
    print("say: " + action + " using the " + engine + " mouth, " + where + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
