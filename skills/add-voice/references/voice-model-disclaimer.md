# The voice-model disclaimer (read this before you commit to a tier)

This is the most important honesty note in the whole voice layer. It is not boilerplate.

The speech model you pick changes two things that cost you directly:

1. **How well your speech is received** - the transcription accuracy. A weak model mishears
   you, and the OS acts on the wrong words.
2. **The cost per turn** - some options are free, some bill you per minute or per character.

So the trade is yours to make with open eyes. Here is each option stated plainly.

## Tier 0 - browser speech (the default)

- **Accuracy:** good for clear speech in a quiet room; degrades with accents, noise, jargon.
- **Cost:** free. No key, no account, no per-minute charge.
- **Privacy:** in Chrome and Edge, your audio is sent to the browser vendor (Google or
  Microsoft) to be transcribed. It is free and keyless, but it is **not local**. Chrome 139+
  has an optional on-device mode; until you turn it on, assume audio leaves the machine.
- **Who it is for:** anyone who wants to feel the loop today with zero setup.

## Tier 0-local - faster-whisper (fully local upgrade)

- **Accuracy:** strong, and tunable by model size (tiny is fast and rough, small/medium is
  the sweet spot, large is best and slowest).
- **Cost:** free. Runs on your own CPU or GPU. No key, no per-minute charge.
- **Privacy:** fully local. No audio leaves your machine.
- **The trade:** one pip install plus a model download, and a little more latency than the
  cloud browser path. This is the right default if privacy matters more than instant setup.

## Tier 1 - Gemini Live (realtime, free key)

- **Accuracy:** high, native realtime turn-taking, sub-second feel.
- **Cost (read this carefully):** the KEY is free to create. Free Google AI Studio keys keep a
  free DAILY quota on **Flash** models (Pro models are paid-only). The realtime default here is a
  Flash native-audio model, so a normal day of use can stay inside the free quota. But realtime
  audio is a billed surface: past the daily quota it charges per token (on the order of $1 per
  million input tokens, and audio is the heavy part). Heavy or all-day use can move a free key onto
  paid rates. The model you pick changes the cost - keep it on a Flash native-audio model unless you
  mean to spend, and watch usage with `python voice/live_server.py --summary`. This is NOT "free
  forever"; it is "free to start, with a real daily ceiling".
- **Privacy:** audio and the live conversation stream to Google to run the model. Your brain (your
  files and the answers read from them) stays local; only the conversation leaves.
- **Whose key:** yours. You create it in your own Google AI Studio account and it lives only in your
  gitignored `.env`. The OS ships no key and never provides one - the setup wires everything else so
  you only drop in your own. That keeps the cost yours to see and control, on your own account.
- **Who it is for:** anyone who wants a no-lag spoken conversation, accepts a cloud realtime
  dependency, and understands the free tier is a daily quota, not unlimited.

## Tier 2 - ElevenLabs (premium mouth)

- **Quality:** the most natural-sounding voice out.
- **Cost:** paid. A key and a plan. This is a deliberate spend, never a default.
- **Who it is for:** anyone who wants a broadcast-quality voice and will pay for it.

## The one rule

State the tier's cost and accuracy trade **before** the user commits, not after. A bad
default silently bills them or mishears them. When in doubt, recommend Tier 0 and name the
two upgrades - never auto-select a paid or cloud option.
