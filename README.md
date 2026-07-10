# Founder OS

![Doc and Install Parity](https://github.com/ARCASSystems/FounderOS/actions/workflows/doc-parity.yml/badge.svg) ![guardian](https://github.com/ARCASSystems/FounderOS/actions/workflows/guardian.yml/badge.svg) ![LinkedIn Pack Acceptance](https://github.com/ARCASSystems/FounderOS/actions/workflows/linkedin-pack.yml/badge.svg)

The operating layer for the person running the business. Six files run your company. Claude works from them every session.

Owned by you. Runs locally in Claude Code. Talk to it.

---

**New here? [Read the Founder OS Playbook first](https://arcassystems.com/playbook)** - a visual walkthrough with screenshots: the problem, the three parts, how to start, and what not to do. Opens framed in any browser, about 15 minutes. It lives on the web so it never drifts out of date; there is no copy shipped in this repo.

**[Download Founder OS](https://github.com/ARCASSystems/FounderOS/archive/refs/heads/main.zip)** - unzip it, open the folder in Claude Code, say "set up Founder OS". No git, no terminal, no curl. Or install via plugin marketplace, one-line curl, or git clone. See [Install](#install) below.

---

**What it is. What it is not.** Your personal brain. Your files, queryable by you. Not team-shared. Not always-on.

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
- **Talk to it, from anywhere.** Built around dictation. Claude Code's built-in dictation is the primary input, and any voice-to-text tool you already use works just as well. Claude Code runs locally as a CLI and through the cloud app (claude.ai/code), so you can start and drive a full session from your phone too. A cloud session runs in a remote sandbox on a branch rather than on your local disk, so the local-first path stays your machine while the cloud path is there when you are away from it.
- **Decay-driven keep/kill.** Set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires. The OS does not auto-kill, you decide.
- **Invisible version control.** Full history and undo, no git command ever typed. Say "save my work", "what changed", or "undo to before this morning" and the OS wraps git for you. Local by default; nothing pushes anywhere unless you ask. Undo is fail-safe: it saves your current work first and can never lose it. Git itself is optional at install: before you turn it on, session snapshots cover you - every file the OS edits is snapshotted before the write and restorable per file up to 2 MB, a rolling net across the last 12 sessions (`/changes` lists every change and one command restores any that were snapshotted; files over 2 MB or written straight to disk by a shell command are listed but not snapshot-restorable). Full history begins the moment you say yes: the OS installs and wires git itself, your data included, and from that save onward every version is permanent - nothing for you to type.

---

## What you actually get

Four layers, the same four the Founder OS Playbook draws on a napkin. Each does one job. Remove any one and the whole thing breaks.

- **The Brain** - memory and judgment, all plain markdown you own. The six operating files (priorities, clients, decisions, today, the week) hold the state of the business right now. The brain layer (log, flags, patterns, parked decisions, knowledge) holds what happened, what is stuck, and what is worth reusing. A wiki layer adds `[[cross-references]]` between files plus a source archive (`raw/`) for articles and transcripts.
- **The Skills** - the abilities the brain has: draft a follow-up, prep a meeting, write a proposal, run the weekly retro. They read and write across the Brain, so the output lands like you, not like a chat window.
- **The Hands** - the tools the skills reach for: calendar, inbox, notes, transcriber, voice capture. Wired through optional MCPs; nothing hard-fails when one is missing.
- **The Heartbeat** - the rhythm that keeps it current: a daily anchor at the start of the day, a weekly retro at the end of the week, and a SessionStart brief that surfaces stalls and stale cadence.

**Six role modes.** Four switch automatically based on what you are doing: COO (default), BD, CMO, Chief of Staff. Two more are there when you need them and you invoke explicitly: CSO for the portfolio view across everything you run, CTO for your tool stack and automations. To change lens yourself, just say "switch to CMO" (or any role).

A **SessionStart brief** runs on every Claude Code session open and surfaces stalls, stale cadence, and items past their decay date in one screen. Background plumbing the wizard sets up. You do not need to think about it. The brief, the Stop hook, and slash commands are Claude Code-only - on Cowork or Cloud Claude they do not fire. Details under [Substrate details](#substrate-details) below if curious. Surface-by-surface compatibility table in [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

**The legal layer (as-needed, not daily).** A safety layer for hires, fires, NDAs, VAT, license renewals, and walking into a lawyer's office prepared. UAE founders get a full reference set out of the box. Founders elsewhere scaffold their jurisdiction and load their own sources. The skill never invents law and surfaces overdue compliance deadlines from `context/compliance.md` on every session. Details under [Legal layer](#legal-layer) below.

**The capture-and-cite loop.** `/rant` qualifies a raw thought dump with one question, then routes it to a decision, draft, plan, log, or capture path. `/dream` distils captured rants into patterns, flags, parked decisions, and needs. Away from the laptop, the same loop still works: drop phone dictations or pasted notes into `capture/inbox/` (or just paste the pile), say "catch up", and the OS files everything into the brain through a self-teaching names glossary - known names correct silently, unknown ones stay marked rather than guessed. Channel guide in [docs/capture-anywhere.md](docs/capture-anywhere.md). Every new brain entry gets a stable `<channel>-YYYY-MM-DD-NNN` ID stamped at write time. The dream digest cites those IDs in one line each instead of restating content. `knowledge-capture` writes distilled takeaways from books, calls, and articles into `brain/knowledge/` with the same ID convention so proposal-writer and strategic-analysis can read them back. Optional: opt in to a tool-call observation log with `FOUNDER_OS_OBSERVATIONS=1` and `/dream` rolls each day's activity into an OBSERVED section.

---

## What it costs

One Claude subscription. Everything else is free.

- **Founder OS** (this repo) - free, MIT licence
- **Claude Code** (the interface) - free to install
- **Claude subscription** - any paid Claude plan with enough context (100K+ tokens). Most plans are $20-100/month.

Founder OS is built for Claude Code: the setup wizard, the slash commands, and the SessionStart and Stop hooks all run there. A paid Claude plan is the only real cost - free tiers usually don't have the context for this to work well. The files themselves are plain markdown and travel with you, so you can read them in any AI you paste them into, but the wizard, commands, and hooks run in Claude Code. You are not locked in.

**Which model?** Any current Claude model runs the OS - Opus for judgment-heavy work, Sonnet for everyday speed, Haiku for quick mechanical tasks. It is not pinned to a model, so newer is always fine. To match the model to the task, see [docs/model-routing.md](docs/model-routing.md).

---

## Before you install

You need three things:

- **Claude Code** - free. Download at [claude.ai/code](https://claude.ai/code). Desktop app for Mac and Windows.
- **A paid Claude plan** - Claude Pro or Claude Max. Free tiers lack sufficient context.
- **Python 3.11+** - for the runtime scripts. Check with `python --version`, then `python3 --version`, then `py -3 --version` - the first one that answers is the one your machine uses. (Bare `python3` is unreliable on Windows.)

That is it. No git. No database. No server. No Notion account required.

Git is deliberately not on the list. The OS runs without it: every session's file changes are snapshotted with a one-command restore - a rolling net that keeps the last 12 sessions, not a permanent timeline. Full version history begins when you say "own my history" - the OS installs git and wires it up itself, and from then on every save is a permanent point in time. You say yes once and never type a git command.

---

## How to use it - talk to Claude

The OS routes on natural language. Say what you need ("set up my voice profile", "what's on for today?", "prep me for my call with Sarah") and the right skill fires. Slash commands are speed shortcuts for power users, not the primary surface. If you forget what's available, say "show me what you can do" (or run `/founder-os:menu`) and the OS returns 5 to 7 capabilities scored against your current state.

---

## Install

Five install paths. The one that needs no Git and no terminal comes first. Full step-by-step for each in [docs/install.md](docs/install.md).

**Not comfortable in a terminal?** Start with the ZIP download below - three steps, nothing typed - or the plugin install after it. Neither needs a terminal.

### Download ZIP (no Git or terminal, own it in 10 minutes)

1. **[Download the ZIP](https://github.com/ARCASSystems/FounderOS/archive/refs/heads/main.zip)**
2. Right-click, **Extract All** (Windows) or double-click it (Mac). Put the folder wherever you keep your work.
3. Open the folder in Claude Code and say **"set up Founder OS"** (or run `/setup`).

That is the whole install. No git, no curl, no terminal command, no account beyond the Claude plan you already have. Updates work the same way: say "update Founder OS" and the OS re-downloads the ZIP itself, refreshes its own engine files, and never touches your data.

**When to choose:** You want the fastest path from zero to owning the system, with nothing new installed on your machine. The folder is yours from the first second - plain markdown you can read, back up, or delete.

**The ZIP is the door, git is the steady state.** Version history is off at first; the OS still snapshots every change each session. When you are settled in, say **"own my history"** once - the OS installs git itself and wires everything, nothing for you to type. From then on updates flow through git instead of ZIP re-downloads, history and undo go all the way back, and git keeps itself maintained. One yes, and the update problem is solved permanently.

### Plugin marketplace (no terminal, cleanest Claude Code experience)

```
/plugin marketplace add ARCASSystems/FounderOS
/plugin install founder-os@founder-os-marketplace
```

Then say "set up Founder OS" (or run `/founder-os:setup`). If setup is not recognised, run `/reload-plugins` first.

**When to choose:** You want the gentlest path. Two commands typed inside Claude Code, no terminal install step, and auto-updates via `/plugin update`. Needs Claude Code with a paid Claude plan. The plugin is the engine and stays out of your way under `~/.claude/plugins/`; setup builds your OS in a folder you own (default `~/founder-os/`). Engine and data are separate - your files are yours even if you remove the plugin.

### One-line curl (fastest if you live in a terminal)

```bash
curl -fsSL https://raw.githubusercontent.com/ARCASSystems/FounderOS/main/install.sh | bash
```

Clones FounderOS to `~/founder-os` (hook scripts and `settings.json` come along in the clone) and sets up in place, so your data, hooks, and commands live in one folder you own. Then prints the natural-language next step. Requires git, Python 3.11+, and bash (on Windows, install git-bash first). Re-running the same command on an existing install offers an update instead.

**When to choose:** You are comfortable in a terminal on macOS or Linux (or git-bash on Windows) and want one command.

### Manual git clone (most reliable)

```bash
git clone --depth 1 https://github.com/ARCASSystems/FounderOS.git ~/founder-os
```

Open Claude Code in the cloned folder, then say "set up Founder OS" (or run `/setup`). Requires git and Python 3.11+. Commands use bare names on this path - no `/founder-os:` prefix.

**When to choose:** The plugin install fails, or you want full control of the local copy and manual `git pull` updates.

### Claude Cowork (partial - natural-language only)

Open the FounderOS folder in Cowork and attach `CLAUDE.md` as folder instructions. Hooks and slash commands do not fire in Cowork. Use it for drafting and timed runs; return to Claude Code for hooks, cadence refresh, and commits.

**When to choose:** You use Cowork for day-to-day drafting and want the OS context available there alongside your Claude Code install.

---

## Setup ladder (40 min total, do in this order)

1. **Install** - pick an [install path](#install) above (5 min). If your install uses git (curl or clone paths, or after "own my history"), run `./scripts/install-git-hooks.sh` to wire the privacy pre-commit hook (operator-only). Out of the box it already blocks committed secrets (API keys, tokens, bot tokens, PEM private keys), em/en dashes, and AI-attribution trailers - no config needed. To also block your private names, open `scripts/private-name-patterns.txt` and add at least your own name (`\bYourName\b`); the name check stays off until that file has a pattern, while the secret and voice checks run regardless. The file is gitignored, so your names never leave your machine. On a ZIP install this step waits until you turn on version history - there is nothing to wire before then.
2. **Say "set up Founder OS"** (or run `/founder-os:setup`) - the wizard builds your operating layer from your answers (15 min). It reads which kind of operator you are (founder, career-mover, builder, student) so the OS leads with what your situation needs, and seeds your brain with a starter flag, pattern, parked decision, and log entry so your first session is not a blank screen.
3. **Say "set up my voice profile"** (or run `/founder-os:voice-interview`) - so every writing skill sounds like you, not Claude (10 min)
4. **Say "set up my brand profile"** (or run `/founder-os:brand-interview`) - so every deliverable looks like you (10 min)

After that, `/founder-os:status` audits the OS anytime, `/today` gives a one-screen view of today, and `/next` recommends one action. Full first-day path in [docs/first-day.md](docs/first-day.md). Full per-command reference in [docs/commands.md](docs/commands.md). Full per-skill reference (outcome, reads, writes, voice rules, prereqs, follow-ups) in [docs/skills.md](docs/skills.md).

> **Path B users (manual git clone):** drop the `/founder-os:` prefix. Commands are bare names: `/setup`, `/voice-interview`, `/brand-interview`, `/today`, etc. The plugin namespace only activates on Path A. See [docs/install.md](docs/install.md) for the exact commands per path.

---

## What ships in this repo

### Skills (87)

Grouped by when you reach for them, not by category. Each row in [`docs/skills.md`](docs/skills.md) names the outcome, reads, writes, voice rules, prereqs, and follow-ups.

The skills are organised into **role packs**, each a function a solo founder covers alone and each opened by one front-door skill that routes you to the rest: LinkedIn (`linkedin-start`), Pipeline (`pipeline-start`), Content (`content-start`), Delivery (`delivery-start`), Money (`unit-economics`), and Decisions (`decisions-start`). You arrive for one job and the pack invites you into the others, never forces you. A pack is a naming convention plus a manifest (`skills/<pack>-pack.md`), not a folder.

One to call out is the **LinkedIn pack**: say "help me with my LinkedIn", pick an outcome (leads, a better job, a louder brand, or a healthier network), and the OS aims your own data export at it - a ranked outreach worklist, a deep network audit, dormant-contact revival, and an algorithm-aware content direction. All local, free-plan, within LinkedIn's terms - no scraper, no automated actions, message content never read.

### Slash commands (38)

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

The skill is jurisdiction-aware. It reads a `jurisdiction:` field from `core/identity.md` and loads only that jurisdiction's reference folder. UAE founders get a complete reference set out of the box - 9 domain files (company formation, employment, tax/VAT, visas, contracts, IP, data protection, dispute resolution, industry permits) plus 27 tracked primary government sources (mohre.gov.ae, tax.gov.ae, icp.gov.ae, det.gov.ae, difc.ae, adgm.com, etc.) plus document templates for NDAs, employment offers, privacy policies. Verified 2026-04-25.

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

Founder OS does not assume your stack. Most of the 87 skills work end-to-end with zero MCPs. A few (`email-drafter`, `meeting-prep`, `knowledge-capture`, `session-handoff`) produce better output with the relevant integration connected. Without a calendar MCP, `/today` shows `no scheduled event next 24h`. Without an email MCP, you paste the thread by hand. Without a Notion MCP, captures stay in `brain/log.md` as markdown. Nothing hard-fails on a missing MCP. Full catalog in [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

---

## Who this is NOT for

You want a no-code app with a UI. This is files plus skills, not an interface. You operate it through Claude Code.

You need shared state across a team. Founder OS is single-user. The Company OS layer (not in scope; community forks may extend) is what handles team coordination.

You want push notifications, automated triggers, or anything that fires while you sleep. Founder OS is the thinking layer. n8n, Make, Zapier, or your own scripts handle offline triggers.

You want a tool you install and forget. Founder OS earns its keep the other way round: you drop a thought in when it happens, glance at the brief when you open Claude Code, and in return it stops you re-remembering the same open loops and re-deciding the same calls. The floor is low, capture takes seconds, but it is not zero. If you will not talk to it at all, it sits unused like every other system, and that part is honest.

---

## What it is not

Not a workflow engine. Not a webhook server. Not a cloud tool that stores your data on someone else's servers.

Your Notion. Your Claude. Your files on your disk if you want them there. If you want to delete it, run `/founder-os:uninstall` or just delete the folder. Nothing to unsubscribe from.

## Why local-first is the security story

2026's defining AI-agent security incident (135,000+ exposed instances, plaintext key files, a poisoned skills marketplace) needed three doors: a server listening on a port, a stored API key, a third-party skill registry. Founder OS has none of the three - nothing listens, your subscription sign-in replaces key files, and every skill ships in this repo as markdown you can read before it runs. Your brain stays on your disk; deleting the OS is deleting a folder. The full record with sources, plus the honest limits: [docs/why-local-first.md](docs/why-local-first.md).

If you need crons, webhooks, offline triggers, or anything that fires while you sleep, that is a different tool (n8n, Make, whatever you use). Founder OS holds the thinking layer. You stay in charge of the rest.

---

## Substrate details

Background plumbing the wizard sets up. You do not need to read this to use the system. The wizard handles all of it. Here for the curious.

- **Decay-aware brain layer.** Set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires.
- **Stable entry IDs.** Every new brain entry (log, pattern, flag, parked, need, know) is stamped with a `<channel>-YYYY-MM-DD-NNN` ID at write time. Skills cite IDs in summaries instead of restating content.
- **Token-aware progressive query.** `scripts/query.py` and `/founder-os:query` operate in three modes: `index` for top hits, `timeline` for entries within a 7-day window of an anchor file or ID, `full` for the body of specific IDs. Pure markdown plus stdlib, no vector DB.
- **Opt-in observation log.** Set `FOUNDER_OS_OBSERVATIONS=1` to enable a `PostToolUse` hook that appends one line per tool call to `brain/observations/<date>.jsonl`. `/dream` rolls each day's activity into an OBSERVED section. Off by default.
- **`system/quarantine.md`** is a catch-net so failing hooks and cron jobs stop being silent.
- **Approval gate matrix** at `rules/approval-gates.md` tells the OS what to auto-run, what to ask about, and what to refuse outright.
- **`brain/relations.yaml`** is a hand-curated graph of edges between files, plus auto-extracted `[[wikilinks]]` refreshed by `/founder-os:wiki-build`.
- **Auto-memory layer.** Claude Code reads `~/.claude/projects/<slug>/memory/MEMORY.md` automatically at session start. The wizard seeds it so behavioral guards persist across sessions.

Full convention spec in `rules/entry-conventions.md` (generated by setup).

---

## Cloud Claude (web, desktop, mobile)

The Notion Starter Kit was scoped but is not yet shipped; community forks welcome. The system prompt at [`notion-package/system-prompts/founder-os-project-prompt.md`](notion-package/system-prompts/founder-os-project-prompt.md) is available for preview and testing only. Use the Claude Code path for the full setup experience.

Slash commands and hooks are Claude Code only. Local file writes run on any surface attached to the folder with write access - Claude Code, or a desktop folder-attached surface like Cowork or Antigravity. Web-only Cloud Claude reads this repo's files as context but cannot write locally or run `/founder-os:setup` from a checkout. Full surface-by-surface matrix in [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

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

Version 1.41.2. Public release. 87 skills, 38 commands. Every push to main runs three CI gates (doc and install parity, the privacy guardian, the LinkedIn pack acceptance suite) and a weekly integrity audit runs on top. The maintainer's full test suite runs upstream before anything lands here; it is not shipped in this repo, so the badge row above is the claim you can verify.

v1.41 is the proof patch on the Second Brain release. Setup now ends by running its own health check automatically and reading the result back to you, so you never leave on trust that the wiring landed - a partial install shows up in the last minute of setup instead of days later mid-task. And session one now closes with your first real proposal run in the flow: the OS reads the snapshot it just wrote and names your single next move toward a paying customer, with the plain statement of how it compounds - every session feeds the brain, so the moves sharpen because they are read from your real state, not guessed. (v1.41.1 removed a rendered HTML card that shipped hours earlier in v1.41.0: an artifact you have to open somewhere else adds friction instead of removing it, and the in-flow proposal plus the growing brain files are the real proof. It also names git as the recommended steady state: the ZIP gets you in, and one yes later the OS installs git for you - after which updates and history maintain themselves.) Same floor: one Claude plan, no key, nothing leaves your machine.

v1.40.1 is the Second Brain release's second wave: memory and money. A PreCompact hook flushes unsaved session facts into the brain files before the context is compacted, so nothing load-bearing dies in a summary. Boot got cheaper on grown installs - the OS orients from a compact snapshot and opens the full files only when the task needs them. A housekeeping sweep keeps a months-old brain honest: one screen of accumulated debt with a fix command per line, and a supervised fix mode for the reversible half. And the OS now knows how your business makes money - a business-model axis captured at setup drives which numbers lead in every money conversation, with a plainly stated honesty rule for regulated and deep-tech operators: accounting math yes, invented domain assumptions never.

v1.40.0 is the Second Brain release. It attacks the distance between you and owning the system. Install is now three steps and nothing typed: download the ZIP, extract, say "set up Founder OS" - git is gone from the prerequisites, and when you want full version history the OS installs and wires git itself on one consent-gated yes ("own my history"). Until then a pre-git undo floor covers you: every file the OS edits is snapshotted before the write, and "what did you change" returns the per-session manifest with a one-command restore for each snapshotted file (files over 2 MB or written straight to disk by a shell command are listed but not restorable). Capture now works away from the laptop: drop phone dictations, voice-note exports, or pasted saved-messages piles anywhere they can land as text, say "catch up", and the OS files them into the brain through a self-teaching names glossary that corrects known mis-hearings and never guesses unknown ones. The local-first security story is now written down with the 2026 record as the counterfactual (docs/why-local-first.md), and CI gained a hooks-parity gate so every hook provably ships for both bash and PowerShell.

v1.38.0 is the Ease release. It finishes the front door and the heartbeat: the skills are grouped into role packs, each opened by one front-door wedge so you arrive for one job and are invited into the rest; the OS owns git for you (say "save my work", "what changed", "undo to before this morning"); it connects a tool when you ask ("connect Telegram", "connect my calendar"); and it runs daily, weekly, and monthly routines, with a flagship that returns the three changes to make in your business now. It also completes the optional voice scaffold: on top of "add voice", you can now "add a mouth" (have answers read aloud, free and local by default), "add hands" (let it open things and save notes, with a confirm gate that stops every irreversible action for an explicit yes), and "tune" (it reads your local voice usage and proposes the next instant handler, never changing anything on its own). Voice stays optional - the OS is complete as text.

v1.37.0 does two things. It installs the OS into one folder you own (default `~/founder-os`) instead of a hidden cache dir, names the engine and your data as the separate things they are, and detects an existing install so you never end up with two copies. And it makes the role system real: it adds two role modes you can reach when you need them, CSO for the portfolio view across everything you run and CTO for your tool stack and automations, makes the BD trigger honest (you invoke it, it does not silently flip on a count nothing reads), and tells you the plain phrase to switch lens yourself ("switch to CMO").

v1.36.1 is a patch: it clears a red CI gate, stops the CMO role shipping an unfilled token, captures your timezone at setup, steers non-technical founders to the no-terminal install, and corrects the provider claim to match what actually runs (Claude Code).

v1.36 adds the output bias self-check. The OS now runs a check on its own reasoning before it gives an opinion of consequence, attaching a counter-case, a confidence level, what evidence is absent, and the do-nothing option, so advice is named-and-countered instead of confidently biased. It ships as `rules/biases.md`, a `/founder-os:devil` command to run it on demand, a boot rule plus a plain-language explanation of why the OS pushes back, and a one-line decision-prompt nudge in the capture hook. Full release history in [CHANGELOG.md](CHANGELOG.md).

---

## Release cadence and forking

FounderOS ships in deliberate increments. Each release closes a specific gap that the previous one made visible. v1.21 added the visible queue and health check. v1.22 added the privacy tag and observation rollup. v1.23 added the natural-language capture path. v1.24 added Python preflight gates so writing and reasoning skills fail visibly when their data is not set up, rather than producing generic output silently. New releases land when there is a real gap worth closing, not on a calendar.

Community forks are encouraged. If you build something on top of FounderOS, open a discussion thread linking your fork. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for what we accept and [`docs/forking.md`](docs/forking.md) for extension points.

**The technical lane is left open on purpose, not built.** Founder OS is plain markdown a coder can fork and extend: turn an idea into a buildable spec, wire deeper automation through the hands layer, or add vector retrieval over the brain. None of that ships by default, because most founders do not write code and the OS does not pre-build for a user who is not in the room. The files are open if you are that user. The brain stays plain markdown either way, so nothing you add locks you in.

## Contributing and security

- Bugs and small fixes: open an issue or PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for what we accept and what stays in the upstream private repo.
- Security: report vulnerabilities to `solutions@arcassystems.com`. See [`SECURITY.md`](SECURITY.md) for scope and response times.

## License

MIT. Copyright (c) 2026 ARCAS Systems. See [LICENSE](LICENSE).

---

People first. Systems second. AI where it earns the right.

Built by [ARCAS Systems](https://arcassystems.com).
