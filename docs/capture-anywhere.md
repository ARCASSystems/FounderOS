# Capture anywhere - feeding the brain when you are not at the laptop

The honest problem: the real work happens away from the desk - a site visit, a hallway conversation, a drive home full of decisions. If a thought cannot land in the brain until you are back at a laptop, it usually never lands at all.

Founder OS solves this with one mental model: **get the thought into the inbox any way you can; the OS files it.** You never structure a capture. You dump it, and the next "catch up" sweeps it into `brain/rants/` with provenance, checks the names, and offers to distil it.

One constraint shapes everything here: the OS runs on your Claude subscription alone - no API key, no server listening for you. So transcription happens on your phone (every phone does this well now), and the OS ingests **text**. Nothing below needs a new paid tool.

## The channels, ranked by friction

Pick ONE that fits how your day actually runs. The setup wizard asks; you can change anytime.

**1. A voice-notes app with an MCP connection (lowest friction once wired).**
If you use a meeting-notes or voice-memo tool that offers an MCP server, bind it as `meeting_notes` in `stack.json` (say "connect my notes tool"). After a one-time sign-in, "catch up" can pull your transcripts itself - you record on the phone and do nothing else. This is the only channel where the OS fetches; all others are you delivering text.

**2. Synced-folder dictation (low friction, no new account, your own synced storage).**
Point a phone automation at your cloud-synced OS folder: an iOS Shortcut or Android automation that takes dictation and writes a text file into `capture/inbox/`. Record, done - the file is waiting at the next session. This is the most private channel: your words touch only your own storage.

**3. Email to self (zero setup, works today).**
Send the thought to yourself with a marker subject like `os:` while it is fresh. At the next session, paste it (or, with an email MCP connected, ask the OS to pull them). Slightly higher friction at ingest, unbeatable at capture.

**4. Saved messages (zero setup, works today).**
Telegram Saved Messages, a WhatsApp chat with yourself, any notes app. Voice-note it or type it, then paste the accumulated pile at the next session and say "catch up". The paste IS the capture - the OS does the rest.

## Setting up the synced folder, step by step

Channel 2 has a prerequisite the one-line version skips: your phone can only drop files into the OS folder if that folder lives somewhere your phone can reach. A default install (`~/founder-os`) is not synced anywhere. Fixing that takes about five minutes, once:

**1. Put the OS folder inside your cloud folder.** Close Claude Code, then move the whole OS folder into the place that already syncs - `OneDrive/Documents/` on most Windows machines, iCloud Drive or Dropbox on a Mac. Reopen it in Claude Code from the new location. The OS keeps working: it is plain files and every script finds its own folder, wherever it sits. Read the five things below first, because a synced folder changes who holds a copy.

- One machine at a time is the honest rule. Cloud sync has no merge - if two machines edit the same file in the same window, the sync tool keeps a "conflicted copy" rather than losing data, but cleaning those up is on you. If you have turned version history on, the same applies to the history folder; prefer finishing on one machine before opening the other.

**Know these five things before you move the folder into a synced place:**

1. Everything in the folder goes to the sync provider, including the keys in `.env`. If you keep keys there (a Telegram bot, a voice tier), they now live with that provider too.
2. Sync conflicts can damage version history. The history lives in a hidden `.git` folder, and a sync tool that copies it while two machines write can leave it broken. Finish on one machine before you open the other.
3. iCloud Drive can move files off your computer to save space, and keep only a placeholder. Keep the Founder OS folder downloaded (on recent macOS versions, right-click it in Finder and choose Keep Downloaded) so the OS can always read its own files.
4. Claude Code's memory folder for this project is tied to the folder's old path. After you move the folder, open it in Claude Code and say "verify the OS".
5. Move the folder only while Claude Code is closed, and reopen it from the new place.

**2. iPhone: a two-action Shortcut.** Open Shortcuts, create a new shortcut: **Dictate Text**, then **Save File** into your cloud folder at `founder-os/capture/inbox/` (iCloud Drive and Dropbox both appear in Save File; OneDrive is patchier in Shortcuts - if that is your cloud, the OneDrive app's own upload works as the fallback). Name it "Brain dump", add it to your home screen. From then on: tap, talk, done.

**3. Android: a folder-pairing app.** Use any voice or notes app that saves text files to a folder, and pair that folder to your cloud with a sync app (FolderSync is the common one; Dropsync for Dropbox). Android setups vary by phone more than iPhone does - if the pairing fights you, email-to-self (channel 3) costs nothing and works identically everywhere.

**4. That is all.** Filenames do not matter, the OS reads any text file in the inbox. Back at the laptop, say "catch up" and the pile gets filed, names checked, provenance kept.

## What happens to a capture

1. Filed to `brain/rants/<date>-<slug>.md`, raw, with `processed: false` and its source recorded. Your words are never rewritten or summarized at capture time.
2. **The name pass runs.** Dictation mangles proper nouns - names, companies, products come out wrong more often than any other class of word. The OS checks every name against your glossary (`context/names.md`): known names are corrected, unknown names stay as heard marked `(sp?)`, and you get ONE batch question, not an interrogation. Every correction you make teaches the glossary, so the same mishearing never survives twice.
3. **Numbers and facts are never "fixed".** A price, date, or term the OS is unsure of stays as captured with a marker. An uncertain marked fact is honest; a confidently corrected wrong one poisons the brain.
4. You say "dream" when you want the pile distilled into patterns, flags, parked decisions, and needs. Capture and distillation are deliberately separate - dumping must stay effortless.

## If the same event arrives twice

Two sources covering one conversation (your voice memo plus a notes tool) are reconciled by a fixed hierarchy - a document beats agreement between sources, agreement beats a single source, and your own correction beats everything. A name or number the sources disagree on is surfaced as provisional, never silently picked.

## What this is not

No always-on listener. Nothing here runs while you are away - the OS is session-based by design (that is the security story, see [why-local-first.md](why-local-first.md)). Captures accumulate wherever you drop them and are swept when you next sit down. The OS never claims background behavior it does not have.
