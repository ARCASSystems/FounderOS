# Founder OS — Claude Code Plugin

> This is the generic Founder OS plugin. Install it to give Claude Code the context of who you are, how you work, what you are building, and what you need help with. It replaces 20+ productivity SaaS tools with a single structured Claude Code environment.

## What This Is

Founder OS is a Claude Code plugin that installs an operating system for one founder: your identity, your roles, your priorities, your cadence, your scars — so the AI you work with stops treating you like an anonymous user and starts working like a chief of staff who has been with you for five years.

It is NOT a framework. It is NOT a multi-tenant AI platform. It is a product you install once and run every day.

## Quick Start

Run the setup wizard to personalize this for your situation:

```
/founder-os:setup
```

The wizard asks you questions about who you are, what you run, what tools you use, and what is slowing you down. From your answers it generates all the operating files in this repo — personalized to you. Takes 15-20 minutes the first time.

## Updates

Founder OS ships with `/founder-os:update` to pull the latest System Layer files (skills, templates, commands, hooks) without touching your personal data. Run it whenever you want. The command tells you what is changing before applying.

Your User Layer (identity, context, cadence, brain, network, clients) is never auto-updated. That is your data and stays exactly where you put it.

Commands:
- `/founder-os:update` - check for updates, show changelog, apply on confirmation
- `/founder-os:update check` - dry-run, report local vs remote version only
- `/founder-os:update rollback` - revert the last update

## How It Works

After setup, every Claude Code session starts with this CLAUDE.md loaded. Claude reads your context from five files:

- `core/identity.md` — who you are, how you work, what you are building
- `context/priorities.md` — what matters this week and this quarter
- `context/decisions.md` — open decisions, parked items, resolved choices
- `cadence/daily-anchors.md` — today's focus and commitments
- `cadence/weekly-commitments.md` — current sprint and retro

When Claude knows all of this, it can give you recommendations instead of asking you to explain context every time.

## Empty-state behavior

If any of the 5 context files above is missing on session start, the OS is not yet set up. Do not fabricate context, do not invent past decisions, do not pretend to know the founder. Reply with this exact message and stop:

> Founder OS is installed but not personalized yet. Run /founder-os:setup to generate your identity, priorities, and cadence files (15 to 20 min). Or ask me to bootstrap minimal versions from the templates in templates/.

This rule is non-negotiable. A wrong recommendation built on hallucinated context is worse than no recommendation at all.

## Roles

Founder OS models the operating functions of a business as roles you can switch between:

- **COO** (default) — daily operations, calendar, commitments, client delivery
- **BD** — pipeline, outreach, deals
- **CMO** — content, brand, marketing, social
- **Chief of Staff** — weekly retro, stall detection, meta-layer
- **CFO** — financials, pricing, engagement P&L (activate when revenue starts)
- **CSO** — portfolio strategy (activate when you have 2+ revenue streams)
- **CTO** — automation, workflows, technical infrastructure (activate when you have 5+ automations)

## Tool Stack

Founder OS adapts to your tools, not the other way around. During setup, you tell it which tools you use. It generates the right integration config.

Supported adapters (configured during setup):
- Knowledge base: Notion, Obsidian, Google Drive, or local-only
- Email: Gmail, Outlook, Apple Mail
- Calendar: Google Calendar, Outlook Calendar
- Automation: n8n, Make, Zapier
- CRM: Notion DB, HubSpot, Airtable, or none

## Agent Teams (recommended)

Claude Code has an experimental Agent Teams feature that turns sequential workflows into parallel specialist teams. For a solo founder running Founder OS, this is the difference between a meeting flow that runs prep, capture, log, and client-update one after another, and the same flow running as parallel specialists that finish in a fraction of the time.

You do not need Agent Teams to run Founder OS. Subagents are the stable default and cover most real work. Agent Teams is an opt-in upgrade once you are comfortable with the system.

**What it unlocks:**

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
- `/pre-meeting <name>` - gate before any meeting; requires a capture artifact and a specific ask
- `/capture-meeting <name>` - routes a transcript or brain dump into brain/log.md + context/clients.md + commitments (M3)
- `/today` - 20-line one-screen view of today (anchor, decisions, flags, last 3 log entries, next calendar) (M4)

**Hooks** (`.claude/hooks/`)
- Session-close revenue-loop check (M2) - warns if outreach verbs appear in recent brain/log.md without a matching context/clients.md update. Registered on the Stop event in `.claude/settings.json`.

**Scheduled tasks** (examples; set yours up via the scheduled-tasks MCP)
- Weekly LinkedIn draft generation - Monday morning, reads your story bank, writes 3 drafts to your content pipeline
- Weekly insights brief - Monday morning synthesis of last-week patterns, stalls, skills fired, revenue-loop health

All fabric pieces are optional. The slash commands ship active. Hooks register in `.claude/settings.json` and ship active. Scheduled tasks require the scheduled-tasks MCP to be installed in your Claude Code environment.

## Skills (14 included)

| Skill | Purpose |
|-------|---------|
| founder-os-setup | Interactive setup wizard (start here) |
| weekly-review | Structured weekly retro and sprint roll |
| priority-triage | Cut the list to what actually matters |
| brain-log | Session logging and pattern capture |
| decision-framework | Structured decision-making for founders |
| session-handoff | End-of-session state capture for continuity |
| meeting-prep | Pre-meeting brief and post-meeting debrief |
| knowledge-capture | Notes from books, podcasts, conversations |
| email-drafter | Emails in your voice |
| sop-writer | Processes turned into delegation-ready docs |
| founder-coaching | Bias toolkit, bottleneck diagnostic, zones |
| unit-economics | Business math, margins, break-even |
| content-repurposer | One piece, multiple formats |
| strategic-analysis | Market sizing, competitive analysis, opportunity assessment |

## Philosophy

- **Local-first.** Your data stays on your machine. Nothing is sent to a company server without your explicit consent.
- **No lock-in.** All files are plain markdown. Obsidian can read them. So can any other markdown editor. The system does not depend on a proprietary platform.
- **Boundary protection is a feature.** Saying no, parking scope, pushing back on unreasonable requests are designed in, not edge cases.
- **People first. Systems second. AI where it earns the right.**

## Getting Help

If something is not working, open Claude Code and say: "Help me fix [specific thing] in my Founder OS."

If you want to add a skill, role, or template: copy an existing one and modify it. The structure is self-documenting.
