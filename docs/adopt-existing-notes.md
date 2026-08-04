# Adopting Founder OS into notes you already have

Almost nobody starts from zero. If you have an Obsidian vault, a folder of markdown notes, or years of journals on disk, you do not have to choose between your history and the OS. Setup has an adopt path: the OS moves in next to your notes, and your notes stay exactly as they are.

## How to trigger it

Say any of these to start setup:

- "set up Founder OS inside my vault"
- "I already have notes - set up around them"
- "adopt my existing notes"

Or run setup normally and answer the knowledge-base question with Obsidian or local files - the wizard asks one follow-up: inside your existing folder, or a fresh one. Both are fine. Fresh is the default if you are unsure.

## What the adopt path does

1. **Creates only what is missing.** The OS adds its own folders (`brain/`, `context/`, `cadence/`, and the rest) next to yours. A file that already exists is never written over - not even `CLAUDE.md`; if you have one, the wizard shows its proposal as a diff and you say yes or no.
2. **Asks before any collision.** If you already have a folder with a name the OS uses, the wizard names it and asks how to handle it. Nothing is resolved silently.
3. **Leaves your folders alone, and says so.** At the end, the wizard lists your untouched folders back to you so you can see the boundary held.

## What your old notes can and cannot do afterwards

Honest version, because this is the part that matters:

- **Claude reads your notes on demand.** Point at any file or folder, ask about a topic and name where it lives - it all works, adopted or not.
- **Your Obsidian links keep working.** The OS writes the same `[[wikilink]]` syntax your vault already uses, and Obsidian reads the OS's files as ordinary notes.
- **The OS's structured search covers the OS's own folders.** Timeline ("what happened in March"), ID lookup, and the brain pass read the brain and context layers - not your pre-existing folders. Your old notes are not lost to Claude, but they are not in that index.
- **The bridge is "capture this".** When an old note starts mattering to current work, say so - its takeaways get filed into `brain/knowledge/` with a stable ID, where structured search reads. Adopt as you go. Nothing needs migrating up front, and most notes never need migrating at all.

## Obsidian specifics

- Your `.obsidian/` config folder is never touched, and stays out of version history if you turn history on later.
- Open the folder as a vault the way you always have. The OS's files show up as ordinary notes; the graph fills in as cross-references accumulate. More detail in [tools-and-mcps.md](tools-and-mcps.md).

## If you would rather keep things separate

Also fine, and simpler: install into a fresh folder and point at your old notes whenever you need them ("read my old pricing notes at ~/vault/Business/pricing.md"). You can adopt later - the adopt path works the same on an existing install by moving the OS folders into your vault, though setup into the right place on day one is the cleaner road.
