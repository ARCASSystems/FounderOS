# Capture anywhere - feeding the brain when you are not at the laptop

The honest problem: the real work happens away from the desk - a site visit, a hallway conversation, a drive home full of decisions. If a thought cannot land in the brain until you are back at a laptop, it usually never lands at all.

Founder OS solves this with one mental model: **get the thought into the inbox any way you can; the OS files it.** You never structure a capture. You dump it, and the next "catch up" sweeps it into `brain/rants/` with provenance, checks the names, and offers to distil it.

One constraint shapes everything here: the OS runs on your Claude subscription alone - no API key, no server listening for you. So transcription happens on your phone (every phone does this well now), and the OS ingests **text**. Nothing below needs a new paid tool.

## The channels, ranked by friction

Pick ONE that fits how your day actually runs. The setup wizard asks; you can change anytime.

**1. A voice-notes app with an MCP connection (lowest friction once wired).**
If you use a meeting-notes or voice-memo tool that offers an MCP server, bind it as `meeting_notes` in `stack.json` (say "connect my notes tool"). After a one-time sign-in, "catch up" can pull your transcripts itself - you record on the phone and do nothing else. This is the only channel where the OS fetches; all others are you delivering text.

**2. Synced-folder dictation (low friction, fully local, no new account).**
Point a phone automation at your cloud-synced OS folder: an iOS Shortcut or Android automation that takes dictation and writes a text file into `capture/inbox/`. Record, done - the file is waiting at the next session. This is the most private channel: your words touch only your own storage.

**3. Email to self (zero setup, works today).**
Send the thought to yourself with a marker subject like `os:` while it is fresh. At the next session, paste it (or, with an email MCP connected, ask the OS to pull them). Slightly higher friction at ingest, unbeatable at capture.

**4. Saved messages (zero setup, works today).**
Telegram Saved Messages, a WhatsApp chat with yourself, any notes app. Voice-note it or type it, then paste the accumulated pile at the next session and say "catch up". The paste IS the capture - the OS does the rest.

## What happens to a capture

1. Filed to `brain/rants/<date>-<slug>.md`, raw, with `processed: false` and its source recorded. Your words are never rewritten or summarized at capture time.
2. **The name pass runs.** Dictation mangles proper nouns - names, companies, products come out wrong more often than any other class of word. The OS checks every name against your glossary (`context/names.md`): known names are corrected, unknown names stay as heard marked `(sp?)`, and you get ONE batch question, not an interrogation. Every correction you make teaches the glossary, so the same mishearing never survives twice.
3. **Numbers and facts are never "fixed".** A price, date, or term the OS is unsure of stays as captured with a marker. An uncertain marked fact is honest; a confidently corrected wrong one poisons the brain.
4. You say "dream" when you want the pile distilled into patterns, flags, parked decisions, and needs. Capture and distillation are deliberately separate - dumping must stay effortless.

## If the same event arrives twice

Two sources covering one conversation (your voice memo plus a notes tool) are reconciled by a fixed hierarchy - a document beats agreement between sources, agreement beats a single source, and your own correction beats everything. A name or number the sources disagree on is surfaced as provisional, never silently picked.

## What this is not

No always-on listener. Nothing here runs while you are away - the OS is session-based by design (that is the security story, see [why-local-first.md](why-local-first.md)). Captures accumulate wherever you drop them and are swept when you next sit down. The OS never claims background behavior it does not have.
