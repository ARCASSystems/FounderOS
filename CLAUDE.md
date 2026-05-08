# Founder OS - Claude Code Plugin

> This is the generic Founder OS plugin. Install it to give Claude Code the context of who you are, how you work, what you are building, and what you need help with. It replaces 20+ productivity SaaS tools with a single structured Claude Code environment.

## What This Is

Founder OS is a Claude Code plugin that installs an operating system for one founder: your identity, your roles, your priorities, your cadence, your scars - so the AI you work with stops treating you like an anonymous user and starts working like a chief of staff who has been with you for five years.

It is NOT a framework. It is NOT a multi-tenant AI platform. It is a product you install once and run every day.

## Quick Start

Run the setup wizard to personalize this for your situation:

```
/founder-os:setup
```

The wizard asks you questions about who you are, what you run, what tools you use, and what is slowing you down. From your answers it generates all the operating files in this repo - personalized to you. Takes 15-20 minutes the first time.

## Updates

Founder OS ships with `/founder-os:update` to pull the latest System Layer files (skills, templates, commands, hooks) without touching your personal data. Run it whenever you want. The command tells you what is changing before applying.

Your User Layer (identity, context, cadence, brain, network, clients) is never auto-updated. That is your data and stays exactly where you put it.

Commands:
- `/founder-os:update` - check for updates, show changelog, apply on confirmation
- `/founder-os:update check` - dry-run, report local vs remote version only
- `/founder-os:update rollback` - revert the last update

## How It Works

After setup, every Claude Code session starts with this CLAUDE.md loaded. Claude reads your context from six files:

- `core/identity.md` - who you are, how you work, what you are building
- `context/priorities.md` - what matters this week and this quarter
- `context/decisions.md` - open decisions, parked items, resolved choices
- `context/clients.md` - prospects, active engagements, closed wins
- `cadence/daily-anchors.md` - today's focus and commitments
- `cadence/weekly-commitments.md` - current sprint and retro

Two more files (`brain/log.md` and `brain/flags.md`) load on demand when you ask Claude to scan history or check what is being avoided.

`core/avatar.md` is your behavioral profile. Skills load it on demand when behavioral context matters. It is not boot-loaded.

The brain layer also holds two capture surfaces and a knowledge store. `brain/rants/` captures raw voice dumps via `/rant`. `/dream` distils unprocessed rants into patterns, flags, parked decisions, and client signals. `brain/knowledge/` holds distilled notes from books, calls, and articles, which `proposal-writer` and `strategic-analysis` read back when relevant.

A separate auto-memory layer at `~/.claude/projects/<slug>/memory/MEMORY.md` (set up by the wizard) holds behavioral guards that persist across every session. Add a guard whenever you correct Claude on something that would otherwise come up again.

When Claude knows all of this, it can give you recommendations instead of asking you to explain context every time.

## Empty-state behavior

If any of the 6 context files above is missing on session start, the OS is not yet set up. Do not fabricate context, do not invent past decisions, do not pretend to know the founder. Reply with this exact message and stop:

> Founder OS is installed but not personalized yet. Run /founder-os:setup to generate your identity, priorities, and cadence files (15 to 20 min). Or ask me to bootstrap minimal versions from the templates in templates/.

This rule is non-negotiable. A wrong recommendation built on hallucinated context is worse than no recommendation at all.

## Cloud or Web Claude Behavior

Founder OS has two supported surfaces:

- Notion Starter Kit for Claude web or desktop Projects
- Claude Code plugin for local markdown, commands, hooks, and git history

If this repo is opened in Claude web, desktop, a cloud IDE, or another assistant that cannot run Claude Code slash commands, treat it as a system layer only. Do not claim that `/founder-os:setup`, `/founder-os:update`, hooks, or local writes have run unless the environment actually supports them.

If the founder context files are missing, stop and route the user to the Notion quickstart or the Claude Code setup command. Do not invent identity, clients, revenue, priorities, decisions, commitments, or past business context.

## Roles

Founder OS models the operating functions of a business as four behavioural modes you can switch between:

- **COO** (default) - daily operations, calendar, commitments, client delivery
- **BD** - pipeline, outreach, deals
- **CMO** - content, brand, marketing, social
- **Chief of Staff** - weekly retro, stall detection, meta-layer

CFO, CSO, and CTO are not shipped as default modes. Financial questions route through the unit-economics skill. Tech and automation questions are best handled by Claude Code itself. If you want a CFO or CTO lens added later, scaffold one with skill-creator.

## Tool Stack

Founder OS adapts to your tools, not the other way around. During setup, you tell it which tools you use. It generates the right integration config.

Supported adapters (configured during setup):
- Knowledge base: Notion, Obsidian, Google Drive, or local-only
- Email: Gmail, Outlook, Apple Mail
- Calendar: Google Calendar, Outlook Calendar
- Automation: n8n, Make, Zapier
- CRM: Notion DB, HubSpot, Airtable, or none

## Wiki Conventions

Founder OS is built like a personal wiki the LLM maintains. Three layers underneath your daily files:

- **raw/** - immutable source documents (transcripts, articles, books, threads). Once written, never edited. See `raw/README.md` for the frontmatter spec. Scaffolded on first `/founder-os:ingest` use.
- **The wiki layer** - your operating files: `core/`, `context/`, `cadence/`, `brain/` (including `brain/knowledge/` for distilled notes and `brain/rants/` for raw dumps), `network/`. Edited by skills as you work.
- **The schema** - this `CLAUDE.md` file. Tells Claude how the layers connect.

Two operations the OS supports natively:

- **Ingest** (`/founder-os:ingest <source>`) - process a source into raw/ with provenance, then propose wiki updates you approve. Different from `knowledge-capture`: ingest preserves the source, knowledge-capture organizes takeaways without source preservation. Use whichever fits.
- **Lint** (`/founder-os:lint`) - read-only audit. Flags broken cross-references, orphan pages, stale time-sensitive content, provenance gaps, and contradictions. Never auto-fixes. Recommended cadence: weekly via `/loop weekly /founder-os:lint`.

**Cross-references between wiki files use `[[page-name]]` syntax.** Example: a decision in `context/decisions.md` referencing your identity might write `as committed in [[core/identity.md]]`. The lint skill catches `[[]]` links pointing to files that don't exist. The wiki-build skill (`/founder-os:wiki-build`, v1.4) walks all wiki files, extracts the `[[wikilinks]]`, and writes them as a machine-readable graph in `brain/relations.yaml`. Idempotent. Run after a session that added cross-references. Existing files that don't use the convention are not retrofitted. The convention applies forward.

All wiki operations are opt-in. The OS works the same with or without them.

### Brain substrate (v1.4)

Three additions sit underneath the daily files. None require setup beyond running `/founder-os:setup` once.

- **`rules/entry-conventions.md`** - bi-temporal + decay convention for entries in `context/decisions.md`, `context/priorities.md`, and the brain layer. Add `Decay after: 14d` (or a date) to a flag and the SessionStart brief surfaces it for keep/kill review when it expires. Add `Superseded by:` + `Invalidated on:` to a decision instead of overwriting it. Convention is forward-only (no backfill).
- **`system/quarantine.md`** - catch-net for silent hook and scheduled-task failures. Helper functions for PowerShell and bash are in the file. SessionStart counts ACTIVE entries. Hooks fail silently by design. Quarantine makes failure visible without blocking the session.
- **`rules/approval-gates.md`** - explicit list of what auto-runs (brain/log appends, wiki-build, archive moves), what requires your yes (identity edits, decision supersession, sends, public pushes), and what is blocked outright (force push, hard reset, AI attribution in commits). Customize to match how you want the OS to behave.

The SessionStart brief (`.claude/hooks/session-start-brief.sh` on Mac/Linux/git-bash, `.claude/hooks/session-start-brief.ps1` on Windows, both registered in `.claude/settings.json`) reads all three at every session open and surfaces what needs attention in one screen.

### Runtime brain context (v1.10)

`scripts/brain-snapshot.py` writes a small deterministic markdown payload to `brain/.snapshot.md` (open flags, this week's must-do, recent decisions, voice and brand fields, staleness). Nine output-producing skills (meeting-prep, weekly-review, strategic-analysis, decision-framework, founder-coaching, knowledge-capture, unit-economics, priority-triage, brain-log) read it at task time so the output reflects current state instead of starting cold. Snapshot is opt-in via the file existing. Skills proceed with profile-only context if it is missing.

The companion `brain-pass` skill (`/founder-os:brain-pass "<question>"`) synthesises an answer across the brain layer and returns Answer, Evidence, Confidence, and Gaps with stable-ID citations. No embeddings. No API call. Free-tier accessible. `meeting-prep` and `linkedin-post` auto-invoke brain-pass before producing output and fall back to `scripts/query.py` if it is unavailable.

`scripts/memory-diff.py` (added v1.12) is read by the SessionStart brief on every session open. It walks `clients/<slug>/` and flags any folder that has no matching entry in your auto-memory (`MEMORY.md` or `project_<slug>.md`). Closes the gap where a cloud or parallel local Claude session creates a client folder that the next local session boots blind to. Hook-only feature. No new skill, no new command.

## Agent Teams (recommended)

Claude Code has an experimental Agent Teams feature that turns sequential workflows into parallel specialist teams. For a solo founder running Founder OS, this is the difference between a meeting flow that runs prep, capture, log, and client-update one after another, and the same flow running as parallel specialists that finish in a fraction of the time.

You do not need Agent Teams to run Founder OS. Subagents are the stable default and cover most real work. Agent Teams is an opt-in upgrade once you are comfortable with the system.

**What it adds:**

- Parallel execution for the weekly insights brief (state files read in parallel, not sequence)
- Multi-step proposal flow (scope, terms, voice pass, deliverable format) run as specialist agents
- Any chained skill invocation where the steps do not depend on each other

**How to enable:**

1. Set the environment variable: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
2. Use Opus 4.6 as your model
3. Restart Claude Code

No other config needed. Founder OS skills and commands work the same way. The flag only changes how multi-agent workflows execute under the hood.

**Source:** https://github.com/victordelrosal/agent-teams-claude-code is the field manual for this feature. Read it before you flip the flag on a real deliverable.

## Fabric (hooks, commands, scheduled tasks)

Founder OS ships with a thin fabric layer that makes the files behave like an operating system, not just documentation.

**Slash commands** (`.claude/commands/`)
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

**Hooks** (`.claude/hooks/`)
- SessionStart brief (v1.4 + v1.12) - surfaces open flags, stale cadence, pending decisions, [FILL] client rows, ACTIVE quarantine entries, Review Due entries (past their `Decay after:` date), and `clients/<slug>/` folders without an auto-memory entry. One screen at session open. Registered on the SessionStart event in `.claude/settings.json`. Quietly skips if the repo is not a Founder OS install (no `core/identity.md`).
- Session-close revenue-loop check - warns if outreach verbs appear in recent brain/log.md without a matching context/clients.md update. Registered on the Stop event in `.claude/settings.json`.

**Windows note:** Hooks invoke bash. If you are on Windows, the install requires git-bash (which ships with Git for Windows). Without it, hooks will silently no-op. PowerShell-only users should switch the hook commands in `.claude/settings.json` to invoke the `.ps1` mirrors in `.claude/hooks/` (PowerShell versions ship alongside the bash versions).

**Scheduled tasks** (optional, configured by you via the scheduled-tasks MCP if you install it). Founder OS does not ship any scheduled tasks out of the box. Two patterns founders commonly add once their cadence is established:

- A weekly LinkedIn draft pass that reads your story bank and writes drafts to your content pipeline
- A weekly insights brief that synthesises last-week patterns, stalls, and revenue-loop health

If you have not installed the scheduled-tasks MCP, ignore this section. Nothing in Founder OS depends on it.

All fabric pieces are optional. The slash commands ship active. Hooks register in `.claude/settings.json` and ship active. Scheduled tasks are bring-your-own.

## Skills (39 included)

| Skill | Purpose |
|-------|---------|
| founder-os-setup | Interactive setup wizard. |
| readiness-check | OS health audit. Routed via `/founder-os:status`. |
| ingest | File a source into `raw/` with provenance. Routed via `/founder-os:ingest`. |
| lint | Read-only audit of wiki integrity. Routed via `/founder-os:lint`. |
| wiki-build | Walk markdown, extract `[[wikilinks]]`, refresh `brain/relations.yaml`. |
| query | Graph and file retrieval. Routed via `/founder-os:query`. |
| brain-snapshot | Writes `brain/.snapshot.md`, the runtime context payload nine output skills read at task time. |
| brain-pass | Synthesised answer across the brain layer with stable-ID citations. Routed via `/founder-os:brain-pass`. |
| audit | Composite health report. Routed via `/founder-os:audit`. |
| weekly-review | Structured weekly retro and sprint roll. |
| priority-triage | Cut the list to what actually matters. |
| brain-log | Session logging and pattern capture. |
| decision-framework | Structured decision-making for founders. |
| forcing-questions | Gate before new initiatives start. |
| session-handoff | End-of-session state capture for continuity. |
| handoff-protocol | Human or role-to-role handoff artifact. |
| context-persistence | Source-backed context lookup before asking the user to repeat. |
| meeting-prep | Pre-meeting brief and post-meeting debrief. |
| knowledge-capture | Distilled notes in `brain/knowledge/`. |
| email-drafter | Emails in your voice. |
| sop-writer | Processes turned into delegation-ready docs. |
| founder-coaching | Bias toolkit, bottleneck check, zones. |
| bottleneck-diagnostic | Founder dependency diagnostic. |
| unit-economics | Business math, margins, break-even. |
| content-repurposer | One piece, multiple formats. |
| strategic-analysis | Market sizing, competitor analysis, opportunity assessment. |
| pre-send-check | Hard gate before any client-facing deliverable leaves your machine. |
| blind-spot-review | Second-pass review before pre-send. |
| ship-deliverable | Final deliverable ship gate. |
| approval-gates | Auto-run, ask-first, or refuse gate checks. |
| data-security | Data class and tool-safety check. |
| voice-interview | Captures your writing voice into core/voice-profile.yml. |
| brand-interview | Captures your visual brand into core/brand-profile.yml. |
| your-voice | Applies your voice profile to any written output. Every voice-coupled writing skill calls it. |
| your-deliverable-template | Produces branded documents from core/brand-profile.yml. |
| business-context-loader | Loads and completes per-company business context. |
| linkedin-post | Voice-coupled LinkedIn post writer. |
| client-update | Voice-coupled client status update writer. |
| proposal-writer | Voice and brand-coupled proposal writer. |

## Philosophy

- **Local-first.** Your data stays on your machine. Nothing is sent to a company server without your explicit consent.
- **No lock-in.** All files are plain markdown. Obsidian can read them. So can any other markdown editor. The system does not depend on a proprietary platform.
- **Boundary protection is a feature.** Saying no, parking scope, pushing back on unreasonable requests are designed in, not edge cases.
- **People first. Systems second. AI where it earns the right.**

## Commits

Commit messages follow `rules/commit-naming.md`. Subjects state the user-visible change in plain language. No version-only subjects, no AI attribution, no banned words.

## Getting Help

If something is not working, open Claude Code and say: "Help me fix [specific thing] in my Founder OS."

If you want to add a skill, role, or template: copy an existing one and modify it. The structure is self-documenting.
