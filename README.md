# Founder OS

![tests](https://github.com/ARCASSystems/FounderOS/actions/workflows/test.yml/badge.svg)

The operating layer for the person running the business. Six files run your company. Claude reads them every session.

Owned by you. Runs locally in Claude Code. Talk to it.

---

**New here? [Read the playbook first](playbook.html)** - explains the problem, the three parts, how to start, and what not to do. 15 minutes. Opens in any browser.

**[Download Founder OS](https://github.com/ARCASSystems/FounderOS/archive/refs/heads/main.zip)** - or install via one-line curl, plugin marketplace, or git clone. See [Install](#install) below.

---

## Who this is for

You run the business or run a P&L inside one. Owner, operator, agency lead, consultancy head, head of department. If the buck stops with you, this is for you.

You are sharp but your day is chopped into thirty-minute pieces. You have tried productivity templates that promised the world and quietly stopped getting opened by week three.

You are not installing a template. You are installing an operating layer. It listens, routes, forgets nothing, and pushes back when you are about to ship something half-baked.

---

## What makes this different

- **Stall detection built in.** The system watches for rolling items and forces keep/kill/escalate decisions. Every retro.
- **Revenue loop enforcement.** Every outreach or content action must log same-session. Catches the gap between "I'll do X" and "I did X."
- **Role as router.** COO, BD, CMO, Chief of Staff are behavioural modes, not personas. The right mode activates based on what you are actually doing.
- **Plan A defines Plan B.** This product is a derivative of an actual founder's daily use. Features graduate from personal use into the product only after surviving contact with live P&L.
- **Talk to it.** Built around dictation. Claude Code's built-in dictation is the primary input. Wispr Flow is an optional power-user upgrade. Claude Code is desktop-only today. There is no native mobile execution surface.
- **Decay-driven keep/kill.** Set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires. The OS does not auto-kill, you decide.

---

## What you actually get

Three layers, in plain English. Skills read and write across all of them.

- **Operating files** - priorities, clients, decisions, today, weekly. The state of the business right now.
- **Brain layer** - log, flags, patterns, parked decisions, rants, knowledge. The memory that captures what happened, what is stuck, and what is worth reusing.
- **Wiki layer** - `[[cross-references]]` between files plus a source archive (`raw/`) for articles, transcripts, and anything you want preserved.

**Four roles as behavioural modes:** COO (default), BD, CMO, Chief of Staff. Claude switches mode based on what you are actually doing.

A **SessionStart brief** runs on every Claude Code session open and surfaces stalls, stale cadence, and items past their decay date in one screen. Background plumbing the wizard sets up. You do not need to think about it. The brief, the Stop hook, and slash commands are Claude Code-only - on Cowork or Cloud Claude they do not fire. Details under [Substrate details](#substrate-details) below if curious. Surface-by-surface compatibility table in [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

**The legal layer (as-needed, not daily).** Most founders won't open this every day. But when a question lands - "can I let someone go", "what's our VAT obligation", "is this NDA enforceable", or you have a meeting with a lawyer next week and need to ask the right questions - the OS already knows your jurisdiction, holds the gazetted source documents, and surfaces compliance deadlines on its own. UAE founders get a full reference set out of the box (10 domain files covering company formation, employment, tax, visas, contracts, IP, data protection, dispute resolution, and industry permits, with 27 primary government sources tracked for freshness). Founders elsewhere run `/founder-os:legal-setup`, name their jurisdiction, and load their own gazetted sources via `/founder-os:legal-add-source <url-or-pdf>`. The skill never invents law - it quotes from sources you've loaded and tells you when a source is missing. SessionStart surfaces anything in `context/compliance.md` that's overdue or due within 30 days, so a license renewal, VAT return, or visa expiry doesn't slip past you. Details below under [Legal layer](#legal-layer).

**The capture-and-cite loop.** `/rant` qualifies a raw thought dump with one question, then routes it to a decision, draft, plan, log, or capture path. `/dream` distils captured rants into patterns, flags, parked decisions, and needs. Every new brain entry gets a stable `<channel>-YYYY-MM-DD-NNN` ID stamped at write time. The dream digest cites those IDs in one line each instead of restating content. `knowledge-capture` writes distilled takeaways from books, calls, and articles into `brain/knowledge/` with the same ID convention so proposal-writer and strategic-analysis can read them back. Optional: opt in to a tool-call observation log with `FOUNDER_OS_OBSERVATIONS=1` and `/dream` rolls each day's activity into an OBSERVED section.

---

## What it costs

One AI subscription. Everything else is free.

- **Founder OS** (this repo) - free, MIT licence
- **Claude Code** (the interface) - free to install
- **AI subscription** - Claude, OpenAI, or Google. Any plan with 100K+ context tokens. Most paid plans are $20-100/month.

Free tiers usually don't have enough context for this to work well. A paid AI subscription is the only real cost. If you already pay for Copilot, Gemini Pro, or GPT-4, try those first. The files travel with you. You are not locked in.

---

## Before you install

You need four things:

- **Claude Code** - free. Download at [claude.ai/code](https://claude.ai/code). Desktop app for Mac and Windows.
- **A paid AI subscription** - Claude Pro, Claude Max, or equivalent. Free tiers lack sufficient context.
- **Git** - version 2.x or later. Run `git --version` to check.
- **Python 3.11+** - for the runtime scripts. Run `python3 --version` to check.

That is it. No database. No server. No Notion account required.

---

## How to use it - talk to Claude

The OS routes on natural language. Say what you need ("set up my voice profile", "what's on for today?", "prep me for my call with Sarah") and the right skill fires. Slash commands are speed shortcuts for power users, not the primary surface. If you forget what's available, say "show me what you can do" (or run `/founder-os:menu`) and the OS returns 5 to 7 capabilities scored against your current state.

---

## Install

Four install paths. Simplest first. Full step-by-step for each in [docs/install.md](docs/install.md).

### One-line curl (simplest)

```bash
curl -fsSL https://raw.githubusercontent.com/ARCASSystems/FounderOS/main/install.sh | bash
```

Downloads FounderOS, copies hooks, and prints the natural-language next step. Requires bash, git, and Python 3.11+. Re-running the same command on an existing install offers an update instead.

**When to choose:** You are on macOS or Linux (or git-bash on Windows), you want one command and you are done.

### Plugin marketplace (cleanest Claude Code experience)

```
/plugin marketplace add ARCASSystems/FounderOS
/plugin install founder-os@founder-os-marketplace
```

Then say "set up Founder OS" (or run `/founder-os:setup`). If setup is not recognised, run `/reload-plugins` first.

**When to choose:** You already use Claude Code with a Pro or Max plan and want auto-updates via `/founder-os:update`.

### Manual git clone (most reliable)

```bash
git clone --depth 1 https://github.com/ARCASSystems/FounderOS.git ~/founder-os
```

Open Claude Code in the cloned folder, then say "set up Founder OS" (or run `/setup`). Commands use bare names on this path - no `/founder-os:` prefix.

**When to choose:** The plugin install fails, or you want full control of the local copy and manual `git pull` updates.

### Claude Cowork (partial - natural-language only)

Open the FounderOS folder in Cowork and attach `CLAUDE.md` as folder instructions. Hooks and slash commands do not fire in Cowork. Use it for drafting and scheduled tasks; return to Claude Code for hooks, cadence refresh, and commits.

**When to choose:** You use Cowork for day-to-day drafting and want the OS context available there alongside your Claude Code install.

---

## Setup ladder (40 min total, do in this order)

1. **Install** - pick an [install path](#install) above (5 min). Run `./scripts/install-git-hooks.sh` to activate the privacy pre-commit hook (operator-only).
2. **Say "set up Founder OS"** (or run `/founder-os:setup`) - the wizard builds your operating layer from your answers (15 min)
3. **Say "set up my voice profile"** (or run `/founder-os:voice-interview`) - so every writing skill sounds like you, not Claude (10 min)
4. **Say "set up my brand profile"** (or run `/founder-os:brand-interview`) - so every deliverable looks like you (10 min)

After that, `/founder-os:status` audits the OS anytime, `/today` gives a one-screen view of today, and `/next` recommends one action. Full first-day path in [docs/first-day.md](docs/first-day.md). Full per-command reference in [docs/commands.md](docs/commands.md). Full per-skill reference (outcome, reads, writes, voice rules, prereqs, follow-ups) in [docs/skills.md](docs/skills.md).

> **Path B users (manual git clone):** drop the `/founder-os:` prefix. Commands are bare names: `/setup`, `/voice-interview`, `/brand-interview`, `/today`, etc. The plugin namespace only activates on Path A. See [docs/install.md](docs/install.md) for the exact commands per path.

---

## What ships in this repo

### Skills (45)

Skills are grouped by when you will actually reach for them, not by category. If you are still on Day 1, you can ignore the rest.

Each row tells you the **outcome** (what you get when it finishes). Detailed reads, writes, voice rules, prereqs, and follow-ups for every skill live in [`docs/skills.md`](docs/skills.md).

#### Day 1 - use during your first session

| Skill | What you get |
|---|---|
| founder-os-setup | Your full operating layer on disk: identity, priorities, decisions, clients, daily anchor, weekly commitments, brain log, flags. 8+ files written. 15 min. |
| voice-interview | A `core/voice-profile.yml` that captures how you actually write. Every writing skill reads it. Requires you paste 2+ writing samples. 10 min. |
| brand-interview | A `core/brand-profile.yml` plus an assets folder. Every branded deliverable inherits the colors, fonts, and logo. 10 min. |
| readiness-check | A weighted readiness score plus the next 3 high-impact moves to run. Read-only. |
| business-context-loader | A loaded per-company context file plus a list of what is missing or stale and the next obvious move. Read-only. |
| brain-log | A new entry in `brain/log.md` with a stable `log-YYYY-MM-DD-NNN` ID. Three modes: log only, log with cross-reference, or log and act. May also update the referenced file. |
| today | A one-screen today brief. Same output as `/today` for surfaces where slash commands do not fire. Read-only. |

#### Week 1 - use within your first working week

| Skill | What you get |
|---|---|
| priority-triage | A top 3 list with everything else explicitly cut and the reason for each cut. Read-only. |
| weekly-review | A Must/Should/Did bucket per priority for last week, plus a keep/kill/escalate verdict on every open flag. Updates `cadence/weekly-commitments.md` and rolls forward. |
| decision-framework | A structured decision document: criteria, options, trade-offs, kill criteria. Writes the resolved decision to `context/decisions.md` with a stable ID. |
| meeting-prep | A brief covering attendees, prior interactions, talking points, and questions. Post-meeting: a debrief routed into `brain/log.md`, `context/clients.md`, and open commitments. |
| email-drafter | A draft email in your voice ready to copy-paste. Reads the inbox via Gmail or Outlook MCP if connected. Otherwise you paste the thread. Read-only. |
| linkedin-post | A LinkedIn post in your voice, anti-AI rules applied, hooks tested against the "see more" cutoff. Read-only. |
| client-update | A status update for a named client, framed in your voice with progress lifted from `context/clients.md`. Read-only. |
| your-voice | Any text rewritten in your voice using `core/voice-profile.yml`. Every writing skill calls this one. Read-only. |
| your-deliverable-template | A branded document (proposal, deck, one-pager) inheriting colors, fonts, and logo from your brand profile. Writes to `drafts/` or `exports/`. |
| pre-send-check | A pass or fail verdict across voice, source truth, anti-AI scan, and personalization. Names every issue. Nothing ships if anything fails. Read-only. |
| session-handoff | A handoff file naming what you did, what is open, and what the next operator needs to know. Writes to `drafts/handoffs/` or a named path. |
| forcing-questions | Six yes/no answers and a verdict on whether to start, kill, or postpone the initiative. Catches vague done states, phantom users, scope creep, false urgency. Read-only during the question loop; writes to priorities, log, and parked decisions after explicit confirmation. |
| blind-spot-review | A second-pass review across legal, contracts, data, timing, relationships, upside, and walkaway risk. Names risks before pre-send. Read-only. |
| ship-deliverable | One pass-or-fail composite across template fit, anti-AI scan, blind-spot evidence, and pre-send-check. Final gate. Read-only. |

#### Month 1+ - use as your pipeline and content rhythm grows

| Skill | What you get |
|---|---|
| proposal-writer | A full proposal document (scope, deliverables, terms, pricing) inheriting voice and brand. Writes a branded file to `drafts/`. |
| sop-writer | A structured SOP document someone else could follow, captured from how you describe the process verbally. Writes to `drafts/sops/` or a named path. |
| content-repurposer | One source piece reformatted across LinkedIn, Twitter, newsletter, and internal doc, all in your voice. Read-only. |
| knowledge-capture | A new `brain/knowledge/<topic>.md` note with a stable `know-YYYY-MM-DD-NNN` ID, plus a row in the knowledge index. Other skills cite it directly instead of restating content. |
| founder-coaching | A diagnostic across the four operating zones (peacetime, pre-war, wartime, recovery), a role/identity map, and a verdict on what to shed. Read-only. |
| unit-economics | The math on a deal, hire, pricing change, or new business line: CAC, LTV, gross margin, breakeven, payback period. Stores the model file under `drafts/`. |
| strategic-analysis | A market scan, competitor map, or opportunity assessment grounded in your `brain/knowledge/` notes. Read-only. |
| ingest | A new file in `raw/<source>.md` with provenance, plus proposed wiki updates you approve before they land. |
| lint | A list of broken `[[wikilinks]]`, orphan pages, stale entries past their decay date, provenance gaps, and possible contradictions. Read-only. |
| wiki-build | A refreshed `brain/relations.yaml` graph extracted from every `[[wikilink]]` in your OS. Idempotent. |
| approval-gates | An auto-run / ask-first / refuse verdict on a proposed action against `rules/approval-gates.md`. Read-only. |
| handoff-protocol | A structured handoff artifact for moving work to another person, role, or future session. Writes a named handoff file. |
| context-persistence | A source-cited answer to "what do we already know about X" before you re-explain. Read-only. |
| data-security | A data classification (Public, Internal, Confidential, Restricted) plus a safe-path verdict before any paste, upload, or external tool use. Read-only. |
| bottleneck-diagnostic | A founder-dependency score across decisions, clients, process, revenue, and growth capacity, plus the highest-impact shed. Read-only. |
| query | The top 3 to 5 OS nodes that match your question, each with a stable ID and the path that reached it. Three modes: index (default), timeline, full. Read-only. |
| brain-snapshot | A small deterministic markdown payload at `brain/.snapshot.md` (open flags, this week's must-do, recent decisions, voice and brand fields, staleness). Output-producing skills read it at task time so they reflect current state instead of starting cold. Writes one file. |
| brain-pass | A synthesised answer across the brain layer with stable-ID citations: Answer, Evidence, Confidence, Gaps. The model IS the retrieval engine. No embeddings, no API call. Read-only. |
| audit | One composite health report across readiness, wiki state, brain staleness, voice completeness, and quarantine. Read-only. |
| legal-compliance | Jurisdiction-aware legal reference lookup and compliance guidance from loaded sources. Read-only unless adding sources. |
| queue | What is moving. Read, add, start, done, and park operations on `cadence/queue.md`. ACTIVE is hard-capped at 3 - starting a fourth item triggers a keep/park/kill decision. Surfaced in the SessionStart brief. |
| verify | A structured health check across 8 substrate checks: plugin surface, hooks, scripts, MCPs, free-tier floor, wiki, cadence freshness, auto-memory. Each check marked PASS / WARN / FAIL with a one-line reason. Never auto-fixes. Read-only. |
| menu | A tailored list of 5 to 7 capabilities scored against your current state, surfaced when you do not know what to ask for. Reads `brain/.snapshot.md` and current context. Read-only. |
| observation-rollup | Compacts raw JSONL observation files older than 7 days into weekly summaries. Runs automatically via the SessionStart hook. Writes to `brain/observations/_rollups/`. |

### Slash commands (27)

Each row tells you the **outcome** (what you see when it finishes), the natural-language phrase that triggers the same skill, and whether it **writes** anything. Detailed behaviour, sample output, args, and follow-ups live in [`docs/commands.md`](docs/commands.md).

| Command | Or say… | What you get |
|---|---|---|
| `/founder-os:menu` | "show me what you can do" | A tailored list of 5 to 7 capabilities scored against your current state. The single entry point if you forget what's available. Read-only. |
| `/founder-os:setup` | "set up Founder OS" | A guided interview that ends with your full operating layer on disk: identity, priorities, decisions, clients, daily anchor, weekly commitments, brain log, flags. Writes 8+ files under `core/`, `context/`, `cadence/`, `brain/`. 15 min. |
| `/founder-os:voice-interview` | "set up my voice profile" | A `core/voice-profile.yml` that captures how you actually write. Every voice-coupled writing skill (LinkedIn, email, proposal, client update) reads it on every output. 10 min. |
| `/founder-os:brand-interview` | "set up my brand profile" | A `core/brand-profile.yml` plus an assets folder. Every branded deliverable (proposal, deck, one-pager) inherits these colors, fonts, and logo. 10 min. |
| `/founder-os:status` | "check my OS readiness" | A weighted readiness score plus the next 3 high-impact moves to run right now. Read-only. |
| `/founder-os:ingest <source>` | "ingest this" / "save this source" | A new file in `raw/<source>.md` with provenance frontmatter, plus proposed wiki updates you approve before they land. Writes `raw/`, optionally updates `brain/relations.yaml`. |
| `/founder-os:lint` | tool invocation | A list of broken `[[wikilinks]]`, orphan files, stale entries past their decay date, provenance gaps, and possible contradictions. Read-only. |
| `/founder-os:wiki-build` | tool invocation | A refreshed `brain/relations.yaml` graph extracted from every `[[wikilink]]` in your OS. Idempotent. Writes `brain/relations.yaml`. |
| `/founder-os:query <question>` | "find the file about [topic]" | The top 3 to 5 OS nodes that match your question, each with a stable ID and the path that reached it. `--mode timeline --anchor <slug>` returns entries within 7 days of an anchor. `--mode full --ids <a,b,c>` returns full bodies. Read-only. |
| `/founder-os:brain-pass "<question>"` | "what do I know about [topic]" | A synthesised answer with stable-ID citations: Answer, Evidence, Confidence, Gaps. Use when a question spans multiple brain files. Read-only. |
| `/founder-os:audit` | "audit the OS" | One composite health report covering readiness, wiki integrity, brain staleness, voice completeness, and quarantine state. Read-only. |
| `/founder-os:forcing-questions <initiative>` | "I'm thinking of starting [X]" | Six yes/no answers plus a scope-creep verdict on whether to start, kill, or postpone the initiative. Read-only during the question loop; writes to priorities, log, and parked decisions after explicit confirmation. |
| `/founder-os:ship-deliverable <path>` | "is this ready to send" | A pass or fail verdict across template fit, anti-AI scan, blind-spot review, and pre-send checks. Names every issue. Nothing ships if anything fails. Read-only. |
| `/founder-os:legal-setup` | "set up my legal context" | A jurisdiction setup flow for the legal reference layer. Writes `jurisdiction:` and `context/compliance.md` when approved. |
| `/founder-os:legal-add-source <source>` | "add this legal source" | Registers a URL or PDF against your jurisdiction's legal source set. Writes `sources.yml` and optional domain stubs. |
| `/founder-os:legal-update` | "refresh legal sources" | Checks source freshness for the loaded jurisdiction and updates review dates after confirmation. |
| `/founder-os:update` | "update Founder OS" | A diff of System Layer files (skills, templates, commands, hooks) refreshed from the latest release. Your personal data (`core/`, `context/`, `cadence/`, `brain/`) is never touched. Subcommands: `check`, `rollback`. |
| `/founder-os:uninstall` | "uninstall Founder OS" | A confirmation list of every file that will be removed, plus the actual cleanup. Default preserves your data. `--purge` removes everything. |
| `/founder-os:rant` | "I want to rant" / "let me dump something" | One short qualification, then a route to a decision, draft, plan, log, or raw capture in `brain/rants/`. |
| `/founder-os:dream` | "process my rants" | A 5-line digest in `brain/log.md` plus stable-ID entries in `brain/patterns.md`, `brain/flags.md`, `brain/decisions-parked.md`, `brain/needs-input.md` as warranted. Each rant marked processed. Writes 5+ files. |
| `/today` | "what's on for today?" | A 20-line one-screen view: today's anchor, top open decisions, active flags, last 3 log entries, next calendar event. Read-only. |
| `/next` | "what should I focus on next?" | One recommended next action across priorities, deals, and cadence. Not a list, one action. Read-only. |
| `/pre-meeting <subject>` | "prep me for my call with [name]" | Pass or fail on the pre-meeting gate (capture artifact present, ask defined). Logs an intent entry to `brain/log.md` on pass. |
| `/capture-meeting <subject>` | "capture this" / "log this" | A routed summary: meeting log entry in `brain/log.md`, updated client status in `context/clients.md`, and any new open commitments. Writes 2 to 3 files. |
| `/founder-os:queue` | "what's on my plate" / "add to queue: <thing>" | Shows ACTIVE items, adds to BACKLOG, moves items between states. ACTIVE is capped at 3. Starting a fourth triggers a keep/park/kill decision. |
| `/founder-os:verify` | "verify the OS" / "health check" | A structured health check across 8 substrate checks, each PASS / WARN / FAIL. Never auto-fixes. Read-only. |
| `/founder-os:observation-rollup` | tool invocation | Compacts raw JSONL observation files older than 7 days into weekly summaries under `brain/observations/_rollups/`. Triggered automatically by the SessionStart hook when FOUNDER_OS_OBSERVATIONS=1. |

### Templates

The setup wizard writes from `templates/`. After setup, you edit the generated files, not the templates.

### Notion package

Scaffold artifacts for users who do not run Claude Code. This path is not live until the public duplicate template ships:
- Notion duplication template (not yet shipped; community forks welcome)
- System prompt for a Claude Project
- Quickstart page

---

## Legal layer

Not a daily skill. A safety layer for the moments you do need it: a hire or a fire, a VAT or corporate tax filing, an NDA you've been asked to sign, a license renewal coming up, a meeting with a lawyer or accountant where you want to walk in informed instead of guessing.

The skill is jurisdiction-aware. It reads a `jurisdiction:` field from `core/identity.md` and loads only that jurisdiction's reference folder. UAE founders get a complete reference set out of the box - 10 domain files (company formation, employment, tax/VAT, visas, contracts, IP, data protection, dispute resolution, industry permits) plus 27 tracked primary government sources (mohre.gov.ae, tax.gov.ae, icp.gov.ae, det.gov.ae, difc.ae, adgm.com, etc.) plus document templates for NDAs, employment offers, privacy policies. Verified 2026-04-25.

Founders outside the UAE run `/founder-os:legal-setup` to:
1. Name their jurisdiction (e.g., `US-Delaware-LLC`, `UK-Ltd`, `IN-Karnataka-Pvt-Ltd`)
2. Get a scaffold folder created from the `_template/` shape
3. Capture their fiscal year end, business structure, and active filings/renewals into `context/compliance.md`

Then load three priority sources via `/founder-os:legal-add-source <url-or-pdf>`:
- Your country's tax authority (IRS, HMRC, IRAS, ATO, etc.)
- Your country's business / companies law
- Your country's labour / employment law

Until at least those three load, the skill **refuses to answer** legal questions for your jurisdiction. It will not invent law. The UAE references give it the *shape* of how a complete reference set looks; your sources give it the *content* for your country.

**What you actually get when the skill is loaded:**

- Plain-language answers grounded in your loaded sources, with citation
- Escalation level on every response: confident / confirm with a lawyer / lawyer required
- Source freshness check: the skill flags the answer if a source hasn't been verified in 6+ months
- A list of right-question prompts before any meeting with a legal consultant - so you go in with the actual questions instead of the lawyer asking what you're asking about

**SessionStart surfaces deadlines automatically.** Anything in `context/compliance.md` overdue or due within 30 days appears at the top of every session. License renewal due in 14 days. VAT return due in 21 days. Visa expiring in 28 days. You don't need to remember.

**Maintenance.** Run `/founder-os:legal-update` quarterly. The command walks each loaded source, web-fetches the canonical URL, captures any material change (a new ministerial decision, an updated threshold, a fee schedule revision), and updates `last_checked_on:`. Anything older than 6 months gets surfaced first.

The skill is opt-in - the rest of Founder OS works without it. You activate it by running `/founder-os:legal-setup` when you want it.

---

## Tools and MCPs

Founder OS does not assume your stack. The OS is files and skills. Each skill declares which MCP servers it can use, and degrades gracefully when those MCPs are not available.

Most of the 45 skills work end-to-end with zero MCPs. A few skills, including `email-drafter`, `meeting-prep`, `knowledge-capture`, and `session-handoff`, function without MCPs but produce better output with the relevant integration connected.

The full catalog: [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

### What does NOT work without an MCP

- Calendar event in `/today` line - needs Google Calendar or Outlook MCP. Without it, the line shows `no scheduled event next 24h`.
- Pulling email context for `email-drafter` - needs Gmail or Outlook MCP. Without it, you paste the email by hand.
- Writing captured insights directly to Notion via `knowledge-capture` - needs Notion MCP. Without it, captures stay in `brain/log.md` as markdown.

Nothing in the OS hard-fails on a missing MCP. It tells you what it can't do and continues.

---

## Who this is NOT for

You want a no-code app with a UI. This is files plus skills, not an interface. You operate it through Claude Code.

You need shared state across a team. Founder OS is single-user. The Company OS layer (not in scope; community forks may extend) is what handles team coordination.

You want push notifications, automated triggers, or anything that fires while you sleep. Founder OS is the thinking layer. n8n, Make, Zapier, or your own scripts handle offline triggers.

You want a tool you install and forget. This is an operating layer that needs you to engage daily and review weekly. If you are not going to do that, this will sit unused like every other system.

---

## What it is not

Not a workflow engine. Not a webhook server. Not a cloud tool that stores your data on someone else's servers.

Your Notion. Your Claude. Your files on your disk if you want them there. If you want to delete it, run `/founder-os:uninstall` or just delete the folder. Nothing to unsubscribe from.

If you need crons, webhooks, offline triggers, or anything that fires while you sleep, that is a different tool (n8n, Make, whatever you use). Founder OS holds the thinking layer. You stay in charge of the rest.

---

## Substrate details

Background plumbing the wizard sets up. You do not need to read this to use the system. The wizard handles all of it. Here for the curious.

- **Decay-aware brain layer.** Set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires.
- **Stable entry IDs.** Every new brain entry (log, pattern, flag, parked, need, know) is stamped with a `<channel>-YYYY-MM-DD-NNN` ID at write time. Skills cite IDs in summaries instead of restating content.
- **Token-aware progressive query.** `scripts/query.py` and `/founder-os:query` operate in three modes: `index` for top hits, `timeline` for entries within a 7-day window of an anchor file or ID, `full` for the body of specific IDs. Pure markdown plus stdlib, no vector DB.
- **Opt-in observation log.** Set `FOUNDER_OS_OBSERVATIONS=1` to enable a `PostToolUse` hook that appends one line per tool call to `brain/observations/<date>.jsonl`. `/dream` rolls each day's activity into an OBSERVED section. Off by default.
- **`system/quarantine.md`** is a catch-net so failing hooks and scheduled tasks stop being silent.
- **Approval gate matrix** at `rules/approval-gates.md` tells the OS what to auto-run, what to ask about, and what to refuse outright.
- **`brain/relations.yaml`** is a hand-curated graph of edges between files, plus auto-extracted `[[wikilinks]]` refreshed by `/founder-os:wiki-build`.
- **Auto-memory layer.** Claude Code reads `~/.claude/projects/<slug>/memory/MEMORY.md` automatically at session start. The wizard seeds it so behavioral guards persist across sessions.

Full convention spec in `rules/entry-conventions.md` (generated by setup).

---

## Cloud Claude (web, desktop, mobile)

The Notion Starter Kit was scoped but is not yet shipped; community forks welcome. The system prompt at [`notion-package/system-prompts/founder-os-project-prompt.md`](notion-package/system-prompts/founder-os-project-prompt.md) is available for preview and testing only. Use the Claude Code path for the full setup experience.

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
| Set up after install | `/founder-os:setup` (Path A) or `/setup` (Path B) |
| Check today after setup | `/today` |
| Verify substrate is healthy | Say "verify the OS" (or run `/founder-os:verify`) |
| Check OS health | `/founder-os:status` |
| Update System Layer later | `/founder-os:update check` |
| Cleanly remove | `/founder-os:uninstall` |
| Business inquiry, install help, speaking | `solutions@arcassystems.com` |

---

## Status

Version 1.24.0. Public release. 45 skills, 27 commands, 354 tests.

v1.24 adds Python preflight gates so writing and reasoning skills fail visibly when their data is not set up, rather than producing generic output silently. Full release history in [CHANGELOG.md](CHANGELOG.md).

---

## Release cadence and forking

FounderOS ships in deliberate increments. Each release closes a specific gap that the previous one made visible. v1.21 added the visible queue and health check. v1.22 added the privacy tag and observation rollup. v1.23 added the natural-language capture path. v1.24 added Python preflight gates so writing and reasoning skills fail visibly when their data is not set up, rather than producing generic output silently. New releases land when there is a real gap worth closing, not on a calendar.

Community forks are encouraged. If you build something on top of FounderOS, open a discussion thread linking your fork. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for what we accept and [`docs/forking.md`](docs/forking.md) for extension points.

## Contributing and security

- Bugs and small fixes: open an issue or PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for what we accept and what stays in the upstream private repo.
- Security: report vulnerabilities to `solutions@arcassystems.com`. See [`SECURITY.md`](SECURITY.md) for scope and response times.

## License

MIT. Copyright (c) 2026 ARCAS Systems. See [LICENSE](LICENSE).

---

People first. Systems second. AI where it earns the right.

Built by [ARCAS Systems](https://arcassystems.com).
