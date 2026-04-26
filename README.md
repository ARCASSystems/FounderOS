# Founder OS

The operating layer for a solo founder. Six files run your company. Claude reads them every session.

Owned by you. Powered by Claude. Talk to it.

**Setup:** Paste the install command. Run `/founder-os:setup`. Talk to it for 15 minutes. Done.

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

Around those: 20 skills covering meeting prep, knowledge capture, decisions, email drafting, content repurposing, founder coaching, weekly review, priority triage, SOPs, unit economics, strategic analysis, brain log, session handoff, pre-send check, the voice and brand interviews that capture how you write and how your work looks, the your-voice and your-deliverable-template skills that apply that profile to every output, the business-context-loader for per-company context, and the setup wizard.

Plus four roles as behavioural modes: COO (default), BD, CMO, Chief of Staff.

---

## Three ways to install

### 1. Notion Starter Kit (fastest, no-Code path)

Duplicate a Notion page. Paste one system prompt into a Claude Project. Five minutes.

Read [`notion-package/pages/01-quickstart.md`](notion-package/pages/01-quickstart.md).

### 2. Claude app with Notion MCP

If you live in the Claude desktop or mobile app. Point the Notion connector at the duplicated workspace. Same logic.

### 3. Claude Code terminal (recommended for power users)

Local markdown files, git history, full control over hooks and slash commands.

Mac, Linux, or git-bash on Windows:

```bash
git clone --depth 1 https://github.com/ARCASSystems/FounderOS.git ~/founder-os && cd ~/founder-os
```

PowerShell on Windows:

```powershell
git clone --depth 1 https://github.com/ARCASSystems/FounderOS.git "$HOME\founder-os"; cd "$HOME\founder-os"
```

Open Claude Code in that folder, then run:

```
/founder-os:setup
```

The setup wizard asks six or seven questions and generates your full operating system locally. 15 to 20 minutes the first time.

---

## What ships in this repo

### Skills (20)

| Skill | What it does |
|---|---|
| founder-os-setup | Setup wizard. Generates identity, priorities, decisions, cadence, brain files. |
| weekly-review | Run the weekly retro. M/S/D bucket calculation, keep/kill/escalate on flags. |
| priority-triage | Force a top-3 from a long list. Names what gets cut. |
| brain-log | Route a thought to log, cross-reference, or act with same-session follow-through. |
| decision-framework | Surface trade-offs. No false simplicity. |
| session-handoff | Pack up context for the next session or a different operator. |
| meeting-prep | Pre-meeting brief plus post-meeting debrief. |
| knowledge-capture | Capture from books, podcasts, courses, conversations. |
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
| business-context-loader | Loads, scans, and progressively fills a per-company context file. Routes you to the next highest-leverage move. |

### Slash commands (5)

| Command | Purpose |
|---|---|
| `/founder-os:setup` | Run the setup wizard. |
| `/founder-os:update` | Pull the latest System Layer files. Subcommands: `check`, `rollback`. |
| `/today` | 20-line one-screen view of today. |
| `/next` | One recommended next action across priorities, deals, and cadence. |
| `/pre-meeting` | Hard gate before any meeting. |
| `/capture-meeting` | Route a transcript or brain dump into log + clients + open commitments. |

### Templates

The setup wizard writes from `templates/`. After setup, you edit the generated files, not the templates.

### Notion package

Three drop-in artifacts for users who do not run Claude Code:
- Notion duplication template (the six core files plus brain log and flags)
- System prompt for a Claude Project
- Quickstart page

---

## Who this is for

You run the business alone or with one or two people. You are sharp but your day is chopped into thirty-minute pieces. You have tried productivity templates that promised the world and quietly stopped getting opened by week three.

You are not installing a template. You are installing an operating layer. It listens, routes, forgets nothing, and pushes back when you are about to ship something half-baked.

---

## The ecosystem

Three repos. One architecture. Choose the one that matches where you are.

| Repo | For | Entry point |
|---|---|---|
| **PersonalOS** | Individuals - career changers, freelancers, side hustlers, learners, creators | [github.com/ARCASSystems/PersonalOS](https://github.com/ARCASSystems/PersonalOS) |
| **FounderOS** (this repo) | Solo founders running a business | [github.com/ARCASSystems/FounderOS](https://github.com/ARCASSystems/FounderOS) |
| **AgentOS** | Builders who want to ship a custom OS to a client or team | [github.com/ARCASSystems/AgentOS](https://github.com/ARCASSystems/AgentOS) |

All three are Claude Code plugins. All three are local-first. FounderOS and PersonalOS are migrations of AgentOS with personal data stripped out.

If you want someone to build and run this for you, that is [ARCAS Systems](https://arcassystems.com).

---

## What it is not

Not a workflow engine. Not a webhook server. Not a cloud tool that stores your data on someone else's servers.

Your Notion. Your Claude. Your files on your disk if you want them there. If you want to delete it, you delete the folder. Nothing to unsubscribe from.

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

The Notion Starter Kit is the safest path. Duplicate the Notion template, create a Claude Project, paste the system prompt from [`notion-package/system-prompts/founder-os-project-prompt.md`](notion-package/system-prompts/founder-os-project-prompt.md).

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
| Install fastest, no-Code | [Notion Quickstart](notion-package/pages/01-quickstart.md) |
| Install locally with Claude Code | `/founder-os:setup` |
| Check today after setup | `/today` |
| Update System Layer later | `/founder-os:update check` |
| Business inquiry, install help, speaking | `alistair@arcassystems.com` |

---

## Status

Version 1.1.0. Public launch week 2026-04-27.

Early and honest. Read [`notion-package/pages/05-current-limits.md`](notion-package/pages/05-current-limits.md) for the current limits.

Built by [Alistair Aranha](https://github.com/ARCASSystems) at [ARCAS Systems](https://arcassystems.com).
