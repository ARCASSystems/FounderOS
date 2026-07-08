# Realtime voice (Tier 1) - how it is built and why

Tier 1 is the opt-in realtime upgrade: a streaming spoken conversation instead of the Tier-0
press-and-release round-trip. This note explains the operating model so you can trust what it
does, change it safely, and know exactly what is proven versus what is an early seam.

Read the cost and accuracy trade first: [voice-model-disclaimer.md](voice-model-disclaimer.md).

## Two models, two jobs (the load-bearing idea)

A realtime model and a reasoning model are good at different things. Tier 1 uses both.

- **The front** is the realtime model (Gemini Live). It holds the conversation: it hears you,
  takes turns with native voice-activity detection, and speaks back in its own voice, sub-second.
  It does NOT hold your OS. It is a host, not a database.
- **The back-brain** is the no-key reasoning CLI you already run the OS in (the same one Tier 0
  detected: `claude -p`, or `codex` / `gemini` if that is your CLI). The front reaches for it
  through the `query_brain` tool whenever a real fact about your OS is needed. The back-brain reads
  your local markdown files and answers. Only the live conversation streams to the cloud; your
  brain stays on your machine.

This split is why a long answer never freezes the voice, and why business facts are read from your
files instead of guessed. It is the public, persona-free form of the same architecture the private
build proved.

## State the front does not have (inject it, never let it guess)

The front holds only the live session. It has zero memory across wakes, and it has no clock. But a
spoken persona invites it to SOUND continuous, so left alone it fabricates the state it is missing:
a time of day, a "him" or "that" from a conversation it never saw, a fact it half-remembers. The
private build hit exactly this - on a 2 a.m. wake the voice cheerfully announced it was half past
nine and offered the morning brief, because no real clock had been handed to it and the greeting
assumed morning.

The fix is plumbing, not a smarter model, and it is the same shape every time: make the missing
state explicit and hand it over at the boundary.

- **Clock: injected per wake.** Every new realtime session gets the real local date and time
  prepended to its instructions, recomputed at that moment - never cached at server start, or the
  clock freezes at whenever the server came up. The instruction states plainly: this is the real
  current time, use it, never state any other time.
- **Continuity: lives in the files, never in the model's head.** The front is a fresh session every
  wake. Anything that must survive - what was said, what was decided, who "him" refers to - is
  written to the brain files and read back through `query_brain`, not trusted to session memory.
- **The desk model.** Think of the front as the desk: only what is placed on it this session
  exists. The repo of markdown files is the filing cabinet: everything durable lives there, and the
  back-brain reads from it fresh on every call. The desk is rebuilt from the cabinet at every
  boundary, so nothing depends on the desk remembering.

If you extend the voice layer, keep this rule: any state the front needs, inject it at session
start or fetch it through a tool. A front that guesses state it does not have will state it with
full confidence, and a confident wrong time is worse than a pause.

## Engage instantly. Pause only when you ask.

Realtime changes the rule. In Tier 0 a slow turn says "give me a moment". In Tier 1 that is the
wrong behaviour. The front is told to respond on EVERY turn at once - acknowledge, reflect, ask, or
narrate what it is about to do. There is no dead air, ever, because of slowness.

The single exception is yours to trigger: if you say **"thinking"** (or "let me think", "hold on",
"give me a second") out loud, you have taken the floor. The front goes quiet and waits until you
speak again. The pause is operator-triggered, never latency-triggered. The Tier-0 backchannel timer
is deliberately absent here.

## The room is a three-way conversation

The default framing is that you may be on camera, or a third person (an audience, a client) may be
present. The front is told to keep the conversation alive and human, address you, and stay aware
that others may be listening. You give it a name and a sharper persona by writing
`voice/persona.md` (gitignored, optional); with no file it speaks as a neutral, calm host with no
proper name. No name ships in the public repo.

## Feeding the front the right context at the right time

There are two ways the back-brain can reach the front. One is shipped and proven; one is an early
seam, off by default, and honestly labelled as such.

- **Pull (shipped, the verified core).** The front decides it needs a fact, says a short line
  ("let me check") so there is no silence, and calls `query_brain`. The call runs off the event
  loop, so a few-second read never stalls the audio. The result is fed back and the front voices it
  in its own words. This is "feed the right context while the front keeps talking", and it is the
  whole working loop today.
- **Push (experimental seam, OFF by default).** `live_server.py` carries a thread-safe context
  queue and an `enqueue_context()` entry point so a back-brain process can push a note that the
  front surfaces at the NEXT turn boundary. It is drained only between turns, never mid-sentence,
  because injecting into a model that is already speaking triggers a disruptive barge-in. Turn it on
  with `proactive_context: true` in `voice/realtime-config.json`. True mid-utterance injection is
  deliberately not built; the seam exists so it can be developed without breaking the loop. Do not
  rely on the push path as if it were the pull path.

## Guardrails: intelligent, not blocking

The OS keeps the confirm-gate principle for anything irreversible, but a live, on-camera
conversation cannot stall on a modal. So Tier 1 draws the line at capability, not at a prompt:

- The realtime tools **read** your OS (`query_brain`, `show_today`, `show_this_week`, `what_changed`)
  and make one **safe, reversible** write (`save_to_brain` appends a note to your log). Nothing here
  can send a message, delete, or control your machine.
- Anything irreversible - sending, posting, computer control - is a SEPARATE capability ("add
  hands") that installs its own explicit confirm gate. Tier 1 will tell you plainly it cannot do
  those yet rather than pretend or stall.
- The character keeps honest pushback over agreement, and keeps cost and feasibility grounded. That
  is judgment at conversation speed, which is the point: the right guardrails, intelligently applied.

## The local transcript, and where it goes next

Every turn is recorded locally (the `voice/` folder is gitignored):

- `voice/live-telemetry.jsonl` - one machine-readable line per turn (latency, tokens, tools).
- `voice/live-log.md` - the readable transcript: what you said, what the OS said, per turn.

This is here so you know your voice is grounded in real context retrieved from your files, and so a
later step can move old runtime logs to an archive and keep only summaries in a lean cache - the
same runtime-log to archive to cache-summary loop the rest of the OS uses. That loop is a planned
next step, not built into Tier 1 yet.

## Keys and cost control

One free Google AI Studio key is enough to start. A second key (`GEMINI_API_KEY2`) is optional
headroom: the realtime front rotates to it automatically the moment the first hits its daily quota,
so a long session does not stall on a `RESOURCE_EXHAUSTED` error mid-conversation.

To add the second free key for headroom:

1. Create another free key at https://aistudio.google.com/apikey. It can be a second key in the
   same Google account, or a key in a second Google account for a separate daily quota.
2. Store it the same gitignored-only way as the first, under the second name:
   `python scripts/connect.py set-secret GEMINI_API_KEY2` and paste the key when prompted (it reads
   from stdin so the key never lands in your shell history or the command line).
3. That is all. The front reads both keys at the next start and rotates to the second on quota;
   there is nothing else to configure. The keys live only in the gitignored `.env` and are never
   committed.

Watch usage with `python voice/live_server.py --summary`, which reports the audio-token count that
drives cost.

## Files

- `realtime/live_server.py` - the bridge: serves the page, runs the Gemini Live session server-side
  (so your key never touches the browser), exposes the safe tools, logs every turn.
- `realtime/live.html` - the page: continuous mic capture, native 24kHz audio playback, barge-in,
  the disclaimer banner, the orb.
- `setup_realtime.py` - the installer: prints the disclaimer first, installs the two deps, copies
  the runtime into `voice/`, writes `voice/realtime-config.json`, checks for a key.

No em dashes or en dashes anywhere in this layer. Hyphens only.
