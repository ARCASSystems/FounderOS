# Voice tiers - what each adds and how to install it

The default (Tier 0) is wired by `setup.py` and needs nothing extra. The rest are opt-in
upgrades. Read [voice-model-disclaimer.md](voice-model-disclaimer.md) for the cost and
accuracy trade of each before you pick.

Every heading below is marked `[WIRED]` or `[DOCUMENTED]`. `[WIRED]` means code ships and
runs it. `[DOCUMENTED]` means this page describes it and nothing implements it yet. The
marks exist because both local rungs used to read as built while being build instructions,
and a reader had no way to tell.

## Tier 0 - default (no extra key, no paid service)  [WIRED]

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

## Tier 0-local ears - faster-whisper (fully local speech, no key)  [WIRED]

Make speech never leave your machine. Free, local, one install.

Until v1.55 this section was build instructions written as though the endpoint
existed. It exists now: `POST /transcribe` in `voice/server.py`, with
MediaRecorder capture behind the **Local ears** toggle on the page.

1. `pip install faster-whisper`
2. Start the server and tick **Local ears**. The first use downloads the model,
   which takes a minute; every use after that is local and instant-ish. Measured
   on a laptop CPU with the `base` model: about 2.4 seconds for a ten-second
   turn including the one-off model load, about 1.1 seconds after it is cached.
3. That is all. The page routes the hold-to-talk button through the recorder
   instead of the browser's recogniser, and the text lands in the same `/brain`
   route as before.

Two settings in `voice/config.json`, both optional:

- `local_stt: true` starts with the toggle already on.
- `local_stt_model` picks the model. `base` is the default and the honest
  starting point; `small` is more accurate and slower.

**The page says which ears are running, every time.** Not which are possible.
With the toggle off it names your browser vendor; with it on it says the audio
stays here. If faster-whisper is not installed the toggle is disabled and its
tooltip says why and how to fix it, rather than failing when you press the
button. faster-whisper is never bundled, so Tier 0 stays a zero-install proof.

## Tier 0-local mouth - Piper (fully local voice out, no key)  [WIRED]

Upgrade the mouth from the browser default to a small local neural voice. Free, local.

1. Install Piper and download a voice, both from https://github.com/rhasspy/piper
2. Put the voice path in `voice/config.json` as `piper_voice` (the `.onnx` file).
   `piper_cmd` defaults to `piper` and only needs setting if yours is elsewhere.
3. Tick **Local voice** on the page.

`POST /speak` shells out to Piper and returns WAV. If Piper is missing, or the
voice file named in the config is not there, the toggle is disabled and says
which of the two is wrong. If Piper fails mid-turn the page falls back to the
browser voice rather than leaving the answer silent, because a silent turn reads
as a broken app.

Not verified by the maintainer on a machine with Piper installed. The absent
path is tested; the speaking path is not.

## Tier 1 - realtime voice (Gemini Live, FREE Google AI Studio key)  [WIRED, last run against a live key 2026-08-05]

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
eligible within the daily quota, and confirmed present on a live free key on 2026-08-05. Model names
change often, and a name that has been retired fails at the first turn, so treat any model id you
read in a doc as a claim to check, not a fact. `python voice/live_server.py --models` lists what your
key actually exposes right now; that list, not this page, is the source of truth. Newer Live models
appear there over time (there are already newer preview ones); the `-latest` default is the
conservative pick because it tracks the current free-tier-eligible Flash audio model for you. The model you pick changes both
accuracy and per-turn cost: a free key has a real free DAILY tier on Flash; heavy use can move you
onto paid rates. Pick deliberately.

## Tier 2 - premium mouth (ElevenLabs, paid)  [DOCUMENTED, not built]

Broadcast-quality voice out. Paid key, paid plan. A deliberate spend, never a default.
Store the key via the connect skill (`connect elevenlabs`) so it only ever lives in `.env`.

## The honest shape

Tier 0 is the whole product working on one subscription with no extra key. Every tier above
it is a deliberate choice with a stated cost. Default down, upgrade on purpose.

And the page never claims a tier it is not running. It reads its status from the server on
load, names the ears and the mouth that are actually active, and disables a toggle whose
dependency is missing with a tooltip saying which one and how to install it. A privacy
feature that says "local" while the audio goes elsewhere would be worse than not shipping
one at all.
