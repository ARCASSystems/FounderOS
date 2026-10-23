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
import locale
import os
import platform
import shutil
import subprocess
import sys
import tempfile
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
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                # The connect skill writes "paste-your-key-here" for the founder to
                # replace. Until they do, there is no key to send.
                if not value or value.lower().startswith(("paste-your", "your")):
                    return None
                return value
    except OSError:
        return None
    return None


# ---- Windows: PowerShell runs a FIXED script ------------------------------------------------
# The text and every path reach PowerShell as data, never as part of the command. Building the
# command by quoting the text failed twice over: PowerShell treats the curly quotes U+2018 to
# U+201B as quote marks too, so "I don't know" typed with a curly apostrophe ended the string
# (a parser error) and crafted text could run commands. Environment variables are read by
# PowerShell as plain strings, whatever they hold. The text itself goes through a UTF-8 file
# because a variable holds at most 32767 characters and a long brief can be longer.
PS_SPEAK = (
    "$ErrorActionPreference = 'Stop'; "
    "try { "
    "Add-Type -AssemblyName System.Speech; "
    "$t = [IO.File]::ReadAllText($env:FOS_SAY_TEXT_FILE, [Text.Encoding]::UTF8); "
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
    "if ($env:FOS_SAY_OUT) { $s.SetOutputToWaveFile($env:FOS_SAY_OUT) }; "
    "$s.Speak($t); $s.Dispose() "
    "} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
)

# Media.SoundPlayer plays WAV only. Handed an MP3 (the ElevenLabs output) it throws "not a
# valid wave file". MediaPlayer plays both. It opens the file in the background, so wait until
# it knows the length, play, and wait that long. A file it cannot open is an error, not silence.
PS_PLAY = (
    "$ErrorActionPreference = 'Stop'; "
    "try { "
    "Add-Type -AssemblyName PresentationCore; "
    "$p = New-Object System.Windows.Media.MediaPlayer; "
    "$p.Open([Uri]::new($env:FOS_SAY_PATH)); "
    "$n = 0; "
    "while (-not $p.NaturalDuration.HasTimeSpan -and $n -lt 50) { Start-Sleep -Milliseconds 100; $n++ }; "
    "if (-not $p.NaturalDuration.HasTimeSpan) { throw 'the audio file could not be opened' }; "
    "$p.Play(); "
    "Start-Sleep -Milliseconds ([int]$p.NaturalDuration.TimeSpan.TotalMilliseconds + 300); "
    "$p.Close() "
    "} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
)


def _powershell():
    return shutil.which("pwsh") or shutil.which("powershell")


def _run_powershell(script, extra_env):
    """Run one of the fixed scripts above with its data in the environment. Returns True on rc 0."""
    exe = _powershell()
    if not exe:
        print("say: no PowerShell found for Windows speech.", file=sys.stderr)
        return False
    env = dict(os.environ)
    env.update(extra_env)
    return subprocess.run([exe, "-NoProfile", "-NonInteractive", "-Command", script],
                          env=env).returncode == 0


def speak_os(text, voice, out):
    """Speak (or render) with the operating system's built-in voice. Returns True on success.

    The text never goes on a command line as an argument: on Windows it reaches PowerShell as
    data, on macOS and Linux it goes through stdin (or after "--"), so text that starts with "-"
    is spoken, not read as an option."""
    system = platform.system()
    if system == "Windows":
        fd, text_file = tempfile.mkstemp(prefix="fos-say-", suffix=".txt")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            return _run_powershell(PS_SPEAK, {"FOS_SAY_TEXT_FILE": text_file,
                                              "FOS_SAY_OUT": str(out) if out else ""})
        finally:
            try:
                os.remove(text_file)
            except OSError:
                pass
    data = text.encode("utf-8")
    if system == "Darwin":
        # With no message and no -f, say reads the text from stdin.
        cmd = ["say"]
        if voice:
            cmd += ["-v", voice]
        if out:
            cmd += ["-o", str(out)]
        return subprocess.run(cmd, input=data).returncode == 0
    # Linux
    espeak = shutil.which("espeak-ng") or shutil.which("espeak")
    if out:
        if espeak:
            return subprocess.run([espeak, "-b", "1", "--stdin", "-w", str(out)],
                                  input=data).returncode == 0
        print("say: rendering to a file on Linux needs espeak-ng or espeak.", file=sys.stderr)
        return False
    if shutil.which("spd-say"):
        # spd-say has no stdin mode; "--" ends its options, so the text is never one.
        return subprocess.run(["spd-say", "--", text]).returncode == 0
    if espeak:
        return subprocess.run([espeak, "-b", "1", "--stdin"], input=data).returncode == 0
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
        return _play(target)
    return True


def speak_elevenlabs(text, voice, out):
    """Synthesize with ElevenLabs (paid, NOT local) and save / play mp3. Needs a key in .env."""
    key = read_env_key("ELEVENLABS_API_KEY")
    if not key:
        print("say: ElevenLabs engine selected but no ELEVENLABS_API_KEY in .env.", file=sys.stderr)
        return False
    voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # a default public ElevenLabs voice id
    # Model ids come and go. Set "model" in voice/mouth-config.json to pin a different one;
    # list what your key actually exposes with a GET on https://api.elevenlabs.io/v1/models.
    model_id = load_config().get("model") or "eleven_multilingual_v2"
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
    body = json.dumps({"text": text, "model_id": model_id}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("xi-api-key", key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "audio/mpeg")
    target = out or (VOICE_DIR / "_say.mp3")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            Path(target).write_bytes(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print("say: ElevenLabs request failed (" + str(exc) + ") using model '" + model_id +
              "'. A 400 usually means that model id was retired - set a current one as \"model\" in "
              "voice/mouth-config.json (your key's list: https://api.elevenlabs.io/v1/models). A 402 "
              "means the voice needs a paid plan; ElevenLabs is the paid tier, so that is expected on "
              "a free account. Your machine's own voice still works: set \"engine\": \"os\".",
              file=sys.stderr)
        return False
    if not out:
        return _play(target)
    return True


# Linux players by what they can play. aplay and paplay take WAV only.
_LINUX_PLAYERS = {
    ".mp3": (("ffplay", ["-nodisp", "-autoexit", "-loglevel", "error"]), ("mpg123", ["-q"]),
             ("mpv", ["--no-video", "--really-quiet"])),
    ".wav": (("aplay", ["-q"]), ("paplay", []), ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "error"])),
}


def _play(path):
    """Play a rendered audio file on this machine. Returns True only when a player ran it and
    finished cleanly. On failure it says so and returns False, so the caller never reports
    "spoke" for audio nobody heard."""
    path = Path(path)
    system = platform.system()
    if system == "Windows":
        ok = _run_powershell(PS_PLAY, {"FOS_SAY_PATH": str(path)})
    elif system == "Darwin":
        ok = bool(shutil.which("afplay")) and subprocess.run(["afplay", str(path)]).returncode == 0
    else:
        ok = False
        for player, extra in _LINUX_PLAYERS.get(path.suffix.lower(), _LINUX_PLAYERS[".wav"]):
            if shutil.which(player):
                ok = subprocess.run([player] + extra + [str(path)]).returncode == 0
                break
    if not ok:
        print("say: made the audio (" + str(path) + ") but could not play it on this machine.",
              file=sys.stderr)
    return ok


def _holds_audio(path):
    """False when a rendered file has no sound in it: missing, empty, or a WAV or AIFF whose
    sample chunk is empty. Windows writes a 46-byte header-only WAV when the voice cannot read
    the text (Arabic with an English voice), and that used to be reported as success."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(12)
            if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
                order, want, skip = "little", b"data", 0
            elif head[:4] == b"FORM" and head[8:12] in (b"AIFF", b"AIFC"):
                order, want, skip = "big", b"SSND", 8  # 8 bytes of offset and block size first
            else:
                return len(head) > 0
            while True:
                chunk = fh.read(8)
                if len(chunk) < 8:
                    return False
                size = int.from_bytes(chunk[4:], order)
                if chunk[:4] == want:
                    fh.seek(skip, 1)
                    # A writer that never filled in the size still left samples after it.
                    return size > skip or bool(fh.read(1))
                fh.seek(size + (size & 1), 1)
    except OSError:
        return False


def _piped_text():
    """The piped text as UTF-8, whatever the console's codepage. Python decodes a Windows pipe
    as cp1252 unless PYTHONUTF8 is set, so a curly quote arrived as garbage and crashed the
    speech step. A pipe that is not UTF-8 is read in the machine's own encoding instead."""
    raw = getattr(sys.stdin, "buffer", None)
    if raw is None:  # already text (a test, or an embedding host)
        return sys.stdin.read()
    data = raw.read()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode(locale.getpreferredencoding(False), errors="replace")


def main():
    # Print UTF-8 whatever the console's codepage: an --out name in Arabic raised
    # UnicodeEncodeError on a Windows pipe after the file was already written.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Speak text, or render it to an audio file.")
    ap.add_argument("text", nargs="*", help="text to speak (omit to read from stdin)")
    ap.add_argument("--out", default=None, help="write audio to this file instead of speaking")
    args = ap.parse_args()

    text = " ".join(args.text).strip()
    if not text and not sys.stdin.isatty():
        text = _piped_text().strip()
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

    if out and not _holds_audio(out):
        # A header with no sound is not a recording. Take it away so no later step sends it.
        try:
            out.unlink()
        except OSError:
            pass
        print("No speech was made: this voice cannot read this text. Try a voice for that language.",
              file=sys.stderr)
        return 1

    local = engine in ("os", "piper")
    where = "on your machine (local)" if local else "via ElevenLabs (paid, not local)"
    action = "wrote " + str(out) if out else "spoke"
    print("say: " + action + " using the " + engine + " mouth, " + where + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
