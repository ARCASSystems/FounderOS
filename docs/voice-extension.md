# Voice: an optional mouth and ears (the OS is complete without it)

Read this only if you want to talk to your OS out loud. You do not need it. Founder OS is fully complete as text - you type, it answers, nothing here is missing. Voice is an optional sensory layer on top of the same brain. It is off by default; you add it by asking.

There is now a skill that wires it for you: say **"add voice"** (the `add-voice` skill). It is still opt-in, still not on unless you install it, and its default tier needs no extra key.

## The four parts, in plain terms

Think of the OS the way you would think of a person who works with you.

- **The Brain** is the memory - the plain markdown files that hold your priorities, clients, decisions, and the week. This is the part that matters, and it is fully built.
- **The Hands** are the tools it reaches for - your calendar, your inbox, your notes. Optional, you connect what you use.
- **The Mouth** is the OS speaking its answer out loud instead of you reading it (text to speech).
- **The Ears** are the OS hearing you instead of you typing (speech to text).

The Brain and the Hands ship. The Mouth and the Ears are the optional layer the `add-voice` skill installs. The Brain stays the same whether you read its answers or hear them.

## You almost certainly do not need this

If you can type and read, the OS is complete. Voice is a convenience for two specific cases:

- you do your thinking out loud and want to talk to the OS the way you talk to a person,
- you want answers read back while your hands and eyes are busy.

If neither is you, stop here. Adding voice is extra moving parts for no gain.

## If you do want it: say "add voice"

The `add-voice` skill installs it in tiers, and the default holds the accessibility floor - it works end-to-end on the one subscription you already run the OS in, with no extra API key and no paid service.

- **Tier 0 (default, no key):** your browser's built-in speech recognition (ears) and speech (mouth), plus the reasoning CLI you already run the OS in (brain). Zero install, zero key. One honest note: in Chrome and Edge the browser sends your audio to its vendor to transcribe it - free and keyless, but not fully local.
- **Tier 0-local (free, fully local):** swap the browser ears for [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and the browser mouth for [Piper](https://github.com/rhasspy/piper) - both free, both run offline on your own machine, no key. One pip install plus a model download, and a little more lag than the cloud path.
- **Tier 1 (realtime, free key):** sub-second spoken conversation - say "add voice --realtime". A realtime model speaks in its own voice while the no-key CLI you already run stays the back-brain that reads your files. Opt-in: the free Google AI Studio key has a free daily quota on Flash models and heavy use can move onto paid rates, stated before you commit.
- **Tier 2 (premium mouth, paid):** ElevenLabs for broadcast-quality voice out. A deliberate spend, never a default.

Full detail lives in the skill: `skills/add-voice/references/tiers.md` and `voice-model-disclaimer.md`.

## The honest shape of it

- **What ships:** the Brain (your files) and the Skills that read and write them. Text in, text out. Complete.
- **What `add-voice` adds:** a thin local loop - your microphone into the OS, and the OS's reply back out to your speakers - wired onto the same brain, kept on your machine.
- **The honest tradeoff:** fully local and free (Tier 0-local: faster-whisper plus Piper) is the privacy-first choice and has a little lag. A real-time, no-lag spoken conversation (Tier 1) needs a streaming voice service on a free key, which is a deliberate choice, not the default. Decide which you actually need before installing anything past Tier 0.

## What this page is not

It is not a claim that the OS talks or listens until you add voice. Out of the box it does not. Run `add-voice` and the OS can hear you and speak its answer, with the default needing no key. Until you install that layer, the OS is text - and text is the whole product, not a lesser version of it.
