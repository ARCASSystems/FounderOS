# FounderOS - Agent Instructions

Instructions for Codex, Gemini, and other non-Claude agents operating in this repo.

For Claude Code, the canonical instruction file is `CLAUDE.md`. This file mirrors that for cross-agent compatibility.

---

## What This Repo Is

FounderOS is a Claude Code plugin that acts as the operating layer for a solo founder. Six core files load every session so the AI has full context: identity, priorities, decisions, clients, daily anchors, weekly commitments. Plus brain log and flags.

There is no server. No database. No cloud sync. Everything is plain markdown on the user's local disk.

---

## How to Navigate

Start with `README.md` for the full picture, then `CLAUDE.md` for the bootloader.

The user's actual operating context (after they run setup) lives in:
- `core/identity.md` - who they are, how they work
- `context/priorities.md` - this week and quarter
- `context/decisions.md` - open, parked, resolved
- `context/clients.md` - prospects, active, won
- `cadence/daily-anchors.md` - today
- `cadence/weekly-commitments.md` - this sprint
- `brain/log.md` - running log
- `brain/flags.md` - open observations needing decisions

---

## Roles (behavioural modes)

- **COO** (default) - daily operations, calendar, client delivery
- **BD** - pipeline, outreach, deals
- **CMO** - content, brand, marketing
- **Chief of Staff** - weekly retro, stall detection, meta-layer

Switch roles based on the work the founder is doing, not on what they say. If they're drafting a LinkedIn post, you're in CMO mode whether they named it or not.

---

## Slash Commands

- `/founder-os:setup` - first-run wizard
- `/founder-os:voice-interview` - capture writing voice into `core/voice-profile.yml`
- `/founder-os:brand-interview` - capture visual identity into `core/brand-profile.yml`
- `/founder-os:status` - read-only OS readiness check
- `/founder-os:update` - pull System Layer updates without touching user data
- `/founder-os:uninstall` - cleanly remove (default mode preserves data; --purge wipes everything)
- `/today` - 20-line daily dashboard
- `/next` - one recommended next action
- `/pre-meeting` - hard gate before any meeting
- `/capture-meeting` - route a transcript or brain dump to log + clients + commitments

These only work in Claude Code. Other agents reading this repo should treat the slash command files in `.claude/commands/` as procedural reference, not invokable.

---

## What Not to Do

- Do not invent identity, priorities, decisions, clients, or revenue from context that is not in the files
- Do not modify the user's data files (`core/`, `context/`, `cadence/`, `brain/`) without their explicit instruction
- Do not skip the setup wizard if context files are missing - point the user to it
- Do not operate the FounderOS as if it were a disposable test install. After setup, the user's working directory IS their OS - treat it accordingly

---

## Voice Input

FounderOS is built for dictation. The user is expected to talk to the AI, not type long prompts.

- **Claude Code desktop** has built-in dictation. This is the primary input method.
- **Wispr Flow** is an optional power-user upgrade for users who want a system-wide dictation overlay.
- **Mobile path** - skills work via typed input. Do not assume voice input on mobile.

When generating responses, write so dictated input parses cleanly. Do not use complex syntactic structures that fail when read aloud back to the user.

---

## Cross-Agent Compatibility

If you are Codex, Cursor, Windsurf, Gemini, or any other agent reading this:

1. Treat `CLAUDE.md` as the source of truth for behavior. This file is a bridge.
2. Read both `README.md` and `CLAUDE.md` at session start.
3. The slash commands are Claude Code specific. Skip them.
4. Skills in `skills/<name>/SKILL.md` are readable as procedural reference. The trigger frontmatter is for Claude's auto-invocation, but the protocol body is portable.

---

## Built by

[Alistair Aranha](https://github.com/ARCASSystems) at [ARCAS Systems](https://arcassystems.com).
