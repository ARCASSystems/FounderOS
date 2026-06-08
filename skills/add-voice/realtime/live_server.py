#!/usr/bin/env python3
"""
Realtime voice front for Founder OS - Tier 1 of the "Add voice" capability.

This is the OPT-IN realtime upgrade that sits ON TOP of the Tier-0 loop. Where Tier 0 is a
press-and-release round-trip (browser STT -> your reasoning CLI -> browser TTS), Tier 1 is a
single streaming conversation: your mic flows continuously to a realtime model (Gemini Live),
it decides turns with native voice-activity detection, and its voice streams straight back -
sub-second, with true barge-in. No "give me a moment", because the front just starts talking.

Two models, two jobs (the load-bearing idea):
  - The FRONT is the realtime model. It holds the conversation, hears you, takes turns, speaks.
    It does NOT hold your OS.
  - The BACK-BRAIN is the no-key reasoning CLI you already run the OS in (claude -p / codex /
    gemini - whatever Tier 0 detected). The front reaches for it through the query_brain tool
    whenever a real fact about your OS is needed. The brain reads your local markdown files;
    only the live conversation streams to the cloud.

Topology (the session lives server-side so your API key never touches the browser, and the
tools run the real OS reads right here):

    browser mic  --16kHz PCM-->  this bridge (:8757 WS)  --->  Gemini Live
    browser <--24kHz PCM audio--      "                  <---       "  (native voice)

Accessibility floor: Tier 1 needs ONE free Google AI Studio key. A free key carries a free
daily quota on Flash models; heavy realtime use can move you onto paid per-token rates. The
disclaimer (references/voice-model-disclaimer.md) states this before you commit. Your brain
stays local.

Run:  python voice/live_server.py        then open http://127.0.0.1:8756/live
Stop: Ctrl+C
Report a session's latency + token cost:  python voice/live_server.py --summary

Requires (installed by setup_realtime.py, NOT by Tier 0): google-genai, websockets.
"""

import argparse
import asyncio
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
# voice/live_server.py lives at the repo root's voice/ when installed; the realtime template
# lives at skills/add-voice/realtime/. Either way the repo root is found by walking up.
PAGE = HERE / "live.html"

DEFAULT_HTTP_PORT = 8756
DEFAULT_WS_PORT = 8757
# A Flash native-audio Live model: free-tier eligible on an AI Studio key (within the daily
# quota), and it speaks in Gemini's own voice so we need no extra text-to-speech dependency.
# This is the stable "-latest" alias; if your key does not expose it, run
# `python voice/live_server.py --models` to see what it does, then set yours in realtime-config.json.
DEFAULT_MODEL = "gemini-2.5-flash-native-audio-latest"
DEFAULT_VOICE = "Aoede"   # a Gemini prebuilt voice; others: Puck, Charon, Kore, Fenrir, Leda, Orus, Zephyr
BRAIN_TIMEOUT_S = 90


def find_repo_root(start: Path) -> Path:
    """Walk up to the Founder OS repo root (the folder holding CLAUDE.md and skills/)."""
    cur = start
    for _ in range(8):
        if (cur / "CLAUDE.md").exists() and (cur / "skills").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.parent  # voice/ sits at the repo root, so one up is the usual answer


ROOT = find_repo_root(HERE)
VOICE_DIR = HERE if HERE.name == "voice" else (ROOT / "voice")
CONFIG_PATH = VOICE_DIR / "realtime-config.json"
TIER0_CONFIG = VOICE_DIR / "config.json"   # Tier-0 setup.py wrote the detected brain_cmd here
ENV_PATH = ROOT / ".env"
LIVE_TELEMETRY = VOICE_DIR / "live-telemetry.jsonl"   # one JSON line per turn (machine)
LIVE_LOG = VOICE_DIR / "live-log.md"                  # readable transcript (human, local-only)


def load_config() -> dict:
    """Read realtime-config.json (written by setup_realtime.py). Tolerate missing/partial.
    brain_cmd falls back to the Tier-0 config so the realtime front uses the same no-key CLI."""
    cfg = {}
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            cfg = {}
    cfg.setdefault("model", DEFAULT_MODEL)
    cfg.setdefault("voice", DEFAULT_VOICE)
    cfg.setdefault("http_port", DEFAULT_HTTP_PORT)
    cfg.setdefault("ws_port", DEFAULT_WS_PORT)
    cfg.setdefault("key_names", ["GEMINI_API_KEY", "GEMINI_API_KEY2"])
    # Off by default. The experimental proactive-context seam (see inject_context below).
    cfg.setdefault("proactive_context", False)
    if "brain_cmd" not in cfg:
        brain = ["claude", "-p"]
        if TIER0_CONFIG.exists():
            try:
                brain = json.loads(TIER0_CONFIG.read_text(encoding="utf-8")).get("brain_cmd", brain)
            except (ValueError, OSError):
                pass
        cfg["brain_cmd"] = brain
    return cfg


CONFIG = load_config()


# ---- the generic persona (NO proper name shipped - you name your own) -------------------------
# A user-authored voice/persona.md (gitignored, optional) overrides the body. The behaviour
# rules below always apply - they are what make this an instant, on-camera host, not a search box.
DEFAULT_PERSONA = (
    "You are the spoken voice of the user's Founder OS - a plain-markdown operating system they "
    "run to track their priorities, clients, decisions and week. You have no name unless they give "
    "you one. You are a calm, precise host, not a search box."
)

BEHAVIOUR_RULES = (
    "\n\nHOW YOU SPEAK (this is heard aloud, never read):\n"
    "- One to three short, natural sentences. Never lists, never markdown, never headings.\n"
    "- Answer first, then at most one concrete next step. Stop. Do not fill air.\n\n"
    "ENGAGE INSTANTLY - this is the whole point of realtime. On EVERY turn, respond at once: "
    "acknowledge, reflect back, ask a sharp question, or narrate what you are about to do. NEVER "
    "stall with 'give me a moment' or 'let me see' as dead air. If a tool will take a beat, say a "
    "short natural line ('let me pull that up') and the tool runs while you have already spoken.\n"
    "THE ONE EXCEPTION - the floor is theirs on request: if the user says 'thinking' (or 'let me "
    "think', 'hold on', 'give me a second', 'one moment') OUT LOUD, they are taking the floor. Go "
    "quiet and wait. Do not prompt them. Resume only when they speak again. You pause ONLY when "
    "they ask for it, never because you are slow.\n\n"
    "THE ROOM - you may be on camera, or a third person (an audience, a client) may be present. "
    "It is a three-way conversation: the operator, you, and whoever else is in the room. Keep it "
    "alive and human. Address the operator, but stay aware there may be others listening.\n\n"
    "CHARACTER - you are honest, not a yes-man. When the operator is about to do something that "
    "cuts against what they themselves said they wanted, say so plainly and briefly, then let them "
    "decide. Reflect their own stated values back when they drift. The honesty is the value; you "
    "are never useful by flattering. Keep cost and feasibility grounded - if something is expensive "
    "or unlikely to work, say it in a sentence.\n\n"
    "TOOLS - they act on the real OS:\n"
    "- For ANY factual question about their business - pipeline, clients, decisions, priorities, "
    "what is or is not done, the state of anything - you MUST call query_brain. NEVER answer a "
    "business fact from memory; you will be wrong. query_brain reads their actual files.\n"
    "- query_brain takes a few seconds. The instant you decide to call it, say a short natural line "
    "first ('let me check') so there is never silence, then answer from what it returns.\n"
    "- show_today / show_this_week read the cadence files. save_to_brain appends a note to their "
    "log (a safe, reversible capture). what_changed reports the working-tree git status.\n"
    "- After a tool runs, relay its result naturally in your own voice. Do not read it robotically.\n"
    "- You have NO power to send messages, delete, or control the machine. Those are a separate, "
    "gated capability ('add hands'). If asked, say plainly you cannot do that yet."
)


def system_instruction() -> str:
    persona = DEFAULT_PERSONA
    custom = VOICE_DIR / "persona.md"
    if custom.exists():
        try:
            body = custom.read_text(encoding="utf-8").strip()
            if body:
                persona = body
        except OSError:
            pass
    return persona + BEHAVIOUR_RULES


# ---- the back-brain: the no-key reasoning CLI, reading the local markdown OS --------------------
def _run_brain(prompt: str) -> str:
    """Shell the configured no-key reasoning CLI with cwd at the repo root so it can read the OS
    files itself. Lean by design: we pass the directive + the question, not the whole repo. Returns
    a spoken-style answer or a short honest failure line. Never raises."""
    cmd = list(CONFIG.get("brain_cmd") or ["claude", "-p"])
    if not shutil.which(cmd[0]):
        return ("I can hear you, but the reasoning command that reads your files is not on this "
                "machine's PATH, so I cannot answer business facts yet.")
    argv = cmd + [prompt]
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=BRAIN_TIMEOUT_S,
            cwd=str(ROOT),
            # Headless CLIs read piped stdin when it is not a TTY and block forever waiting for
            # input a server never sends. DEVNULL gives an immediate EOF so they use only the argv.
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return "That one took too long, so I stopped it. Ask it shorter, or try again."
    except OSError as exc:
        return "The reasoning command would not start: " + str(exc)[:120]
    if proc.returncode != 0:
        tail = ((proc.stderr or "").strip().splitlines() or ["unknown error"])[-1]
        return "The reasoning command returned an error: " + tail[:160]
    return (proc.stdout or "").strip() or "I did not get an answer back from the brain. Try again."


def _t_query_brain(args: dict) -> str:
    q = (args.get("question") or "").strip()
    if not q:
        return "I did not catch the question."
    directive = (
        "You are the back-brain of a spoken Founder OS. Answer the user's question from the markdown "
        "files in this folder (core/, context/, cadence/, brain/). Reply in ONE or TWO short spoken "
        "sentences, plain, no markdown, no lists. If the files do not hold the answer, say so in one "
        "sentence rather than guessing. Question: " + q
    )
    return _run_brain(directive)


def _read_head(rel: str, lines: int, label: str) -> str:
    p = ROOT / rel
    if not p.exists():
        return f"There is no {label} file yet."
    try:
        head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:lines]).strip()
    except OSError:
        return f"I could not read your {label} file."
    return head or f"Your {label} file is empty."


def _t_show_today(args: dict) -> str:
    return _read_head("cadence/daily-anchors.md", 12, "daily anchor")


def _t_show_this_week(args: dict) -> str:
    return _read_head("cadence/weekly-commitments.md", 14, "weekly commitments")


def _t_save_to_brain(args: dict) -> str:
    text = (args.get("text") or "").strip()
    if not text:
        return "There was nothing to save."
    log_path = ROOT / "brain" / "log.md"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write("\n### " + stamp + " (voice capture)\n\n" + text + "\n")
    except OSError as exc:
        return "I could not write to your log: " + str(exc)[:120]
    return "Saved to your log."


def _t_what_changed(args: dict) -> str:
    if not shutil.which("git"):
        return "Git is not on this machine, so I cannot see what changed."
    try:
        out = subprocess.run(
            ["git", "status", "--short"], cwd=str(ROOT), capture_output=True, text=True, timeout=15,
            stdin=subprocess.DEVNULL,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "I could not read the git status."
    if not out:
        return "Nothing has changed in the working tree - it is clean."
    n = len(out.splitlines())
    return f"{n} file{'s' if n != 1 else ''} changed in the working tree right now."


TOOL_HANDLERS = {
    "query_brain": _t_query_brain,
    "show_today": _t_show_today,
    "show_this_week": _t_show_this_week,
    "save_to_brain": _t_save_to_brain,
    "what_changed": _t_what_changed,
}


def build_live_config():
    """Built lazily so the module imports even without google-genai (for --summary)."""
    from google.genai import types

    def decl(name, desc, str_args=None):
        params = None
        if str_args:
            params = types.Schema(
                type=types.Type.OBJECT,
                properties={k: types.Schema(type=types.Type.STRING, description=v)
                            for k, v in str_args.items()},
                required=list(str_args.keys()),
            )
        return types.FunctionDeclaration(name=name, description=desc, parameters=params)

    decls = [
        decl("query_brain",
             "Answer ANY factual question about the user's business or OS - pipeline, clients, "
             "decisions, priorities, status of anything. Reads their real markdown files. Slower "
             "(a few seconds): say a short 'let me check' before calling.",
             {"question": "The user's question, phrased plainly"}),
        decl("show_today", "Read today's anchor and focus from the OS. Use for 'what's today', 'my day'."),
        decl("show_this_week", "Read this week's commitments. Use for 'this week', 'the week ahead'."),
        decl("save_to_brain", "Append a short note to the user's brain log (a safe, reversible "
             "capture). Use when they say 'save this', 'note that', 'remember this'.",
             {"text": "The note to save, in the user's words"}),
        decl("what_changed", "Report what files changed in the working tree right now. Use for "
             "'what changed', 'what did you do'."),
    ]
    tools = [types.Tool(function_declarations=decls)]

    return types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=types.Content(parts=[types.Part(text=system_instruction())]),
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=CONFIG.get("voice", DEFAULT_VOICE))
            )
        ),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        realtime_input_config=types.RealtimeInputConfig(
            # Native endpointing - what kills the fragmentation. ~700ms of silence = you are done.
            automatic_activity_detection=types.AutomaticActivityDetection(silence_duration_ms=700),
        ),
        # A long conversation otherwise hits the context cap and stalls; a sliding window keeps it
        # alive by compressing older turns. This is the guardrail against "errors after a long session".
        context_window_compression=types.ContextWindowCompressionConfig(sliding_window=types.SlidingWindow()),
        tools=tools,
    )


# ---- keys: one free key is enough; a second is optional headroom we rotate to on quota ----------
def load_keys() -> list:
    names = CONFIG.get("key_names") or ["GEMINI_API_KEY", "GEMINI_API_KEY2"]
    found, seen = [], set()
    # .env first (gitignored), then real environment.
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    for name in names:
        val = env.get(name) or os.environ.get(name, "")
        val = val.strip()
        if val and not val.lower().startswith("your") and val not in seen:
            found.append(val)
            seen.add(val)
    return found


def _is_quota(exc) -> bool:
    m = str(exc)
    return any(s in m for s in ("RESOURCE_EXHAUSTED", "429", "quota", "PERMISSION_DENIED",
                                "403", "401", "API key"))


# ---- per-turn transcript + telemetry (local-only; voice/ is gitignored) -------------------------
def _usage(um):
    if not um:
        return None

    def by_mod(details):
        out = {}
        for d in (details or []):
            out[str(getattr(d, "modality", "?")).split(".")[-1]] = (d.token_count or 0)
        return out

    return {
        "total": um.total_token_count or 0,
        "prompt": um.prompt_token_count or 0,
        "response": um.response_token_count or 0,
        "prompt_by_mod": by_mod(um.prompt_tokens_details),
        "response_by_mod": by_mod(um.response_tokens_details),
    }


def _log_turn(rec):
    """One machine line + one human line per turn. The local transcript record. Never breaks a turn."""
    try:
        with LIVE_TELEMETRY.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        new = not LIVE_LOG.exists()
        with LIVE_LOG.open("a", encoding="utf-8") as fh:
            if new:
                fh.write("# Founder OS realtime voice - local transcript\n\nEvery realtime turn: what "
                         "you said, what the OS said, tools used, reply latency, tokens. Local-only "
                         "(this folder is gitignored). Newest at the bottom.\n\n")
            lat = f"{rec['reply_ms']}ms" if rec.get("reply_ms") is not None else "?"
            tok = rec.get("tokens_total")
            tools = (" [" + ", ".join(rec["tools"]) + "]") if rec.get("tools") else ""
            meta = f"{lat}, {tok} tok" if tok is not None else lat
            fh.write(f"- **{rec['ts']}**{tools} ({meta})\n"
                     f"  - you: {rec.get('heard') or '(no speech captured)'}\n"
                     f"  - os:  {rec.get('said') or '(audio only)'}\n")
    except Exception as exc:  # noqa: BLE001 - logging must never break a turn
        print(f"[live-log error] {exc}", flush=True)


def print_summary():
    if not LIVE_TELEMETRY.exists():
        print("No realtime turns logged yet. Talk to your OS first.")
        return
    rows = [json.loads(l) for l in LIVE_TELEMETRY.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not rows:
        print("Transcript log is empty.")
        return
    from collections import Counter
    lat = [r["reply_ms"] for r in rows if r.get("reply_ms")]
    tok = [r["tokens_total"] for r in rows if r.get("tokens_total")]
    audio_tok = sum((r.get("tokens_response_by_mod") or {}).get("AUDIO", 0)
                    + (r.get("tokens_prompt_by_mod") or {}).get("AUDIO", 0) for r in rows)
    tools = Counter(t for r in rows for t in r.get("tools", []))
    avg = lambda xs: round(sum(xs) / len(xs)) if xs else 0
    print(f"Realtime voice - {len(rows)} turns")
    print(f"  reply latency:  avg {avg(lat)}ms  | fastest {min(lat) if lat else 0}  | slowest {max(lat) if lat else 0}")
    print(f"  TOKENS:         {sum(tok):,} total this session  (~{audio_tok:,} audio - the cost driver)")
    print(f"  per-turn avg:   {avg(tok):,} tokens")
    print(f"  tools used:     {', '.join(f'{k} x{v}' for k, v in tools.most_common()) or 'none'}")


# ---- the experimental proactive-context seam ---------------------------------------------------
# OFF by default (config proactive_context=false). This is the honest, SAFE form of "the back-brain
# pushes context into the live session": a thread-safe queue the back-brain (or a future watcher)
# enqueues notes onto, drained ONLY at a turn boundary - never mid-sentence, because injecting into
# a model that is already speaking triggers a disruptive barge-in. The front never goes silent here
# because its immediate-engage behaviour (above) already keeps the room alive. True mid-turn
# injection is deliberately not done; this seam exists so it can be built on without breaking the loop.
_CONTEXT_QUEUE: "queue.Queue[str]" = queue.Queue()


def enqueue_context(note: str):
    """Public seam: a back-brain process can push a context note to surface at the next turn break."""
    if note and note.strip():
        _CONTEXT_QUEUE.put(note.strip())


class Bridge:
    """One browser socket <-> one Gemini Live session, pumped both directions on one API key."""

    def __init__(self, ws, client, model, live_config):
        self.ws = ws
        self.client = client
        self.model = model
        self.live_config = live_config
        self.session = None
        self.sess_total = 0
        self.turn = {}
        self._reset_turn()

    def _reset_turn(self):
        self.turn = dict(t_open=None, t_user_last=None, t_first_audio=None,
                         heard=[], said=[], tools=[], usage=None)

    def _mark_open(self):
        if self.turn["t_open"] is None:
            self.turn["t_open"] = time.perf_counter()

    def _finalize(self):
        t = self.turn
        if t["t_open"] is None and not t["said"] and not t["heard"]:
            return
        ref = t["t_user_last"] or t["t_open"] or time.perf_counter()
        reply_ms = round((t["t_first_audio"] - ref) * 1000) if t["t_first_audio"] else None
        u = t["usage"] or {}
        reported = u.get("total")
        tokens_total = None
        if reported is not None:                       # usage_metadata is cumulative; per-turn = delta
            delta = reported - self.sess_total
            tokens_total = delta if delta > 0 else reported
            self.sess_total = max(self.sess_total, reported)
        _log_turn({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "heard": "".join(t["heard"]).strip(),
            "said": "".join(t["said"]).strip(),
            "tools": t["tools"],
            "reply_ms": reply_ms,
            "tokens_total": tokens_total,
            "tokens_reported": reported,
            "tokens_prompt_by_mod": u.get("prompt_by_mod"),
            "tokens_response_by_mod": u.get("response_by_mod"),
        })
        self._reset_turn()

    async def _browser_to_gemini(self):
        from google.genai import types
        async for msg in self.ws:
            if isinstance(msg, (bytes, bytearray)):
                await self.session.send_realtime_input(
                    audio=types.Blob(data=bytes(msg), mime_type="audio/pcm;rate=16000"))
            else:
                try:
                    d = json.loads(msg)
                except ValueError:
                    continue
                if d.get("type") == "end":
                    await self.session.send_realtime_input(audio_stream_end=True)

    async def _run_tool(self, fc):
        from google.genai import types
        self._mark_open()
        await self.ws.send(json.dumps({"type": "acting", "name": fc.name}))
        handler = TOOL_HANDLERS.get(fc.name)
        if not handler:
            result = f"Unknown tool {fc.name}."
        else:
            try:
                # Off the event loop so a slow brain call never stalls the audio stream.
                result = await asyncio.to_thread(handler, dict(fc.args or {}))
            except Exception as exc:  # noqa: BLE001 - a failed action must not kill the turn
                print(f"[live] tool {fc.name} failed: {exc}", flush=True)
                result = f"That action failed: {str(exc)[:120]}"
        self.turn["tools"].append(fc.name)
        print(f"[live] tool {fc.name}({dict(fc.args or {})}) -> {str(result)[:80]}", flush=True)
        return types.FunctionResponse(id=fc.id, name=fc.name, response={"result": result})

    async def _drain_context_queue(self):
        """At a turn boundary, push any queued back-brain context as a non-spoken client turn."""
        if not CONFIG.get("proactive_context"):
            return
        from google.genai import types
        notes = []
        while not _CONTEXT_QUEUE.empty():
            try:
                notes.append(_CONTEXT_QUEUE.get_nowait())
            except queue.Empty:
                break
        if notes:
            text = "Context update from the back-brain (do not read aloud unless relevant): " + " ".join(notes)
            await self.session.send_client_content(
                turns=types.Content(role="user", parts=[types.Part(text=text)]), turn_complete=False)

    async def _gemini_to_browser(self):
        # receive() yields one turn's messages then returns; re-enter it for every turn for the life
        # of the session, or only the FIRST turn is ever read (the "answered once then went silent" bug).
        while True:
            async for resp in self.session.receive():
                if resp.usage_metadata:
                    self.turn["usage"] = _usage(resp.usage_metadata)
                if resp.tool_call:
                    responses = await asyncio.gather(
                        *[self._run_tool(fc) for fc in resp.tool_call.function_calls])
                    await self.session.send_tool_response(function_responses=list(responses))
                    continue
                if resp.data:                          # Gemini's NATIVE audio - stream straight to the browser
                    self._mark_open()
                    if self.turn["t_first_audio"] is None:
                        self.turn["t_first_audio"] = time.perf_counter()
                    await self.ws.send(resp.data)
                sc = resp.server_content
                if not sc:
                    continue
                if sc.interrupted:                     # barge-in: you talked over it
                    await self.ws.send(json.dumps({"type": "interrupted"}))
                if sc.input_transcription and sc.input_transcription.text:
                    self._mark_open()
                    self.turn["t_user_last"] = time.perf_counter()
                    self.turn["heard"].append(sc.input_transcription.text)
                    await self.ws.send(json.dumps({"type": "heard", "text": sc.input_transcription.text}))
                if sc.output_transcription and sc.output_transcription.text:
                    self.turn["said"].append(sc.output_transcription.text)
                    await self.ws.send(json.dumps({"type": "say", "text": sc.output_transcription.text}))
                if sc.turn_complete:
                    self._finalize()
                    await self.ws.send(json.dumps({"type": "turn_complete"}))
                    await self._drain_context_queue()

    async def run(self):
        async with self.client.aio.live.connect(model=self.model, config=self.live_config) as session:
            self.session = session
            await asyncio.gather(self._browser_to_gemini(), self._gemini_to_browser())


async def serve_socket(ws):
    """Open the session, rotating across the available keys if one is over quota / rejected."""
    from google import genai
    keys = load_keys()
    if not keys:
        await ws.send(json.dumps({"type": "error", "text":
            "No Google AI Studio key found. Add a free one: say 'connect gemini', or run "
            "python scripts/connect.py set-secret GEMINI_API_KEY"}))
        return
    live_config = build_live_config()
    print(f"[live] browser connected ({len(keys)} key(s)); opening Gemini session...", flush=True)
    for attempt, key in enumerate(keys):
        try:
            await Bridge(ws, genai.Client(api_key=key), CONFIG["model"], live_config).run()
            return
        except Exception as exc:  # noqa: BLE001 - boundary
            if _is_quota(exc) and attempt < len(keys) - 1:
                print(f"[live] key #{attempt + 1} unavailable ({str(exc)[:60]}); rotating", flush=True)
                continue
            msg = ("all keys are over quota right now" if _is_quota(exc)
                   else f"{type(exc).__name__}: {str(exc)[:160]}")
            print(f"[live] session ended: {msg}", flush=True)
            try:
                await ws.send(json.dumps({"type": "error", "text": msg}))
            except Exception:
                pass
            return


# ---- tiny page server (serves live.html) on a daemon thread ------------------------------------
class PageHandler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/live", "/live.html"):
            if PAGE.exists():
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(500, b'{"error":"live.html missing next to live_server.py"}', "application/json")
        elif self.path == "/health":
            self._send(200, json.dumps({"ok": True, "model": CONFIG["model"],
                                        "voice": CONFIG["voice"], "keys": len(load_keys())}).encode(),
                       "application/json")
        else:
            self._send(404, b'{"error":"not found"}', "application/json")

    def log_message(self, *a):
        return


def serve_page(port):
    ThreadingHTTPServer(("127.0.0.1", port), PageHandler).serve_forever()


def _port_busy(port):
    """True if something already holds the local port. A clean preflight beats a raw traceback."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        return False
    except OSError:
        return True
    finally:
        s.close()


async def main():
    import websockets
    http_port = CONFIG["http_port"]
    ws_port = CONFIG["ws_port"]
    # Preflight both ports so a conflict is a clear message, not a stack trace (a likely cause:
    # another voice server already running, or the ports clash with another app).
    for port, label in ((http_port, "page"), (ws_port, "bridge")):
        if _port_busy(port):
            print(f"Port {port} (the {label} port) is already in use. Another voice server may be "
                  f"running, or another app holds it. Stop that process, or change \"http_port\" / "
                  f"\"ws_port\" in voice/realtime-config.json, then start again.", flush=True)
            return
    threading.Thread(target=serve_page, args=(http_port,), daemon=True).start()
    keys = load_keys()
    print("Founder OS realtime voice (Tier 1)", flush=True)
    print(f"  model: {CONFIG['model']}   voice: {CONFIG['voice']}", flush=True)
    print(f"  keys:  {len(keys)} found" + (" - add one: connect gemini" if not keys else ""), flush=True)
    print(f"  open:  http://127.0.0.1:{http_port}/live", flush=True)
    print("  Stop:  Ctrl+C", flush=True)
    async with websockets.serve(serve_socket, "127.0.0.1", ws_port, max_size=None):
        await asyncio.Future()


def list_models():
    """Free API call (no Live session, no audio cost): print the models your key exposes."""
    from google import genai
    keys = load_keys()
    if not keys:
        print("No key found. Add one: connect gemini")
        return
    client = genai.Client(api_key=keys[0])
    print("Models on your key (look for a Flash native-audio / live one for Tier 1):")
    for m in client.models.list():
        name = getattr(m, "name", "")
        if any(s in name for s in ("live", "audio", "flash")):
            print(f"  {name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Founder OS realtime voice (Tier 1).")
    ap.add_argument("--summary", action="store_true", help="print this session's latency + token report")
    ap.add_argument("--models", action="store_true", help="list the Live models your key exposes (no audio cost)")
    args = ap.parse_args()
    if args.summary:
        print_summary()
        sys.exit(0)
    if args.models:
        list_models()
        sys.exit(0)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nstopped", flush=True)
