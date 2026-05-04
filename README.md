# Founder OS

The operating layer for a solo founder. Six files run your company. Claude reads them every session.

Owned by you. Powered by Claude. Talk to it.

**Setup:** Install the plugin. Open Claude Code. Run `/founder-os:setup` (15 min). Then `/founder-os:voice-interview` (10 min) and `/founder-os:brand-interview` (10 min) to unlock the writing skills. Then `/founder-os:status` anytime to audit. Full first-day path in [docs/first-day.md](docs/first-day.md).

---

## What you actually get

Six files load at every session start so Claude has full context:

- **Identity.** Who you are, how you work, what you're building.
- **Priorities.** What matters this week and this quarter.
- **Decisions.** Open, parked, resolved. Nothing falls through.
- **Clients.** Prospects, active, won, the ones you said no to.
- **Daily anchors.** Today's focus and tasks.
- **Weekly commitments.** Current sprint and retro.

Two more files load on demand:

- **Brain log.** Running thoughts, observations, patterns, flags.
- **Flags.** Stalls, role feedback, friction. Used by Chief of Staff mode for stall detection.

Around those: 27 skills covering meeting prep, knowledge capture, decisions, email drafting, content repurposing, founder coaching, weekly review, priority triage, SOPs, unit economics, strategic analysis, brain log, session handoff, pre-send check, the voice and brand interviews that capture how you write and how your work looks, the your-voice and your-deliverable-template skills that apply that profile to every output, the business-context-loader for per-company context, three voice-coupled writers (linkedin-post, client-update, proposal-writer), a readiness check, the setup wizard, the v1.3 ingest + lint pair (file external sources with provenance, audit cross-references and freshness), and the v1.4 wiki-build skill (extracts your `[[wikilinks]]` into a real entity graph at `brain/relations.yaml`).

**v1.4 also adds the substrate underneath all of this:** a decay-aware brain layer (set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires), a `system/quarantine.md` catch-net so failing hooks and scheduled tasks stop being silent, a documented approval gate matrix at `rules/approval-gates.md` so the OS knows what to do without asking and what to ask before doing, and a SessionStart brief that surfaces all of the above in one screen at every session open. Full convention spec at `rules/entry-conventions.md`.

Plus four roles as behavioural modes: COO (default), BD, CMO, Chief of Staff.

---

## Install

Three install paths. Pick the one that matches your stack. Full details in [docs/install.md](docs/install.md).

### Path A - Claude Code plugin (cleanest)

```
/plugin marketplace add ARCASSystems/FounderOS
/plugin install founder-os@founder-os-marketplace
/founder-os:setup
```

Requires Claude Code with a Pro or Max plan. If the plugin install does not work in your Claude Code version, fall back to Path B.

### Path B - Manual git clone (most reliable)

Mac, Linux, or git-bash on Windows:

```bash
git clone --depth 1 https://github.com/ARCASSystems/FounderOS.git ~/founder-os
cd ~/founder-os
```

PowerShell on Windows:

```powershell
git clone --depth 1 https://github.com/ARCASSystems/FounderOS.git "$HOME\founder-os"
cd "$HOME\founder-os"
```

Open Claude Code in that folder, then run:

```
/founder-os:setup
```

The setup wizard asks six or seven questions and generates your full operating system locally. 15 to 20 minutes the first time.

### Path C - Cloud Claude (read-only)

Open Claude.ai, attach this repo's README and CLAUDE.md as Project context, and use the safe fallback prompt below. Cloud Claude cannot run slash commands or write to local disk - it's a read-only operating mode until the Notion Starter Kit ships. See [docs/install.md](docs/install.md) for the full instructions.

---

## What ships in this repo

### Skills (27)

| Skill | What it does |
|---|---|
| founder-os-setup | Setup wizard. Generates identity, priorities, decisions, cadence, brain files. |
| readiness-check | OS health audit. Run via `/founder-os:status`. |
| ingest | File a source into `raw/` with provenance. Propose wiki updates you approve. Run via `/founder-os:ingest`. |
| lint | Read-only audit of wiki integrity. Broken links, orphans, stale content, provenance gaps. Run via `/founder-os:lint`. |
| wiki-build | Walk the OS markdown, extract `[[wikilinks]]`, refresh the auto-generated graph in `brain/relations.yaml`. Companion to lint. Run via `/founder-os:wiki-build`. |
| weekly-review | Run the weekly retro. M/S/D bucket calculation, keep/kill/escalate on flags. |
| priority-triage | Force a top-3 from a long list. Names what gets cut. |
| brain-log | Route a thought to log, cross-reference, or act with same-session follow-through. |
| decision-framework | Surface trade-offs. No false simplicity. |
| session-handoff | Pack up context for the next session or a different operator. |
| meeting-prep | Pre-meeting brief plus post-meeting debrief. |
| knowledge-capture | Capture from books, podcasts, courses, conversations (no source preservation). |
| email-drafter | Draft in your voice once setup runs the voice interview. |
| sop-writer | Turn a process into a delegation-ready document. |
| founder-coaching | Coaching loop for stuck moments. |
| unit-economics | Run the math on a deal, hire, or pricing change. |
| content-repurposer | One piece of content adapted across channels in your voice. |
| strategic-analysis | Competitive scan, market sizing, opportunity assessment. |
| pre-send-check | Hard gate before any client-facing deliverable leaves your machine. |
| voice-interview | Captures your writing voice into core/voice-profile.yml. |
| brand-interview | Captures your visual brand into core/brand-profile.yml. |
| your-voice | Writes everything as you, using your voice profile. |
| your-deliverable-template | Produces all branded documents (CV, proposal, deck, one-pager) in your visual identity. |
| business-context-loader | Loads, scans, and progressively fills a per-company context file. Routes you to the next move. |
| linkedin-post | Voice-coupled LinkedIn post writer. |
| client-update | Voice-coupled client status update writer. |
| proposal-writer | Voice and brand-coupled proposal writer. |

### Slash commands (13)

| Command | Purpose |
|---|---|
| `/founder-os:setup` | Run the setup wizard. |
| `/founder-os:voice-interview` | Capture how you write into `core/voice-profile.yml`. Unlocks the voice-coupled writing skills. |
| `/founder-os:brand-interview` | Capture your visual identity into `core/brand-profile.yml`. Unlocks branded outputs. |
| `/founder-os:status` | Read-only OS readiness check. Returns a weighted score and the next 3 high-leverage moves. |
| `/founder-os:ingest <source>` | File a URL, file path, or pasted text into `raw/` with provenance. Propose wiki updates you approve. |
| `/founder-os:lint` | Read-only wiki audit. Cross-references, orphans, stale content, provenance, possible contradictions. |
| `/founder-os:wiki-build` | Refresh the auto-generated wiki graph in `brain/relations.yaml`. Idempotent. |
| `/founder-os:update` | Pull the latest System Layer files. Subcommands: `check`, `rollback`. |
| `/founder-os:uninstall` | Cleanly remove Founder OS. Default mode preserves your data. `--purge` removes everything. |
| `/today` | 20-line one-screen view of today. |
| `/next` | One recommended next action across priorities, deals, and cadence. |
| `/pre-meeting` | Hard gate before any meeting. |
| `/capture-meeting` | Route a transcript or brain dump into log + clients + open commitments. |

### Templates

The setup wizard writes from `templates/`. After setup, you edit the generated files, not the templates.

### Notion package

Scaffold artifacts for users who do not run Claude Code. This path is not live until the public duplicate template ships:
- Notion duplication template (planned)
- System prompt for a Claude Project
- Quickstart page

---

## Tools and MCPs

Founder OS does not assume your stack. The OS is files and skills. Each skill declares which MCP servers it can use, and degrades gracefully when those MCPs are not available.

23 of the 27 skills work end-to-end with zero MCPs. Four skills (`email-drafter`, `meeting-prep`, `knowledge-capture`, `session-handoff`) function without MCPs but produce better output with the relevant integration connected.

The full catalog: [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

### What does NOT work without an MCP

- Calendar event in `/today` line - needs Google Calendar or Outlook MCP. Without it, the line shows `no scheduled event next 24h`.
- Pulling email context for `email-drafter` - needs Gmail or Outlook MCP. Without it, you paste the email by hand.
- Writing captured insights directly to Notion via `knowledge-capture` - needs Notion MCP. Without it, captures stay in `brain/log.md` as markdown.

Nothing in the OS hard-fails on a missing MCP. It tells you what it can't do and continues.

---

## Who this is for

You run the business alone or with one or two people. You are sharp but your day is chopped into thirty-minute pieces. You have tried productivity templates that promised the world and quietly stopped getting opened by week three.

You are not installing a template. You are installing an operating layer. It listens, routes, forgets nothing, and pushes back when you are about to ship something half-baked.

---

## The repos

Three repos. One architecture. FounderOS is production. The siblings are in development.

| Repo | Status | For | Entry point |
|---|---|---|---|
| **FounderOS** (this repo) | Production v1.3 | Owners running a business | [github.com/ARCASSystems/FounderOS](https://github.com/ARCASSystems/FounderOS) |
| **PersonalOS** | In development, ETA late May 2026 | Individuals - career changers, freelancers, side hustlers, learners, creators | [github.com/ARCASSystems/PersonalOS](https://github.com/ARCASSystems/PersonalOS) |
| **AgentOS** | In development, ETA June 2026 | Builders who want to ship a custom OS to a client or team | [github.com/ARCASSystems/AgentOS](https://github.com/ARCASSystems/AgentOS) |

All three are Claude Code plugins. All three are local-first. FounderOS and PersonalOS are migrations of AgentOS with personal data stripped out. If you want a polished operating layer right now, FounderOS is the one to use. The siblings are previews.

The three repos share one architecture - User OS (Layer 1) / Company OS (Layer 2) / Knowledge Base (Layer 3). FounderOS lives at Layer 1 today and reads from Layer 2 when you're coordinating with teammates. The full picture is in [AgentOS/docs/three-layer-architecture.md](https://github.com/ARCASSystems/AgentOS/blob/main/docs/three-layer-architecture.md).

If you want someone to build and run this for you, that is [ARCAS Systems](https://arcassystems.com).

---

## What it is not

Not a workflow engine. Not a webhook server. Not a cloud tool that stores your data on someone else's servers.

Your Notion. Your Claude. Your files on your disk if you want them there. If you want to delete it, run `/founder-os:uninstall` or just delete the folder. Nothing to unsubscribe from.

If you need crons, webhooks, offline triggers, or anything that fires while you sleep, that is a different tool (n8n, Make, whatever you use). Founder OS holds the thinking layer. You stay in charge of the rest.

---

## What makes this different

- **Stall detection built in.** The system watches for rolling items and forces keep/kill/escalate decisions. Every retro.
- **Revenue loop enforcement.** Every outreach or content action must log same-session. Catches the gap between "I'll do X" and "I did X."
- **Role as router.** COO, BD, CMO, Chief of Staff are behavioural modes, not personas. The right mode activates based on what you are actually doing.
- **Plan A defines Plan B.** This product is a derivative of an actual founder's daily use. Features graduate from personal use into the product only after surviving contact with live P&L.
- **Talk to it.** Built around dictation. Claude Code's built-in dictation is the primary input. Wispr Flow is an optional power-user upgrade. On mobile, skills work via typed input - no dictation tool required.
- **Kill criteria in the product.** Tells you when a flag has been open too long and forces a decision.

---

## Cloud Claude (web, desktop, mobile)

The Notion Starter Kit is in development. Until the public duplicate template ships, use the Claude Code path for setup. The system prompt at [`notion-package/system-prompts/founder-os-project-prompt.md`](notion-package/system-prompts/founder-os-project-prompt.md) is available for preview and testing only.

Slash commands and local file writes only run in Claude Code. Cloud Claude can read this repo's files as context but cannot run `/founder-os:setup` from a checkout.

Safe fallback prompt for Cloud Claude:

```text
Use this repo as the Founder OS system layer. Read README.md and CLAUDE.md first.
If the founder context files are missing, stop and tell me to run /founder-os:setup
or use the Notion quickstart. Do not invent identity, clients, priorities, decisions,
revenue, or commitments.
```

---

## Start here

| Want to | Run |
|---|---|
| Install via plugin | `/plugin marketplace add ARCASSystems/FounderOS` then `/plugin install founder-os@founder-os-marketplace` |
| Install via git clone | See [docs/install.md](docs/install.md) Path B |
| Set up after install | `/founder-os:setup` |
| Check today after setup | `/today` |
| Check OS health | `/founder-os:status` |
| Update System Layer later | `/founder-os:update check` |
| Cleanly remove | `/founder-os:uninstall` |
| Business inquiry, install help, speaking | `solutions@arcassystems.com` |

---

## Status

Version 1.3.0. Public push week of 2026-05-04.

v1.3 adds the wiki conventions block: a `raw/` source layer with provenance, a `[[wiki-link]]` cross-reference convention, the `/founder-os:ingest` skill (file a source, propose wiki updates), and the `/founder-os:lint` skill (read-only audit of broken links, orphans, stale content, provenance gaps). All additive. No existing skill, command, hook, or file changes behavior. See [CLAUDE.md "Wiki Conventions"](CLAUDE.md) for the spec.

Early and honest. Read [`notion-package/pages/05-current-limits.md`](notion-package/pages/05-current-limits.md) for the current limits.

Built by [Alistair Aranha](https://github.com/ARCASSystems) at [ARCAS Systems](https://arcassystems.com).
