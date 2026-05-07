# Founder OS

The operating layer for the person running the business. Six files run your company. Claude reads them every session.

Owned by you. Runs locally in Claude Code. Talk to it.

**Setup ladder (45 min total, do in this order):**

1. **Install** - pick an [install path](#install) below (5 min)
2. **`/founder-os:setup`** - the wizard builds your operating layer from your answers (15 min)
3. **`/founder-os:voice-interview`** - so every writing skill sounds like you, not Claude (15 min)
4. **`/founder-os:brand-interview`** - so every deliverable looks like you (10 min)

After that, `/founder-os:status` audits the OS anytime, `/today` gives a one-screen view of today, and `/next` recommends one action. Full first-day path in [docs/first-day.md](docs/first-day.md).

> **Path B users (manual git clone):** drop the `/founder-os:` prefix. Commands are bare names: `/setup`, `/voice-interview`, `/brand-interview`, `/today`, etc. The plugin namespace only activates on Path A. See [docs/install.md](docs/install.md) for the exact commands per path.

---

## What you actually get

Three layers, in plain English. Skills read and write across all of them.

- **Operating files** - priorities, clients, decisions, today, weekly. The state of the business right now.
- **Brain layer** - log, flags, patterns, parked decisions, rants, knowledge. The memory that captures what happened, what is stuck, and what is worth reusing.
- **Wiki layer** - `[[cross-references]]` between files plus a source archive (`raw/`) for articles, transcripts, and anything you want preserved.

Areas for searching across the 37 skills:

- **Daily ops:** weekly-review, priority-triage, brain-log, decision-framework, session-handoff, meeting-prep, knowledge-capture, founder-coaching, unit-economics, strategic-analysis, pre-send-check, sop-writer, forcing-questions, blind-spot-review, ship-deliverable
- **Voice and brand:** voice-interview, brand-interview, your-voice, your-deliverable-template
- **Voice-coupled writers:** linkedin-post, client-update, proposal-writer, email-drafter, content-repurposer
- **Setup and audit:** founder-os-setup, readiness-check, business-context-loader, query, audit
- **Wiki and safety layer:** ingest, lint, wiki-build, approval-gates, handoff-protocol, context-persistence, data-security, bottleneck-diagnostic

**Four roles as behavioural modes:** COO (default), BD, CMO, Chief of Staff. Claude switches mode based on what you are actually doing.

A **SessionStart brief** runs on every session open and surfaces stalls, stale cadence, and items past their decay date in one screen. Background plumbing the wizard sets up; you do not need to think about it. Details under [Substrate details](#substrate-details) below if curious.

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

### Skills (37)

Skills are grouped by when you will actually reach for them, not by category. If you are still on Day 1, you can ignore the rest.

#### Day 1 - use during your first session

| Skill | What happens when you run it |
|---|---|
| founder-os-setup | Asks 6 to 7 structured questions about your business, role, priorities, and tools. Writes your full operating system to local disk. 15 min. |
| voice-interview | 20 structured questions. You paste at least 2 writing samples. Generates a voice profile every writing skill reads on every output. |
| brand-interview | Structured questions on colors, fonts, logo, document layout. Generates a brand profile every visual deliverable inherits. |
| readiness-check | Scans your OS for stale priorities, missing decisions, empty cadence, broken voice profile. Returns a weighted score and the next 3 high-impact moves. |
| business-context-loader | Loads the per-company context file. Surfaces what is missing or stale. Routes to the next obvious move. |
| brain-log | Captures a thought. Routes to `brain/log.md` in one of three modes: log only, log with a cross-reference to an existing file, or log and act on it now. |

#### Week 1 - use within your first working week

| Skill | What happens when you run it |
|---|---|
| priority-triage | Takes a long list of priorities. Forces a top 3. Explicitly names what gets cut and why. |
| weekly-review | Walks last week. Forces a Must/Should/Did bucket per priority. Surfaces every open flag for keep/kill/escalate. |
| decision-framework | Walks you through a structured decision: criteria, options, trade-offs, kill criteria. Writes the resolved decision to `context/decisions.md`. |
| meeting-prep | Builds a brief from meeting context, attendees, and your prior interactions with them. Captures the debrief afterward into the right files. |
| email-drafter | Drafts emails in your voice. Reads the inbox via Gmail or Outlook MCP if connected. Otherwise you paste the thread. |
| linkedin-post | Writes a LinkedIn post in your voice. Pulls from your voice profile and applies anti-AI rules. |
| client-update | Writes a status update for a client. Pulls progress from `context/clients.md` and frames it in your voice. |
| your-voice | Reads `core/voice-profile.yml` and writes any text in your voice. Every other writing skill calls this one. |
| your-deliverable-template | Produces branded documents using your visual brand profile. |
| pre-send-check | Hard gate before any deliverable leaves your machine. Checks voice, source truth, anti-AI scan, and personalization. |
| session-handoff | Packs up what you did, what is open, what the next operator needs to know. Writes a handoff file. |
| forcing-questions | Runs six fixed questions before a new initiative starts. Catches vague done states, phantom users, scope creep, and false urgency. |
| blind-spot-review | Runs a second-pass review across legal, contracts, data, timing, relationships, upside, and walkaway risk before pre-send. |
| ship-deliverable | Runs template fit, anti-AI scan, blind-spot evidence, and pre-send-check in one read-only final gate. |

#### Month 1+ - use as your pipeline and content rhythm grows

| Skill | What happens when you run it |
|---|---|
| proposal-writer | Writes a full proposal: scope, deliverables, terms, pricing. Inherits voice and visual brand. |
| sop-writer | Captures a process you describe verbally. Writes a structured SOP someone else could follow. |
| content-repurposer | Takes one source piece. Repurposes it across LinkedIn, Twitter, newsletter, internal doc, all in your voice. |
| knowledge-capture | Captures takeaways from a book, podcast, article, or conversation into `brain/knowledge/` so future skills can read them back. |
| founder-coaching | Coaching loop when you are stuck. References a bias toolkit and a zone framework to diagnose what is actually going on. |
| unit-economics | Runs the math on a deal, hire, pricing change, or new business line. CAC, LTV, gross margin, breakeven. Stores the model file. |
| strategic-analysis | Runs a market scan, competitor map, or opportunity assessment. Reads relevant `brain/knowledge/` notes before writing. |
| ingest | Files a URL, file path, or pasted text into `raw/` with provenance. Then proposes wiki updates you approve before they land. |
| lint | Walks the OS for broken `[[wikilinks]]`, orphan pages, stale time-sensitive content, provenance gaps, and contradictions. |
| wiki-build | Extracts every `[[wikilink]]` across the OS and writes them to a machine-readable graph at `brain/relations.yaml`. |
| approval-gates | Reads `rules/approval-gates.md` and decides whether an action is auto-runnable, ask-first, or refused. |
| handoff-protocol | Creates a structured handoff artifact when work moves to another person, role, or future session. |
| context-persistence | Searches the OS before asking the founder to repeat context. Cites source paths or names what is missing. |
| data-security | Classifies data before paste, upload, or external tool use. Blocks unsafe data movement and names the safe path. |
| bottleneck-diagnostic | Scores founder dependency across decisions, clients, process, revenue, and growth capacity. |
| query | Traverses `brain/relations.yaml` plus operating files and returns the 3 to 5 most relevant nodes for a question. |
| audit | Runs readiness, lint, wiki state, brain staleness, and voice completeness as one OS health report. |

### Slash commands (19)

| Command | Purpose |
|---|---|
| `/founder-os:setup` | Run the setup wizard. |
| `/founder-os:voice-interview` | Capture how you write into `core/voice-profile.yml`. Required for the voice-coupled writing skills to sound like you. |
| `/founder-os:brand-interview` | Capture your visual identity into `core/brand-profile.yml`. Required for branded deliverables to look like you. |
| `/founder-os:status` | Read-only OS readiness check. Returns a weighted score and the next 3 high-impact moves. |
| `/founder-os:ingest <source>` | File a URL, file path, or pasted text into `raw/` with provenance. Propose wiki updates you approve. |
| `/founder-os:lint` | Read-only wiki audit. Cross-references, orphans, stale content, provenance, possible contradictions. |
| `/founder-os:wiki-build` | Refresh the auto-generated wiki graph in `brain/relations.yaml`. Idempotent. |
| `/founder-os:query <question>` | Search the OS graph and return the top 3 to 5 related nodes. |
| `/founder-os:audit` | Composite OS health report across readiness, lint, wiki, brain, and voice. |
| `/founder-os:forcing-questions <initiative>` | Run the six-question gate before starting a new initiative. |
| `/founder-os:ship-deliverable <path>` | Run the final read-only deliverable ship gate. |
| `/founder-os:update` | Pull the latest System Layer files. Subcommands: `check`, `rollback`. |
| `/founder-os:uninstall` | Cleanly remove Founder OS. Default mode preserves your data. `--purge` removes everything. |
| `/founder-os:rant` | Capture a raw thought dump into `brain/rants/`. |
| `/founder-os:dream` | Process unprocessed rants into patterns, flags, parked decisions, needs-input, and client signals. |
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

Most of the 37 skills work end-to-end with zero MCPs. A few skills, including `email-drafter`, `meeting-prep`, `knowledge-capture`, and `session-handoff`, function without MCPs but produce better output with the relevant integration connected.

The full catalog: [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

### What does NOT work without an MCP

- Calendar event in `/today` line - needs Google Calendar or Outlook MCP. Without it, the line shows `no scheduled event next 24h`.
- Pulling email context for `email-drafter` - needs Gmail or Outlook MCP. Without it, you paste the email by hand.
- Writing captured insights directly to Notion via `knowledge-capture` - needs Notion MCP. Without it, captures stay in `brain/log.md` as markdown.

Nothing in the OS hard-fails on a missing MCP. It tells you what it can't do and continues.

---

## Substrate details

Background plumbing the wizard sets up. You do not need to read this to use the system; the wizard handles all of it. Here for the curious.

- **Decay-aware brain layer.** Set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires.
- **`system/quarantine.md`** is a catch-net so failing hooks and scheduled tasks stop being silent.
- **Approval gate matrix** at `rules/approval-gates.md` tells the OS what to auto-run, what to ask about, and what to refuse outright.
- **`brain/relations.yaml`** is a hand-curated graph of edges between files, plus auto-extracted `[[wikilinks]]` refreshed by `/founder-os:wiki-build`.
- **Auto-memory layer.** Claude Code reads `~/.claude/projects/<slug>/memory/MEMORY.md` automatically at session start. The wizard seeds it so behavioral guards persist across sessions.

Full convention spec in `rules/entry-conventions.md` (generated by setup).

---

## Who this is for

You run the business or run a P&L inside one. Owner, operator, agency lead, consultancy head, head of department. If the buck stops with you, this is for you.

You are sharp but your day is chopped into thirty-minute pieces. You have tried productivity templates that promised the world and quietly stopped getting opened by week three.

You are not installing a template. You are installing an operating layer. It listens, routes, forgets nothing, and pushes back when you are about to ship something half-baked.

---

## Who this is NOT for

You want a no-code app with a UI. This is files plus skills, not an interface. You operate it through Claude Code.

You need shared state across a team. Founder OS is single-user. The Company OS layer (planned, not shipped) is what handles team coordination.

You want push notifications, automated triggers, or anything that fires while you sleep. Founder OS is the thinking layer. n8n, Make, Zapier, or your own scripts handle offline triggers.

You want a tool you install and forget. This is an operating layer that needs you to engage daily and review weekly. If you are not going to do that, this will sit unused like every other system.

---

## The repos

Three repos. One architecture. FounderOS is production. The siblings are in development.

| Repo | Status | For | Entry point |
|---|---|---|---|
| **FounderOS** (this repo) | Production v1.8.0 | Owners and operators running a business | [github.com/ARCASSystems/FounderOS](https://github.com/ARCASSystems/FounderOS) |
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

Version 1.8.0. Public push week of 2026-05-07.

v1.8.0 is the query test coverage release. It adds a stdlib `unittest` suite for `scripts/query.py` with a synthetic corpus covering index, timeline, full, bare invocation, and guard paths. v1.7.0 remains the latest user-facing feature release: stable entry IDs, progressive query modes, and opt-in observation logging.

Full release history in [`CHANGELOG.md`](CHANGELOG.md). Current limits in [`notion-package/pages/05-current-limits.md`](notion-package/pages/05-current-limits.md).

---

## Contributing and security

- Bugs and small fixes: open an issue or PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for what we accept and what stays in the upstream private repo.
- Security: report vulnerabilities to `solutions@arcassystems.com`. See [`SECURITY.md`](SECURITY.md) for scope and response times.

## License

MIT. Copyright (c) 2026 ARCAS Systems. See [`LICENSE`](LICENSE).

---

Built by [Alistair Aranha](https://github.com/ARCASSystems) at [ARCAS Systems](https://arcassystems.com).
