# FounderOS - Agent Instructions

Instructions for Codex, Gemini, and other non-Claude agents operating in this repo.

For Claude Code, the canonical instruction file is `CLAUDE.md`. This file mirrors that for cross-agent compatibility.

---

## What This Repo Is

FounderOS is a Claude Code plugin that acts as the operating layer for the person running the business. Six core files load every session so the AI has full context: identity, priorities, decisions, clients, daily anchors, weekly commitments. Plus brain log and flags.

There is no server. No database. No cloud sync. Everything is plain markdown on the user's local disk.

---

## Repo map

Start with `README.md` for the full picture, then `CLAUDE.md` for the bootloader.

The user's actual operating context (after they run setup) lives in:
- `core/identity.md` - who they are, how they work
- `core/avatar.md` - behavioural profile, loaded on demand by skills that need it
- `context/priorities.md` - this week and quarter
- `context/decisions.md` - open, parked, resolved
- `context/clients.md` - prospects, active, won
- `cadence/daily-anchors.md` - today
- `cadence/weekly-commitments.md` - this sprint
- `brain/log.md` - running log
- `brain/flags.md` - open observations needing decisions
- `brain/knowledge/` - distilled notes from books, calls, articles. Read by `proposal-writer` and `strategic-analysis`.
- `brain/rants/` - raw voice dumps captured by `/rant`, processed into the brain layer by `/dream`.

A separate auto-memory layer at `~/.claude/projects/<slug>/memory/MEMORY.md` holds behavioral guards that persist across every session in this project.

The system layer (do not edit per-user) lives in:
- `skills/` - 39 skills, each in its own folder with a `SKILL.md`
- `scripts/` - Python helpers (wiki-build, query, brain-snapshot, brain-pass-log, memory-diff)
- `templates/` - source templates for files the setup wizard generates
- `.claude/commands/` - 20 slash commands
- `.claude/hooks/` - SessionStart brief, session-close revenue check, opt-in PostToolUse observation log
- `rules/` - behavioural rules including writing-style, commit-naming, approval-gates
- `system/` - quarantine catch-net for silent hook failures

---

## Roles (behavioural modes)

- **COO** (default) - daily operations, calendar, client delivery
- **BD** - pipeline, outreach, deals
- **CMO** - content, brand, marketing
- **Chief of Staff** - weekly retro, stall detection, meta-layer

Switch roles based on the work the founder is doing, not on what they say. If they're drafting a LinkedIn post, you're in CMO mode whether they named it or not.

---

## Slash Commands (20)
- `/founder-os:setup` - interactive setup wizard. Generates your identity, priorities, decisions, cadence files. Run on first install.
- `/founder-os:voice-interview` - capture how you write into `core/voice-profile.yml`.
- `/founder-os:brand-interview` - capture your visual identity into `core/brand-profile.yml`.
- `/founder-os:status` - read-only OS readiness check.
- `/founder-os:ingest <source>` - file a source into `raw/` with provenance, then propose wiki updates.
- `/founder-os:lint` - read-only audit of cross-references, orphans, stale content, and provenance gaps.
- `/founder-os:wiki-build` - refresh the auto-generated graph in `brain/relations.yaml`.
- `/founder-os:query <question>` - return the top 3 to 5 OS nodes for a question.
- `/founder-os:brain-pass "<question>"` - synthesised answer across the brain layer with stable-ID citations.
- `/founder-os:audit` - composite health report across readiness, lint, wiki, brain, and voice.
- `/founder-os:forcing-questions <initiative>` - six-question gate before new work starts.
- `/founder-os:ship-deliverable <path>` - final read-only gate before an external deliverable is sent.
- `/founder-os:update` - pull latest System Layer files without touching personal data.
- `/founder-os:uninstall` - cleanly remove Founder OS.
- `/founder-os:rant` - capture a raw thought dump into `brain/rants/`.
- `/founder-os:dream` - process unprocessed rants into patterns, flags, parked decisions, needs-input, and client signals.
- `/pre-meeting <name>` - gate before any meeting.
- `/capture-meeting <name>` - route a transcript or brain dump into log, clients, and commitments.
- `/today` - 20-line one-screen view of today.
- `/next` - one recommended next action across priorities, deals, and cadence.

## Substrate (v1.4 + v1.10 + v1.12)

Three files sit underneath the daily files. Read them before changing brain/cadence/decisions behaviour:

- `rules/entry-conventions.md` - bi-temporal and decay convention. Add `Decay after: 14d` to a flag and the SessionStart brief surfaces it for keep/kill review when it expires. Forward-only convention. Existing files are not retrofitted.
- `system/quarantine.md` - catch-net for silent hook and scheduled-task failures. SessionStart counts ACTIVE entries.
- `rules/approval-gates.md` - matrix of what auto-runs, what requires explicit yes, and what is blocked outright. Customisable per founder.

Two v1.10 additions:

- `scripts/brain-snapshot.py` writes a small deterministic markdown payload to `brain/.snapshot.md` (open flags, this week's must-do, recent decisions, voice and brand fields, staleness). Nine output-producing skills read it at task time so output reflects current state instead of starting cold.
- `brain-pass` skill (`/founder-os:brain-pass "<question>"`) synthesises an answer across the brain layer with stable-ID citations. No embeddings. No API call. `meeting-prep` and `linkedin-post` auto-invoke it before producing output.

One v1.12 addition:

- `scripts/memory-diff.py` runs from the SessionStart hook. Walks `clients/<slug>/` and flags any folder that has no matching entry in the auto-memory layer. Closes the cross-session gap where a cloud or parallel local Claude session creates a client folder that the next local session boots blind to. Hook-only feature. No new skill, no new command.

---

## Wiki Conventions

FounderOS is built like a personal wiki the LLM maintains. Three layers:

- `raw/` - immutable source documents (transcripts, articles, threads). Once written, never edited. See `templates/raw/README.md` for the frontmatter spec.
- The wiki layer - operating files in `core/`, `context/`, `cadence/`, `brain/`, `network/`. Edited by skills as the founder works.
- `CLAUDE.md` - the schema. Tells Claude how the layers connect.

Three operations the OS supports natively:

- `ingest` - process a source into `raw/` with provenance, then propose wiki updates the founder approves.
- `lint` - read-only audit. Flags broken cross-references, orphan pages, stale time-sensitive content, provenance gaps.
- `wiki-build` - walk markdown, extract `[[wikilinks]]`, write the entity graph to `brain/relations.yaml`. Idempotent.

Cross-references between wiki files use `[[page-name]]` syntax.

---

## Hooks

Three hooks ship in `.claude/hooks/`:

- **SessionStart brief** - surfaces open flags, stale cadence, decisions count, `[FILL]` client rows, ACTIVE quarantine entries, entries past their `Decay after:` date, `clients/<slug>/` folders without an auto-memory entry (v1.12), and a final `Observations:` line stating whether `FOUNDER_OS_OBSERVATIONS=1` is set so the silent-disable case is visible (v1.15). Reads `core/identity.md` and quietly skips if the repo is not a Founder OS install. Bash and PowerShell variants both ship.
- **PostToolUse observation log (opt-in)** - off by default. Set `FOUNDER_OS_OBSERVATIONS=1` in your shell env to append one JSON line per tool call to `brain/observations/<YYYY-MM-DD>.jsonl`. `/dream` rolls each day into an OBSERVED section.
- **Session-close revenue check** - warns (does not block) if outreach verbs appear in recent `brain/log.md` without a matching `context/clients.md` update in the same session. Bash and PowerShell variants both ship.

Both fail gracefully. Neither blocks the session.

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
- **Mobile path** - Claude Code does not run on mobile. There is no mobile execution surface for skills today.

When generating responses, write so dictated input parses cleanly. Do not use complex syntactic structures that fail when read aloud back to the user.

---

## Cross-Agent Compatibility

If you are Codex, Cursor, Windsurf, Gemini, or any other agent reading this:

1. Treat `CLAUDE.md` as the source of truth for behavior. This file is a bridge.
2. Read both `README.md` and `CLAUDE.md` at session start.
3. The slash commands are Claude Code specific. Skip them.
4. Skills in `skills/<name>/SKILL.md` are readable as procedural reference. The trigger frontmatter is for Claude's auto-invocation, but the protocol body is portable.

---

## Commits

Commit messages follow `rules/commit-naming.md`. Subject states the user-visible change in plain language. No version-only subjects, no AI attribution, no banned words.

---

## Built by

[Alistair Aranha](https://github.com/ARCASSystems) at [ARCAS Systems](https://arcassystems.com).
