# Founder OS

![tests](https://github.com/ARCASSystems/FounderOS/actions/workflows/test.yml/badge.svg)

The operating layer for the person running the business. Six files run your company. Claude reads them every session.

Owned by you. Runs locally in Claude Code. Talk to it.

---

**New here? [Read the Founder OS Playbook first](founder-os-playbook.html)** - explains the problem, the three parts, how to start, and what not to do. 15 minutes. Opens in any browser.

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

**The legal layer (as-needed, not daily).** A safety layer for hires, fires, NDAs, VAT, license renewals, and walking into a lawyer's office prepared. UAE founders get a full reference set out of the box. Founders elsewhere scaffold their jurisdiction and load their own sources. The skill never invents law and surfaces overdue compliance deadlines from `context/compliance.md` on every session. Details under [Legal layer](#legal-layer) below.

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

Grouped by when you reach for them, not by category. Three tiers: 7 for Day 1, 13 for Week 1, 25 for Month 1+ and beyond. Each row in [`docs/skills.md`](docs/skills.md) names the outcome, reads, writes, voice rules, prereqs, and follow-ups.

### Slash commands (27)

Every command has a natural-language equivalent - slash commands are speed shortcuts for power users, not the primary surface. Full reference with outcomes, args, and follow-ups in [`docs/commands.md`](docs/commands.md).

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

Founder OS does not assume your stack. Most of the 45 skills work end-to-end with zero MCPs. A few (`email-drafter`, `meeting-prep`, `knowledge-capture`, `session-handoff`) produce better output with the relevant integration connected. Without a calendar MCP, `/today` shows `no scheduled event next 24h`. Without an email MCP, you paste the thread by hand. Without a Notion MCP, captures stay in `brain/log.md` as markdown. Nothing hard-fails on a missing MCP. Full catalog in [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

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

Already installed? Say "what's on for today?" (`/today`) or "verify the OS" (`/founder-os:verify`). Need to install? See [Install](#install) above. Business inquiry, install help, speaking: `solutions@arcassystems.com`.

---

## Status

Version 1.24.0. Public release. 45 skills, 27 commands, 355 tests.

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
