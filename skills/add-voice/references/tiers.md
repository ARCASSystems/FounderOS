# Voice tiers - what each adds and how to install it

The default (Tier 0) is wired by `setup.py` and needs nothing extra. The rest are opt-in
upgrades. Read [voice-model-disclaimer.md](voice-model-disclaimer.md) for the cost and
accuracy trade of each before you pick.

## Tier 0 - default (no extra key, no paid service)

Already wired by `python skills/add-voice/setup.py`:

- **Ears:** the browser's built-in speech recognition.
- **Mouth:** the browser's built-in speech.
- **Brain:** the reasoning CLI you already run the OS in (`claude -p` by default), no API key.

Run it: `python voice/server.py`. That is the whole default. Nothing below is required.

### Pointing the brain at a different CLI

`voice/config.json` holds `brain_cmd` as an argv list. The server appends your spoken text
as the final argument (no shell, so nothing you say is run as a command). Defaults to
`["claude", "-p"]`. If you run the OS through a different agent CLI, set it to that agent's
headless form and confirm it answers a prompt:

- Claude Code: `["claude", "-p"]`  (confirmed)
- Codex CLI:   `["codex", "exec"]` (verify on your version)
- Gemini CLI:  `["gemini", "-p"]`  (verify on your version)

The accessibility floor holds whenever that CLI runs on your existing subscription with no
separate API key. If your only subscription cannot run a no-key headless command, the page
still does ears, mouth, and save-to-brain; conversational answers then need a key (Tier 1).

## Tier 0-local - faster-whisper (fully local speech, no key)

Make speech never leave your machine. Free, local, one install.

1. `pip install faster-whisper`
2. Download a model the first run pulls automatically (start with `small`).
3. Capture mic audio in the browser (MediaRecorder), POST it to a small local transcribe
   endpoint, and feed the text into the same `/brain` route. The browser page is the same;
   only the ears change. This is the local-first keeper the disclaimer points to.

faster-whisper is the documented upgrade, not bundled, so Tier 0 stays a zero-install proof.

## Tier 0-local mouth - Piper (fully local voice out, no key)

Upgrade the mouth from the browser default to a small local neural voice. Free, local.

- Install Piper and a voice model (see https://github.com/rhasspy/piper), then have the
  server shell out to Piper instead of returning text for the browser to speak.

## Tier 1 - realtime voice (Gemini Live, FREE Google AI Studio key)

Sub-second spoken conversation. The cheapest realtime option that needs only a free-tier key -
no paid console, no ElevenLabs. The realtime model speaks in its OWN native voice (no extra
text-to-speech to install), while the reasoning CLI you already run stays the back-brain that
reads your files. Wired by `setup_realtime.py`. Architecture: [realtime-architecture.md](realtime-architecture.md).

1. Read the disclaimer below first - this tier can cost money past the free daily quota.
2. Get a free key at https://aistudio.google.com/apikey.
3. Store it with the connect skill so it lands only in the gitignored `.env`: say "connect gemini"
   or `python scripts/connect.py set-secret GEMINI_API_KEY` - never paste a key into a tracked file
   or a command argument (stdin only). A second key (`GEMINI_API_KEY2`) is optional quota headroom.
4. Install and wire: `python skills/add-voice/setup_realtime.py` (installs google-genai +
   websockets, copies the realtime runtime into `voice/`, writes `voice/realtime-config.json`).
5. Run it: `python voice/live_server.py`, open `http://127.0.0.1:8756/live`. Pick a voice with
   `--voice <name>` at setup; list the Live models your key exposes with `python voice/live_server.py --models`.

Default model: a Flash native-audio Live model (`gemini-2.5-flash-native-audio-latest`) - free-tier
eligible within the daily quota. Model names change over time; `python voice/live_server.py --models`
lists what your key actually exposes if the default is unavailable. The model you pick changes both
accuracy and per-turn cost: a free key has a real free DAILY tier on Flash; heavy use can move you
onto paid rates. Pick deliberately.

## Tier 2 - premium mouth (ElevenLabs, paid)

Broadcast-quality voice out. Paid key, paid plan. A deliberate spend, never a default.
Store the key via the connect skill (`connect elevenlabs`) so it only ever lives in `.env`.

## The honest shape

Tier 0 is the whole product working on one subscription with no extra key. Every tier above
it is a deliberate choice with a stated cost. Default down, upgrade on purpose.
