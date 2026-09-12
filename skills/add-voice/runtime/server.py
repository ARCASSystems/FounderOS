# -*- coding: utf-8 -*-
"""
server.py - Tier-0 voice loop server for Founder OS (the "Add voice" capability).

The accessibility-floor spine: a tiny local web server, Python standard library only,
that lets a single local browser page talk to your OS out loud with NO extra API key
and NO paid service. It does three things:

  GET  /            -> serves the voice page (index.html sitting next to this file)
  POST /brain {text}-> answers a spoken turn using the reasoning CLI you already run the
                       OS in (default: the Claude Code CLI, `claude -p`). No API key: it
                       uses the subscription you already have. Context is kept LEAN on
                       purpose (a short preamble + a small identity slice, never the whole
                       repo) so a long session does not bloat and fail.
  POST /save {text} -> appends the spoken text to brain/log.md (the capture route). Needs
                       no model at all, so it works even with no reasoning CLI present.
  POST /transcribe  -> OPT-IN local ears. Takes raw audio bytes from the browser and
                       transcribes them with faster-whisper on this machine, so speech
                       never reaches a browser vendor. Off unless faster-whisper is
                       installed; answers {ok:false,reason} rather than failing, so the
                       page falls back to the browser's ears instead of dead-ending.
  POST /speak {text}-> OPT-IN local mouth. Renders speech with Piper and returns WAV. Same
                       contract: absent means {ok:false,reason} and the browser speaks.
  GET  /health      -> reports whether the brain CLI is reachable AND which ears and mouth
                       are actually usable right now, so the page can say what is active
                       rather than what is possible.

Every turn is logged one-JSON-line-per-turn to voice/runtime-log.jsonl (route, latency,
ok). That log is local-only and gitignored - it holds what you said.

Reads:  config.json (next to this file; written by setup.py) for port, repo root, and
        brain_cmd. Falls back to sane defaults if config is missing.
        <root>/core/identity.md (first lines only, if present) for a lean brain context.
Writes: <root>/brain/log.md (append, on /save)
        voice/runtime-log.jsonl (append, one line per turn)

Tier 0 needs no pip install and no third-party API: standard library only
(http.server, json, subprocess, pathlib, datetime, argparse). The two local upgrades are
imported lazily inside their own handlers and are never required to start the server, so
an install without them runs exactly as it always has.

Usage:
    python server.py                 # reads config.json next to this file
    python server.py --port 8765     # override the port
    python server.py --no-browser    # do not open a browser window
"""

import argparse
import json
import re
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PORT = 8765
BRAIN_TIMEOUT_S = 90  # a freeform answer can take a while; never hang forever
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # a recorder that never stops must not eat memory

# The lean brain preamble. Deliberately small - this is the guardrail against the
# "errors after a long session" failure: we do NOT load the whole OS per turn.
PREAMBLE = (
    "You are the spoken voice of a Founder OS - a plain-markdown operating system the "
    "user runs to keep track of their priorities, clients, decisions and week. Answer "
    "out loud in ONE or TWO short sentences, plainly, the way a sharp assistant would "
    "speak. No lists, no markdown, no preamble. If you genuinely do not know or the OS "
    "does not hold the answer, say so in one sentence rather than guessing."
)


def load_config():
    """Read config.json next to this file. Tolerate a missing or partial file."""
    cfg_path = HERE / "config.json"
    cfg = {}
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            cfg = {}
    cfg.setdefault("port", DEFAULT_PORT)
    # root defaults to the repo root (voice/ lives at the repo root, so parent of HERE).
    cfg.setdefault("root", str(HERE.parent))
    # brain_cmd is an argv list. The user's spoken text is appended as the final arg at
    # call time - no shell, so nothing in the text can be interpreted as a command.
    cfg.setdefault("brain_cmd", ["claude", "-p"])
    # The two local upgrades. Both default OFF: they need a package or a binary
    # that Tier 0 deliberately does not install, and a default that silently
    # needs an install is not a zero-install default.
    cfg.setdefault("local_stt", False)
    cfg.setdefault("local_stt_model", "base")
    cfg.setdefault("local_tts", False)
    cfg.setdefault("piper_cmd", "piper")
    cfg.setdefault("piper_voice", "")
    return cfg


CONFIG = load_config()
ROOT = Path(CONFIG["root"]).resolve()
RUNTIME_LOG = HERE / "runtime-log.jsonl"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def log_turn(route, latency_ms, ok, chars_in=0, chars_out=0, note=""):
    """One JSON line per turn. Local-only (voice/ is gitignored). Never raises."""
    try:
        line = json.dumps(
            {
                "ts": _now_iso(),
                "route": route,
                "latency_ms": round(latency_ms, 1),
                "ok": ok,
                "chars_in": chars_in,
                "chars_out": chars_out,
                "note": note,
            },
            ensure_ascii=True,
        )
        with RUNTIME_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass  # logging must never break a turn


def lean_context():
    """A SMALL slice of the OS for the brain - not the whole repo. Identity head only."""
    identity = ROOT / "core" / "identity.md"
    if not identity.exists():
        return ""
    try:
        head = identity.read_text(encoding="utf-8").splitlines()[:30]
    except OSError:
        return ""
    return "\n".join(head).strip()


def brain_available():
    """True if the configured reasoning CLI is on PATH. Cheap probe, no model call."""
    import shutil

    cmd = CONFIG.get("brain_cmd") or []
    if not cmd:
        return False
    return shutil.which(cmd[0]) is not None


def ask_brain(text):
    """Run one brain turn through the no-key reasoning CLI. Returns (answer, ok)."""
    cmd = list(CONFIG.get("brain_cmd") or ["claude", "-p"])
    ctx = lean_context()
    prompt = PREAMBLE
    if ctx:
        prompt += "\n\nWho the user is (for context, do not read aloud):\n" + ctx
    prompt += "\n\nThe user just said: " + text + "\n\nYour spoken reply:"
    argv = cmd + [prompt]
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=BRAIN_TIMEOUT_S,
            # Give the child an immediate EOF on stdin. Headless CLIs like `claude -p`
            # read piped stdin when it is not a TTY and will block forever waiting for
            # input that a web server never sends. DEVNULL makes them use only the argv
            # prompt and return at once - without this the loop hangs every turn.
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return (
            "I can hear you and I can save to your brain, but the reasoning command is "
            "not on this machine's PATH, so I cannot answer yet. See the troubleshooting "
            "note in the add-voice skill.",
            False,
        )
    except subprocess.TimeoutExpired:
        return ("That one took too long, so I stopped it. Try again or ask it shorter.", False)
    if proc.returncode != 0:
        err = (proc.stderr or "").strip().splitlines()
        tail = err[-1] if err else "unknown error"
        return ("The reasoning command returned an error: " + tail[:200], False)
    answer = (proc.stdout or "").strip()
    if not answer:
        return ("I did not get an answer back. Try asking again.", False)
    return (answer, True)


def append_to_log(text):
    """Append a spoken capture to brain/log.md. Returns (confirmation, ok)."""
    log_path = ROOT / "brain" / "log.md"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = "\n### " + stamp + " (voice capture)\n\n" + text.strip() + "\n"
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError as exc:
        return ("I could not write to your brain log: " + str(exc)[:120], False)
    return ("Saved to your log.", True)


# --------------------------------------------------------------- local ears --
# faster-whisper on this machine. The reason this tier exists: the browser's
# built-in recognition sends your audio to Google or Microsoft to turn into
# text. That is fine for most turns and it is stated on the page, but "most
# turns" is not all of them, and a founder talking about a client should be able
# to choose. Model loading is slow and once-only, so it is cached here.
_STT_MODEL = None
_STT_ERROR = ""

# Anything that looks like a filesystem location, ANYWHERE in the string.
#
# Two earlier versions of this were too clever. The first listed three shapes
# and missed four. The second anchored the posix branch on start-or-whitespace,
# which a quote character defeats - and Python quotes the path in almost every
# filesystem error it raises, so the single most common shape
# ("[Errno 2] No such file or directory: '/home/someone/...'") walked straight
# through. No anchors now: a slash-or-backslash separated path fragment of any
# depth counts, wherever it sits.
_PATHISH = re.compile(
    r"[A-Za-z]:[\\/]"                                  # C:\ or D:/
    r"|\\\\[^\\/]+[\\]"                               # \\server\share
    r"|/(?:home|users|root|tmp|var|mnt|media|opt|srv|private|volumes|app|data"
    r"|cache|export|usr|etc)/"
    r"|~[A-Za-z0-9._-]*/"                               # ~/ and ~someone/
    r"|\$HOME|%USERPROFILE%|%APPDATA%|%LOCALAPPDATA%"
    r"|[\\/][^\\/\s'\"]+[\\/][^\\/\s'\"]+[\\/]",      # any three-deep path
    re.IGNORECASE,
)


def _safe_error(raw: str) -> str:
    """An error a founder can act on, with no path in it.

    This string is printed on the page. A privacy tier that puts the account
    name on screen has missed its own point, so anything path-shaped is
    replaced wholesale rather than trimmed.
    """
    if _PATHISH.search(raw):
        return ("the local model could not be loaded - check the model name in "
                "voice/config.json and that the first download completed")
    return raw[:200]


def local_stt_status():
    """What the local ears can do right now. Never raises, never installs."""
    model_name = CONFIG.get("local_stt_model") or "base"
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        return {
            "available": False,
            "model": model_name,
            "reason": "faster-whisper is not installed",
            "how": "pip install faster-whisper",
        }
    # An import is not a working transcriber. A model name that does not exist
    # imports perfectly and then fails every turn, and the page was painting
    # "your speech stays on this machine" over ears that could not hear. Once a
    # load has failed, say so here rather than on the next recording.
    if _STT_ERROR:
        return {
            "available": False,
            "model": model_name,
            "reason": _STT_ERROR,
            "how": "check local_stt_model in voice/config.json",
        }
    return {"available": True, "model": model_name, "reason": "", "how": ""}


def _load_stt():
    """Load the model once. The first call also downloads it, which is slow."""
    global _STT_MODEL, _STT_ERROR
    if _STT_MODEL is not None or _STT_ERROR:
        return _STT_MODEL
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        _STT_ERROR = "faster-whisper is not installed"
        return None
    try:
        _STT_MODEL = WhisperModel(
            CONFIG.get("local_stt_model") or "base",
            device="cpu",
            compute_type="int8",
        )
    except Exception as exc:                      # a failed model download, a bad name
        _STT_ERROR = _safe_error(str(exc))
        return None
    return _STT_MODEL


def transcribe_audio(raw, suffix=".webm"):
    """Transcribe recorded audio locally. Returns (text, ok, note).

    Nothing leaves this machine on this path. The audio is written to a temp
    file because the decoder wants a path, and the file is deleted straight
    after whether or not the transcription worked.
    """
    import tempfile

    status = local_stt_status()
    if not status["available"]:
        return ("", False, status["reason"])
    model = _load_stt()
    if model is None:
        return ("", False, _STT_ERROR or "the local model could not be loaded")

    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="founderos-voice-")
        with __import__("os").fdopen(fd, "wb") as fh:
            fh.write(raw)
        segments, _info = model.transcribe(tmp_path, beam_size=1, vad_filter=True)
        text = " ".join(seg.text.strip() for seg in segments).strip()
    except Exception as exc:
        # Never echo the decoder's message. It carries the temp path, which
        # carries the account name, and this string is printed on the page - a
        # privacy tier that puts your username on screen has missed the point.
        note = "that recording could not be decoded"
        if "Invalid data" not in str(exc) and "moov atom" not in str(exc):
            note = "the local transcriber failed on that recording"
        return ("", False, note)
    finally:
        if tmp_path:
            try:
                __import__("os").remove(tmp_path)
            except OSError:
                pass
    if not text:
        return ("", False, "nothing recognised in that audio")
    return (text, True, "")


# -------------------------------------------------------------- local mouth --

# A turn that failed is the only hard evidence about whether Piper works. A
# binary on PATH and a file on disk are not, which is how the page came to paint
# "a local voice speaks" over a mouth that could not.
_TTS_ERROR: list = []


def local_tts_status():
    """Whether Piper can speak on this machine right now."""
    import shutil

    if _TTS_ERROR:
        return {
            "available": False,
            "reason": _TTS_ERROR[-1],
            "how": "check piper_cmd and piper_voice in voice/config.json",
        }
    cmd = CONFIG.get("piper_cmd") or "piper"
    if shutil.which(cmd) is None:
        return {
            "available": False,
            "reason": "the piper command is not on PATH",
            "how": "install Piper: https://github.com/rhasspy/piper",
        }
    voice = CONFIG.get("piper_voice") or ""
    if not voice:
        return {
            "available": False,
            "reason": "no piper_voice set in voice/config.json",
            "how": "download a voice model and set piper_voice to its .onnx path",
        }
    if not Path(voice).exists():
        return {
            "available": False,
            "reason": "the piper voice file named in config.json is not there",
            "how": "fix piper_voice in voice/config.json",
        }
    return {"available": True, "reason": "", "how": ""}


def synthesize(text):
    """Render speech with Piper. Returns (wav_bytes, ok, note)."""
    status = local_tts_status()
    if not status["available"]:
        return (b"", False, status["reason"])
    argv = [CONFIG.get("piper_cmd") or "piper",
            "--model", CONFIG.get("piper_voice"),
            "--output_file", "-"]
    try:
        proc = subprocess.run(argv, input=text.encode("utf-8"),
                              capture_output=True, timeout=60)
    except FileNotFoundError:
        return (b"", False, "the piper command disappeared between the check and the call")
    except subprocess.TimeoutExpired:
        return (b"", False, "piper took too long")
    if proc.returncode != 0 or not proc.stdout:
        err = (proc.stderr or b"").decode("utf-8", "replace").strip().splitlines()
        # Through the same scrubber as the ears. Piper names the voice file it
        # could not load, which is a full path to the founder's home directory,
        # and this string reaches the page and the runtime log. Fixing the ears
        # and leaving the mouth is the instance-not-class mistake that
        # rules/release-verification.md gate 3 exists to stop.
        note = _safe_error(err[-1] if err else "piper returned nothing")
        _TTS_ERROR.append(note)
        return (b"", False, note)
    return (proc.stdout, True, "")


class Handler(BaseHTTPRequestHandler):
    # quiet the default per-request stderr spam
    def log_message(self, *args):
        return

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            length = 0
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            page = HERE / "index.html"
            if not page.exists():
                self._send_json({"error": "index.html missing next to server.py"}, 500)
                return
            body = page.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/health":
            stt = local_stt_status()
            tts = local_tts_status()
            # "active" is what is running this second, not what could be
            # installed. The page prints this, and a page that says "local" when
            # the audio is going to a browser vendor is the one thing this tier
            # must never do.
            self._send_json(
                {
                    "ok": True,
                    "brain_cmd": CONFIG.get("brain_cmd"),
                    "brain_available": brain_available(),
                    "root": str(ROOT),
                    "local_stt": stt,
                    "local_tts": tts,
                    "ears_active": "local" if (CONFIG.get("local_stt") and stt["available"])
                                   else "browser",
                    "mouth_active": "local" if (CONFIG.get("local_tts") and tts["available"])
                                    else "browser",
                }
            )
            return
        self._send_json({"error": "not found"}, 404)

    def _read_raw(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            length = 0
        if length <= 0 or length > MAX_AUDIO_BYTES:
            return b""
        return self.rfile.read(length)

    def do_POST(self):
        if self.path == "/transcribe":
            raw = self._read_raw()
            if not raw:
                self._send_json({"ok": False, "reason": "no audio received"})
                return
            ctype = (self.headers.get("Content-Type") or "").lower()
            suffix = (".ogg" if "ogg" in ctype else ".mp4" if "mp4" in ctype
                      else ".wav" if "wav" in ctype else ".webm")
            t0 = time.time()
            text, ok, note = transcribe_audio(raw, suffix)
            ms = (time.time() - t0) * 1000.0
            # The log records that a local turn happened and how long it took.
            # It never records the audio, and the text it records is the same
            # text /brain would have logged anyway.
            log_turn("transcribe", ms, ok, len(raw), len(text), note)
            # recheck tells the page to re-read /health: the ears it is
            # advertising have just proved they do not work.
            self._send_json({"ok": ok, "text": text, "reason": note,
                             "engine": "faster-whisper", "recheck": bool(_STT_ERROR),
                             "latency_ms": round(ms, 1)})
            return

        if self.path == "/speak":
            data = self._read_body()
            said = (data.get("text") or "").strip()
            if not said:
                self._send_json({"ok": False, "reason": "nothing to say"})
                return
            t0 = time.time()
            wav, ok, note = synthesize(said)
            ms = (time.time() - t0) * 1000.0
            log_turn("speak", ms, ok, len(said), len(wav), note)
            if not ok:
                # recheck, exactly as /transcribe does: the mouth the page is
                # advertising has just proved it does not work.
                self._send_json({"ok": False, "reason": note, "recheck": True})
                return
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(wav)))
            self.end_headers()
            self.wfile.write(wav)
            return

        data = self._read_body()
        text = (data.get("text") or "").strip()
        if self.path == "/brain":
            if not text:
                self._send_json({"answer": "I did not catch that.", "ok": False})
                return
            t0 = time.time()
            answer, ok = ask_brain(text)
            ms = (time.time() - t0) * 1000.0
            log_turn("brain", ms, ok, len(text), len(answer))
            self._send_json({"answer": answer, "ok": ok, "latency_ms": round(ms, 1)})
            return
        if self.path == "/save":
            t0 = time.time()
            confirm, ok = append_to_log(text)
            ms = (time.time() - t0) * 1000.0
            log_turn("save", ms, ok, len(text), 0)
            self._send_json({"answer": confirm, "ok": ok})
            return
        self._send_json({"error": "not found"}, 404)


def main():
    ap = argparse.ArgumentParser(description="Tier-0 Founder OS voice loop server.")
    ap.add_argument("--port", type=int, default=CONFIG.get("port", DEFAULT_PORT))
    ap.add_argument("--no-browser", action="store_true", help="do not open a browser")
    args = ap.parse_args()

    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = "http://127.0.0.1:" + str(args.port) + "/"
    print("Founder OS voice (Tier 0) serving at " + url)
    print("Brain command: " + " ".join(CONFIG.get("brain_cmd") or []) +
          ("  [reachable]" if brain_available() else "  [NOT on PATH - ears+save still work]"))
    stt, tts = local_stt_status(), local_tts_status()
    print("Ears:  " + ("local (faster-whisper, " + stt["model"] + ")"
                       if CONFIG.get("local_stt") and stt["available"]
                       else "browser (audio goes to your browser vendor)"
                            + ("" if stt["available"] else "  [local: " + stt["reason"] + "]")))
    print("Mouth: " + ("local (piper)" if CONFIG.get("local_tts") and tts["available"]
                       else "browser" + ("" if tts["available"] else "  [local: " + tts["reason"] + "]")))
    print("Press Ctrl+C to stop.")
    if not args.no_browser:
        threading.Thread(target=lambda: (time.sleep(0.6), webbrowser.open(url)), daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        httpd.shutdown()


if __name__ == "__main__":
    sys.exit(main())
