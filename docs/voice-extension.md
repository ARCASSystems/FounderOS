# Voice: an optional mouth and ears (you build it, the OS is complete without it)

Read this only if you want to talk to your OS out loud. You do not need it. Founder OS is fully complete as text - you type, it answers, nothing here is missing. This page is direction for a do-it-yourself extension, not a feature that ships in the box. Nothing below is installed or wired for you.

## The four parts, in plain terms

Think of the OS the way you would think of a person who works with you.

- **The Brain** is the memory - the plain markdown files that hold your priorities, clients, decisions, and the week. This is the part that matters, and it is fully built.
- **The Hands** are the tools it reaches for - your calendar, your inbox, your notes. Optional, you connect what you use.
- **The Mouth** is the OS speaking its answer out loud instead of you reading it (text to speech).
- **The Ears** are the OS hearing you instead of you typing (speech to text).

The Brain and the Hands ship. The Mouth and the Ears do not - they are a sensory layer you can add yourself if you want them, on top of the same Brain. The Brain stays the same whether you read its answers or hear them.

## You almost certainly do not need this

If you can type and read, the OS is complete. Voice is a convenience for two specific cases:

- you do your thinking out loud and want to talk to the OS the way you talk to a person,
- you want answers read back while your hands and eyes are busy.

If neither is you, stop here. Adding voice is extra moving parts for no gain.

## If you do want it: free, local tools

You build this yourself, and it can be done for free and entirely on your own machine - nothing sent to a server, in keeping with how the rest of the OS works.

- **Ears (speech to text):** [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - a fast local port of OpenAI's Whisper. Runs offline on your own CPU or GPU, no API key, no per-minute cost. It turns what you say into text the OS reads as if you had typed it.
- **Mouth (text to speech):** [Piper](https://github.com/rhasspy/piper) - a small, fast, local neural voice. Runs offline, no key, no cost. It reads the OS's answer aloud.

Both are free and open-source. Both run locally. Neither is required.

## The honest shape of it

This is provision and direction, not a wired feature:

- **What ships:** the Brain (your files) and the Skills that read and write them. Text in, text out. Complete.
- **What you would add:** a thin local loop - your microphone into faster-whisper into the OS, and the OS's reply into Piper out to your speakers. That loop is yours to assemble; it is not in this repo and there is no command for it.
- **The honest tradeoff:** fully local and free (faster-whisper plus Piper) is the right default and has a small amount of lag. A real-time, no-lag spoken conversation generally needs a streaming voice service, which is a paid dependency and breaks the free-local-first posture - so it is a deliberate choice, not the default. Decide which you actually need before building anything.

## What this page is not

It is not a claim that the OS talks or listens today. It does not. If you read "the OS can speak", read it as "the OS can be given a mouth, by you, with free local tools, if you decide it is worth the wiring". Until you build that loop, the OS is text - and text is the whole product, not a lesser version of it.
