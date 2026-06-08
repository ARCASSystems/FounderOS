---
name: add-voice
description: >
  Give your Founder OS a voice - talk to it out loud and hear it answer. Trigger on "add
  voice", "let me talk to my OS", "voice mode", "talk to it out loud", or "set up voice".
  Installs the Tier-0 loop by default: your browser's built-in speech (ears and mouth) plus
  the reasoning CLI you already run the OS in (brain), with NO extra API key and NO paid
  service - the accessibility floor. A small local Python setup wires a gitignored voice/
  runtime bound to your machine. Realtime voice (Gemini Live, free Google AI Studio key) and
  a premium mouth (ElevenLabs) are opt-in upgrades, never the default. Honest disclaimer up
  front: in Chrome/Edge the browser sends your audio to its vendor to transcribe (no key, no
  cost, but not fully local); a faster-whisper upgrade makes it fully local. Your brain -
  your files and answers - stays on your machine.
why: "Voice is the most-asked extension and the easiest place to either silently bill the user or mishear them. Shipping it as a tiered skill - default that needs no key, upgrades that are opt-in and disclosed - holds the accessibility floor and keeps the honesty note load-bearing instead of buried."
enhance: "Use Chrome or Edge for built-in speech input. Want speech that never leaves your machine? Add the faster-whisper upgrade in references/tiers.md. Want sub-second realtime conversation? That is Tier 1 - a free Google AI Studio key, with the cost-and-accuracy trade stated plainly before you commit."
summary: "Talk to your OS and hear it back - default needs no key."
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# Add voice

Runs on: local-exec - the happy path runs a local Python setup that writes a gitignored `voice/` runtime and serves a local page. On a read-only or cloud surface, explain the steps and the tiers but do NOT claim the install ran or the loop works - it has not until the user runs it locally.

This turns the documented "voice is a DIY mouth and ears" direction ([docs/voice-extension.md](../../docs/voice-extension.md)) into a wired capability the user installs by asking. The OS ships as a complete text brain; this adds a sensory layer on top of the same brain. Nothing here is required.

## The accessibility floor (the rule that governs the default)

The default install - Tier 0 - must work end-to-end on the **one subscription the user already runs the OS in**, with **no extra API key and no paid service**. That is non-negotiable. The brain answers through the reasoning CLI the OS already uses (`claude -p` by default - no API key, it uses the existing subscription); the browser hears and speaks. Everything past Tier 0 is opt-in and disclosed.

## The tiers

| Tier | What it adds | Needs | Default? |
| --- | --- | --- | --- |
| **0** | Browser speech-in + speech-out + brain on your one subscription | nothing extra | YES |
| **0-local** | Swap browser STT for faster-whisper so speech never leaves your machine | one pip install + a model download | no - opt-in |
| **1** | Realtime, sub-second spoken conversation (Gemini Live front) | a FREE Google AI Studio key | no - opt-in |
| **2** | A premium, higher-quality mouth (ElevenLabs) | a paid key | no - opt-in |

Full detail, the upgrade commands, and the cost-and-accuracy trade for each are in [references/tiers.md](references/tiers.md) and [references/voice-model-disclaimer.md](references/voice-model-disclaimer.md). The disclaimer is load-bearing: the voice/STT model the user picks changes both how well their speech is received and the cost per turn. State it before they commit, never after.

## Pre-flight

- If `core/identity.md` does not exist, voice still installs, but say plainly that with no identity the brain answers from a thin context. Offer `/founder-os:setup` first for richer answers. Do not block on it.
- Confirm a local runtime: this skill runs Python and serves a local page. On a web-only surface, walk the steps and stop - do not claim it ran.

## The flow

### 1. Confirm the tier (default to 0)

Say one line: **"I'll set up Tier 0 - you talk, it answers, no key needed. Want fully-local speech or realtime instead, or shall I wire the default?"** Default to Tier 0 unless they ask otherwise. Do not open a menu - one recommendation, the two upgrades named.

### 2. Run the setup

```
python skills/add-voice/setup.py
```

It checks Python, detects the reasoning CLI on PATH (the no-key brain), creates a gitignored `voice/` folder, copies the page and server into it, and writes `voice/config.json` bound to this machine. It installs nothing and needs no key. Add `--port <n>` to change the port, `--start` to launch the server immediately.

Read its output back to the user honestly: what it wired, and whether a reasoning CLI was found. If none was found, ears and save-to-brain still work; conversational answers wait until a CLI is on PATH.

### 3. Start the loop and prove it

```
python voice/server.py
```

It serves `http://127.0.0.1:8765/` and opens it. The user holds **Talk**, speaks, releases; the OS answers out loud. **Save last to brain** appends what they said to `brain/log.md`. Tell them the one honest thing: in Chrome/Edge the browser sends audio to its vendor to transcribe (no key, no cost, not fully local); the faster-whisper upgrade makes it local.

A clean proof is: server serves the page, a spoken turn comes back as a spoken answer, and a save lands a line in `brain/log.md`. Do not say "voice works" until that round-trip has actually happened on the user's machine.

## Tier 1 - realtime voice (the opt-in upgrade)

Trigger: **"add voice --realtime"**, "add realtime voice", "I want a real conversation", "make it talk back instantly". This is the sub-second streaming loop: a realtime model (Gemini Live) hears you, takes turns with native voice detection, and speaks back in its own voice, while the reasoning CLI you already run stays the back-brain that reads your files. It sits ON TOP of Tier 0; it does not replace it. Two models, two jobs - detail in [references/realtime-architecture.md](references/realtime-architecture.md).

It is NOT zero-cost or zero-install, and you say so BEFORE installing:

1. **Disclaimer first (load-bearing).** A FREE Google AI Studio key has a free daily quota on Flash models; heavy realtime use can move you onto paid per-token rates. Audio streams to Google to run the model; your files and the answers read from them stay local. State this before they commit, not after. `setup_realtime.py` prints it at the top; you say it in conversation too. Full trade in [references/voice-model-disclaimer.md](references/voice-model-disclaimer.md).
2. **Get and store your own free key (the OS ships none).** The user creates their own free key at https://aistudio.google.com/apikey, in their own Google account. Setup wires everything else so they only drop the key in. Store it via the connect flow so it lands only in the gitignored `.env`: say "connect gemini" or run `python scripts/connect.py set-secret GEMINI_API_KEY` (pasted on stdin, never an argument). A second key (`GEMINI_API_KEY2`) is optional headroom the front rotates to on quota. Never ship, hardcode, or provide a key.
3. **Run the installer.** `python skills/add-voice/setup_realtime.py` installs two packages (google-genai, websockets - a real install), copies the realtime page and bridge into the gitignored `voice/`, writes `voice/realtime-config.json`, and inherits the Tier-0 brain command. Pick a voice with `--voice <name>` (Aoede default; Puck, Charon, Kore, Fenrir, Leda also work). `python voice/live_server.py --models` lists the Live models your key exposes if the default is unavailable.
4. **Start it and prove it.** `python voice/live_server.py` serves `http://127.0.0.1:8756/live`. Tap the orb, allow the mic, talk. Say "thinking" out loud to take the floor and it waits. Every turn records to `voice/live-log.md` (local-only). A clean proof is a spoken turn answered in the model's own voice, plus a business-fact question that visibly calls the brain. Do not claim realtime works until that has happened on the user's machine with their own key.

The realtime tools READ your OS (today, this week, what changed, query the brain) and make one safe, reversible append (save a note to your log). Sending, posting, and computer control are a SEPARATE gated capability ("add hands"), never in this tier - the front will say plainly it cannot do those yet rather than stall a live conversation.

## What it does and does not do

- **Does:** wire a local voice loop on the user's machine, no key, no paid service; keep the brain (files + answers) local; log each turn to `voice/runtime-log.jsonl` (local-only) so failures are visible; degrade honestly when a reasoning CLI or browser STT is absent.
- **Does not:** send a message, take any irreversible action, or claim to be local when the browser STT is not. Send-power and computer-control are not in this skill. If they are added later, they get an explicit confirm gate first.

## The guardrails this skill is built against

These are the three failure modes the design defends against (see [references/troubleshooting.md](references/troubleshooting.md)):

1. **"The site can't be reached."** The server is a plain local process - if the terminal closed, it is gone. Restart with `python voice/server.py`.
2. **Errors after a long session.** The brain context is kept deliberately lean (a short preamble + a small identity slice, never the whole repo) so a long session does not bloat and fail. If answers degrade, restart the server.
3. **A silent failure.** Every turn is logged and every boundary catches its error and returns a spoken message, never a dead-end.

## Runtime honesty

This skill needs a local runtime. On a web-only agent that cannot run Python or serve a page, do not claim voice is installed. Walk the user through the same steps and say plainly that the setup and the loop have to run in Claude Code (or any local-runtime agent pointed at the folder).

No em dashes or en dashes in anything you write here. Hyphens only.
