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
  GET  /health      -> reports whether the brain CLI is reachable, so the page can degrade
                       honestly instead of dead-ending.

Every turn is logged one-JSON-line-per-turn to voice/runtime-log.jsonl (route, latency,
ok). That log is local-only and gitignored - it holds what you said.

Reads:  config.json (next to this file; written by setup.py) for port, repo root, and
        brain_cmd. Falls back to sane defaults if config is missing.
        <root>/core/identity.md (first lines only, if present) for a lean brain context.
Writes: <root>/brain/log.md (append, on /save)
        voice/runtime-log.jsonl (append, one line per turn)

No pip installs. No third-party APIs. Python standard library only
(http.server, json, subprocess, pathlib, datetime, argparse).

Usage:
    python server.py                 # reads config.json next to this file
    python server.py --port 8765     # override the port
    python server.py --no-browser    # do not open a browser window
"""

import argparse
import json
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
            self._send_json(
                {
                    "ok": True,
                    "brain_cmd": CONFIG.get("brain_cmd"),
                    "brain_available": brain_available(),
                    "root": str(ROOT),
                }
            )
            return
        self._send_json({"error": "not found"}, 404)

    def do_POST(self):
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
