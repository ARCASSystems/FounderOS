# Founder OS

![Doc and Install Parity](https://github.com/ARCASSystems/FounderOS/actions/workflows/doc-parity.yml/badge.svg) ![guardian](https://github.com/ARCASSystems/FounderOS/actions/workflows/guardian.yml/badge.svg) ![LinkedIn Pack Acceptance](https://github.com/ARCASSystems/FounderOS/actions/workflows/linkedin-pack.yml/badge.svg)

Get an operating system with your first team already on it: five named digital employees with written job descriptions, a brain that keeps everything you tell it and invents nothing, and your working life - clients, pipeline, decisions, the week - modelled in files you own. Six files run your company, or the part of one you run. Claude works from them every session.

Built from markdown and Python because every AI reads both. The model is the part you will swap one day. The brain is the part you keep.

Owned by you. Runs locally in Claude Code. Talk to it.

---

**New here? [Read the Founder OS Playbook first](https://arcassystems.com/playbook)** - a visual walkthrough with screenshots: the problem, the three parts, how to start, and what not to do. Opens framed in any browser, about 15 minutes. It lives on the web so it never drifts out of date; there is no copy shipped in this repo.

**[Download Founder OS](https://github.com/ARCASSystems/FounderOS/archive/refs/heads/main.zip)** - unzip it, double-click **Start Founder OS**, and the setup wizard is talking. No git, no terminal, no curl. Or install via plugin marketplace, one-line curl, or git clone. See [Install](#install) below.

---

**What it is. What it is not.** Your personal brain. Your files, queryable by you. Not team-shared. Not always-on.

---

## What you get on day one

Install, answer the wizard's questions, and by the end of the first sitting:

- **An OS built around your actual work.** The wizard interviews you - what you run, who waits on you, what is stuck - and writes your six operating files from the answers, filled, not blank. The deeper layers are named waits, not surprises: quarterly targets and business-context rows arrive marked for you to fill, and voice and brand are two ten-minute interviews you run right after.
- **Your first team, named and chartered.** A daily assistant, a next-move caller, a capture filer, an account manager, and a reviewer that audits the other four. Each has a written job description, a list of exactly what it may touch, and a track record that starts empty and fills as you grade its runs. All five start gated: they propose, you decide.
- **A brain that remembers and does not invent.** What you tell it lands in plain markdown: log, flags, patterns, parked decisions, knowledge. Raw dumps are captured whole; meetings and passing facts file with your confirm. A name or number said once stays marked unconfirmed until you confirm it, and money figures and contact details never enter the provisional ledger at all, by design.
- **Your digital infrastructure, modelled.** Clients and leads, today and the week, decisions made and parked, your network, your tool stack, and the two profile slots your voice and brand interviews fill. One folder you can read, back up, move, or delete.
- **A gate between a draft and a send.** The OS writes the client update, the follow-up, the proposal. It sends none of them. That line is written into each role's charter and its skill's declared tool list, kept identical and audited for drift - a written contract, not a polite request in a prompt. Anything outside a role's grant lands in your normal permission prompts, never silently.

If you stop using it, you lose nothing: it is a folder of files you can read without us. That is the whole risk of trying it.

## The one habit that makes it compound

Tell it what happened. Say what you did, what someone said, what is stuck - typed, dictated, or pasted in from your phone. A session that hears something worth keeping writes it into your files, so the next session starts warmer than this one; captures land raw, and one word ("dream") distils them into patterns, flags, and parked decisions. Once a week, close the loop: the retro offers the distil pass if captures are sitting raw, rolls the week, forces a keep-or-kill on every stall, and grades the team, so the roles that perform earn more room. Seconds a day, twenty minutes a week. Everything else in here compounds off those two habits.

## Who runs this

You run the business, run a P&L inside one, or run a role inside one. Owner, agency lead, consultancy head, head of department, the employee a whole workstream lands on. If work stops with you, this fits, and the wizard reads which one you are and shapes the OS to it:

- **The founder.** The North Star is the next paying customer. The pipeline, the cadence, and the next-move caller all point at it.
- **The employee a workstream lands on.** You tell the wizard who you answer to and what is yours to own. The next-move caller aims at the work you own, and the account manager drafts the status update to whoever is waiting on it.
- **The career-mover, the builder, the student.** Same brain, same capture, same cadence, led by what your situation needs. The next-move engine speaks founder and operator today; for the rest it says so honestly instead of pretending.

You are sharp but your day is chopped into thirty-minute pieces. You have tried productivity templates that promised the world and quietly stopped getting opened by week three. This is not a template. It is an operating layer: it listens, routes, forgets nothing, and pushes back when you are about to ship something half-baked.

## Prove it in ten minutes, offline

Most of the claims above are checkable on your machine without trusting us:

- **The brain answers with no model at all.** `python scripts/query.py "<term>"` searches your whole brain - index mode by default, `--mode timeline` and `--mode full` for depth - pure Python, no API, no vector database. This is what "your files outlive any model" means in practice.
- **The provisional-facts rule is a ledger, not a promise.** `python scripts/unconfirmed_facts.py list` shows the provisional names and claims waiting on your confirm or cut - a ledger that refuses money figures and contact details outright.
- **Undo works before git exists.** Say "what did you change" and every file the OS edited through its editing tools this session lists with a one-command restore. A file a shell command wrote is outside that net until version history is on - the one honest gap.
- **The team's boundaries are audited, not asserted.** After setup, `python scripts/employee_verdict.py charters` reads every role's charter against the tool list its skill declares, both directions, and names any drift.
- **The capability page is generated, not written.** `python scripts/skills_sync.py --capabilities` rebuilds [docs/what-this-can-do.md](docs/what-this-can-do.md) from the skills on disk - it cannot claim a skill that is not there.

---

## How is this different from just using Claude or ChatGPT well?

The honest version of that question is sharper than it sounds. Someone who prompts well already gets good answers. So what does a folder of markdown add?

Four things, and none of them arrive from writing a better prompt.

**Your context is a folder you own.** Everything the OS knows about your work sits in plain markdown on your disk. Not in a chat history, not in a vendor's memory feature, not in an account you can be locked out of. When a better model ships next year you point it at the same folder and keep everything it knows - the operating files carry the knowledge; only tool conveniences (Claude Code's behavioural memory, the pre-git session undo net) stay with the tool. When you want to know what it knows, you open a file.

**Nothing becomes a fact because it was said once.** A name mentioned in passing, a number from a call, a claim in a transcript. The OS marks those provisional and asks you to confirm or cut them before it repeats them anywhere. An assistant that remembers everything you said will eventually say your own work back to you slightly wrong, at the worst possible moment, with total confidence. This is the part that stops that.

**You get five named roles, and you grade them.** Not one assistant that is good at everything and accountable for nothing. Each role has a written job description, a list of exactly what it may touch, and a record that starts empty and fills as you grade its runs. When one keeps getting something wrong you change its definition once, instead of correcting it every week.

**There is a gate between a draft and a send.** The OS writes the client update, the follow-up, the proposal. It delivers none of them. That boundary is written into each role's charter and its skill's declared tool list, kept identical and audited for drift, and anything outside a grant still routes through your own permission prompts. A written, audited contract holds on the day you are tired and moving fast; a sentence buried in a prompt does not.

A good chat session is a good hour. This is the part that compounds over a year, because what it learns gets written down in files you keep.

## Founders, teams, and the people inside them

This was built for one person running a business alone, and that is still who it fits best. It also works for an employee running part of a job: you are the operator of your part, the setup wizard asks who you answer to and what is yours to own, and every seat serves that scope. One product, one track, wider door.

It works with a team too, with one thing to be clear about: each person runs their own OS. Yours holds your context, theirs holds theirs, and what passes between them is shared work items.

What deliberately never passes between two of them, in either direction: pay and commercial terms, one person's private profile landing in someone else's system, and personal data about anybody. Convenience will make an argument for it about once a month. The answer stays no.

Several people inside one live session is not something this does today. The whole category is circling that problem and nothing here pretends to have solved it.

---

## What makes this different

- **You own the operating logic, not a vendor.** Every other tool in this category asks you to make how you work legible to their platform, so their system can act on it. What you get back is behaviour inside their product; what they keep is the record of how your business actually runs. This is files on your machine. You can read them, edit them in any text editor, copy them to a USB stick, fork them, and keep every one of them the day the vendor disappears or triples the price. That difference is not a feature they forgot to build. Copying it would cost them their revenue model.
- **It tells the truth about what it produces.** Capture side: a name or a number heard once is held as unconfirmed until you confirm or cut it, and the ledger refuses to hold contact details or amounts at all. Research side: every load-bearing number in an analysis, a proposal, or a market read carries a tier - measured, sourced, or estimated - and `claims_check.py` reads the finished document back for untagged numbers, quotes with no source, universal negatives nobody can verify, and arithmetic that does not reconcile. It warns, it never blocks, and it never edits your file.
- **Stall detection built in.** The system watches for rolling items and forces keep/kill/escalate decisions. Every retro.
- **Revenue loop enforcement.** Every outreach or content action must log same-session. Catches the gap between "I'll do X" and "I did X."
- **Role as router.** COO, BD, CMO, Chief of Staff are behavioural modes, not personas. The right mode activates based on what you are actually doing.
- **Plan A defines Plan B.** This product is a derivative of an actual founder's daily use. Features graduate from personal use into the product only after surviving contact with live P&L.
- **Talk to it, from anywhere.** Built around dictation. Claude Code's built-in dictation is the primary input, and any voice-to-text tool you already use works just as well. Claude Code runs locally as a CLI and through the cloud app (claude.ai/code), so you can start and drive a full session from your phone too. A cloud session runs in a remote sandbox on a branch rather than on your local disk, so the local-first path stays your machine while the cloud path is there when you are away from it.
- **Decay-driven keep/kill.** Set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires. The OS does not auto-kill, you decide.
- **Invisible version control.** Full history and undo, no git command ever typed. Say "save my work", "what changed", or "undo to before this morning" and the OS wraps git for you. Local by default; nothing pushes anywhere unless you ask. Undo is fail-safe: it saves your current work first and can never lose it. Git itself is optional at install: before you turn it on, session snapshots cover you - every file the OS edits through its editing tools is snapshotted before the write and restorable per file up to 2 MB, a rolling net across the last 12 sessions (`/changes` lists those changes and one command restores any that were snapshotted; files over 2 MB stay listed without a restore, and a file a shell command writes directly is outside the net entirely until version history is on). Full history begins the moment you say yes: the OS installs and wires git itself, your data included, and from that save onward every version is permanent - nothing for you to type.

---

## What you actually get

Four layers, the same four the Founder OS Playbook draws on a napkin. Each does one job. Remove any one and the whole thing breaks.

- **The Brain** - memory and judgment, all plain markdown you own. The six operating files (priorities, clients, decisions, today, the week) hold the state of the business right now. The brain layer (log, flags, patterns, parked decisions, knowledge) holds what happened, what is stuck, and what is worth reusing. A wiki layer adds `[[cross-references]]` between files plus a source archive (`raw/`) for articles and transcripts.
- **The Skills** - the abilities the brain has: draft a follow-up, prep a meeting, write a proposal, run the weekly retro. They read and write across the Brain, so the output lands like you, not like a chat window.
- **The Hands** - the tools the skills reach for: calendar, inbox, notes, transcriber, voice capture. Wired through optional MCPs; nothing hard-fails when one is missing.
- **The Heartbeat** - the rhythm that keeps it current: a daily anchor at the start of the day, a weekly retro at the end of the week, and a SessionStart brief that surfaces stalls and stale cadence.

**Six role modes.** Four switch automatically based on what you are doing: COO (default), BD, CMO, Chief of Staff. Two more are there when you need them and you invoke explicitly: CSO for the portfolio view across everything you run, CTO for your tool stack and automations. To change lens yourself, just say "switch to CMO" (or any role).

**It runs when you open it, plus hooks.** Some tools in this space monitor your work all day and act on their own. This one does not, and that is a real difference rather than a gap in the copy. It runs when you start a session, when a hook fires (session open, before a write, before compaction, on stop), and when you ask. What you trade for that is a system with no daemon, no server, no account, and nothing running against your files while you are asleep.

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

### Your first session, in nine sentences

Setup ends by telling you who you have. This is what to type next. Say these out loud or paste them; none of them is a command you have to remember, and every one works on a fresh install (number 9 will offer the ten-minute voice interview first, so drafts sound like you and not like a template).

1. `What's on for today?`
2. `Log this: <whatever just happened>`
3. `What should I do next?`
4. `What's on my plate?`
5. `I just got off a call with <name>, here's what happened: ...`
6. `Help me decide between <A> and <B>`
7. `What would an investor ask me about this business?`
8. `Save my work`
9. `Draft a follow-up to <name> about <thing>`

If only one of these lands this week, make it number 2. Everything the OS does later is built on having something written down, and the first time it answers a question using a thing you told it three weeks ago is the moment the whole system stops feeling like a folder.

A fuller list, generated from the skills actually installed on your machine, is in [docs/what-this-can-do.md](docs/what-this-can-do.md). Scenario walkthroughs are in [docs/a-day-in-the-os.md](docs/a-day-in-the-os.md).

---

## Install

Five install paths. The one that needs no Git and no terminal comes first. Full step-by-step for each in [docs/install.md](docs/install.md).

**Not comfortable in a terminal?** Start with the ZIP download below - three steps, nothing typed - or the plugin install after it. Neither needs a terminal.

### Download ZIP (no Git or terminal, own it in 10 minutes)

1. **[Download the ZIP](https://github.com/ARCASSystems/FounderOS/archive/refs/heads/main.zip)**
2. Right-click, **Extract All** (Windows) or double-click it (Mac). Put the folder wherever you keep your work.
3. Double-click **Start Founder OS** in the folder (Windows: the `.bat` file; Mac: the `.command` file). It opens Claude Code right there and starts the setup wizard talking. If Claude Code is not installed yet, it says so plainly and opens the download page instead of failing. First run only: Windows may show a note about a downloaded script - let it run (the file is plain text, right-click and Edit to read it); on a Mac, right-click the file and choose Open once.

Prefer not to run a script? The spoken way works the same: open the folder in Claude Code and say **"set up Founder OS"** (or run `/setup`).

That is the whole install. No git, no curl, no terminal command, no account beyond the Claude plan you already have. Updates work the same way: say "update Founder OS" and the OS re-downloads the ZIP itself, refreshes its own engine files, and never touches your data.

**Already have notes?** If you keep an Obsidian vault or a folder of markdown, setup can move the OS in next to your notes instead of starting a separate folder - your existing files are never touched. Say "set up Founder OS inside my vault". Details in [docs/adopt-existing-notes.md](docs/adopt-existing-notes.md).

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

**When to choose:** The plugin install fails, or you want full control of the local copy. Updates work the same as every path ("update Founder OS"); `git pull` also works if you prefer raw git.

### Claude Cowork (partial - natural-language only)

Open the FounderOS folder in Cowork and attach `CLAUDE.md` as folder instructions. Hooks and slash commands do not fire in Cowork. Use it for drafting and timed runs; return to Claude Code for hooks, cadence refresh, and saves.

**When to choose:** You use Cowork for day-to-day drafting and want the OS context available there alongside your Claude Code install.

---

## Setup ladder (about 90 minutes end to end - stop after step 2 and come back any time)

1. **Install** - pick an [install path](#install) above (5 min). If your install uses git (curl or clone paths, or after "own my history"), setup wires the privacy guard for you; `./scripts/install-git-hooks.sh` re-wires it by hand if you ever need to. Out of the box it already blocks committed secrets (API keys, tokens, bot tokens, PEM private keys), em/en dashes, and AI-attribution trailers - no config needed. To also block private names, open `scripts/private-name-patterns.txt` and add the names that must never enter your files (`\bClientName\b` - a client under NDA, a person you keep off the record); the name check stays off until that file has a pattern, while the secret and voice checks run regardless. Do not add your own name: once you own your history, your identity file is tracked by design, and your own name as a pattern would block every save that touches it. The file is gitignored, so any names in it never leave your machine. On a ZIP install this step waits until you turn on version history - there is nothing to wire before then.
2. **Say "set up Founder OS"** (or run `/founder-os:setup`) - the wizard builds your operating layer from your answers (15 min). It reads which kind of operator you are (founder, career-mover, builder, student) so the OS leads with what your situation needs, and seeds your brain with a starter flag, pattern, parked decision, and log entry so your first session is not a blank screen.
3. **Say "set up my voice profile"** (or run `/founder-os:voice-interview`) - so every writing skill sounds like you, not Claude (10 min)
4. **Say "set up my brand profile"** (or run `/founder-os:brand-interview`) - so every deliverable looks like you (10 min). Three interviews exist and do different jobs: voice-interview = how YOU write, brand-interview = how your documents LOOK, brand-voice-interview = how a BRAND you run writes (only if you run one)

After that, `/founder-os:status` audits the OS anytime, `/today` gives a one-screen view of today, and `/next` recommends one action. Full first-day path in [docs/first-day.md](docs/first-day.md). Full per-command reference in [docs/commands.md](docs/commands.md). Full per-skill reference (outcome, reads, writes, voice rules, prereqs, follow-ups) in [docs/skills.md](docs/skills.md).

For the short answer to "what can this actually do", [docs/what-this-can-do.md](docs/what-this-can-do.md) lists every capability in plain language. It is generated from the skills on disk rather than maintained by hand, and on installs with version history the privacy guard refuses a skill change that leaves it stale, so it is never a wish list. Rebuild it any time with `python scripts/skills_sync.py --capabilities`.

> **ZIP and git-clone users (Paths B and C):** drop the `/founder-os:` prefix. Commands are bare names: `/setup`, `/voice-interview`, `/brand-interview`, `/today`, etc. The plugin namespace only activates on Path A. See [docs/install.md](docs/install.md) for the exact commands per path.

---

## What ships in this repo

### Skills (93)

Grouped by when you reach for them, not by category. Each row in [`docs/skills.md`](docs/skills.md) names the outcome, reads, writes, voice rules, prereqs, and follow-ups.

The skills are organised into **role packs**, each a function a solo founder covers alone and each opened by one front-door skill that routes you to the rest: LinkedIn (`linkedin-start`), Pipeline (`pipeline-start`), Content (`content-start`), Delivery (`delivery-start`), Money (`unit-economics`), and Decisions (`decisions-start`). You arrive for one job and the pack invites you into the others, never forces you. A pack is a naming convention plus a manifest (`skills/<pack>-pack.md`), not a folder.

One to call out is the **LinkedIn pack**: say "help me with my LinkedIn", pick an outcome (leads, a better job, a louder brand, or a healthier network), and the OS aims your own data export at it - a ranked outreach worklist, a deep network audit, dormant-contact revival, and an algorithm-aware content direction. All local, free-plan, within LinkedIn's terms - no scraper, no automated actions, message content never read.

### Slash commands (44)

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

Founder OS does not assume your stack. Most of the 93 skills work end-to-end with zero MCPs. A few (`email-drafter`, `meeting-prep`, `knowledge-capture`, `session-handoff`) produce better output with the relevant integration connected. Without a calendar MCP, `/today` shows `no scheduled event next 24h`. Without an email MCP, you paste the thread by hand. Without a Notion MCP, captures stay in `brain/log.md` as markdown. Nothing hard-fails on a missing MCP. Full catalog in [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

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

Have an idea but no business yet? That counts. Say **"I have an idea"** and describe it the way you would to a friend - the OS answers with the real next step (usually: which five people to talk to this week), not a business plan or a course.

---

## Status

Version 1.48.1. Public release. 93 skills, 44 commands, 788 tests. Every push to main runs three CI gates (doc and install parity, the privacy guardian, the LinkedIn pack acceptance suite) and a weekly integrity audit runs on top. The maintainer's full test suite runs upstream before anything lands here; it is not shipped in this repo, so the badge row above is the claim you can verify.

v1.48.0 is the arrival release, and the thought process behind it is one sentence: we watched how people actually arrive, and the OS assumed someone they are not. It assumed a founder with a business, a terminal, and no history. Real arrivals are a student with an idea and a phone, an operator who wants a team of assistants for her own creative process, a founder with years of notes in Obsidian, someone coming back after five weeks away. Each got a door. Download-extract-double-click: `Start Founder OS` files for Windows and Mac open Claude Code in the folder and start the wizard talking - the standing front door, honest in-file about what they cannot do. "I have an idea" now reaches the propose engine, which answers with the five real people to talk to this week, never a business plan or a course. "Turn my process into assistants" builds a team the way a real operator specced it: one job per assistant, the human keeps the taste decisions, effectiveness before efficiency, seats earned then registered. Setup adopts an existing vault without touching a single file, and says honestly what old notes can and cannot do. `AGENTS.md` now tells any connected agent - an SEO engine, an outreach drafter - how to join the team under a charter instead of freelancing in your files. The brief welcomes a returner back with counts and one offer instead of a wall of flags. And people research in meeting prep carries sources inline or says "unverified - confirm on the call", with a same-name check before anything is attributed to the human across the table.

v1.47.0 is the fourth-pass patch: an independent end-to-end review ran over the pushed v1.45.0 and the confirmed findings shipped as this patch. The blockers first. The standalone uninstaller kept a preserve-list that had fallen behind the layer model and could delete an operator's registry, quarantine record, rules, and brand config - both uninstallers now delete only named system paths, so an unknown folder survives by construction, and purge finally removes everything it claims to. The natively discoverable skills never reached `.claude/skills/` on a fresh extract - setup now runs the apply step and proves it clean. And every sentence that called a role's tool list "enforced" now says what Claude Code documents: the list is pre-approval, the boundary is a written contract audited in both directions, and anything outside a grant routes through your own permission prompts. Around those: the charter audit reads every frontmatter shape and catches interpreter-wide wildcards, impossible calendar dates fail the entry guard, future-dated verdicts stop triggering reviews, a ZIP install on a machine that happens to have git now asks before turning history on, the wizard's timestamps no longer require a Unix shell, a completed review with nothing to change still clears its due flag, and this README's offer and offline proofs were corrected to what the commands and the wizard actually do.

v1.45.0 is the wider-door release, and it opens two doors, then holds the boundary behind both. A third-pass architecture review before the push closed the charter seam: every role's declared tool list now matches its written charter, the charter audit names any drift between the two, uninstall can no longer delete what update protects, and the review loop that turns gated roles into a track record now has real daily and weekly triggers. The first is for the person who will never run git: the OS already ran without it, but the words had not caught up - a rules file installed a push cadence onto machines with no git, the tour said "your repo is your memory", and one doc claimed updates need `git pull`. All of it now speaks plainly: your files are the memory and they persist the moment they are written, saves and versions replace commit language everywhere a user reads, updates work over plain download on every path, and the install doc names in one place which folders are yours, which are the OS's, and which an update proposes changes to instead of writing. The second door is for the employee a workstream lands on. The wizard already asked whether you own the business or run a role inside one, and the answer finally leads somewhere: operators get a Role Snapshot - the part of the job you run, who you answer to, what is yours to own, what is not yours to decide, and the blocker - the propose engine gained an operator path aimed at the work you own, the account manager drafts the status update to whoever you answer to, and every line of copy that read false to a non-founder was fixed in place. One product, one track, wider door.

v1.44.0 is the usability release. A group stress-tested the product and named the risk in one line: the backend is not the problem, someone who did not build it being unable to drive it is. So setup now ends by introducing five named roles and what each will give you tomorrow morning, rather than by showing you a folder. Every role is backed by a skill on your disk and every one starts gated, because a chart claiming a track record it does not have is the thing worth avoiding. Around that: an autonomy ramp with real dates you can read and overrule, a written answer to how this differs from using Claude well, a generated page listing what the install can actually do, two commit guards for the failures that stay invisible until they are expensive, and seven scripts that had been in the repo since earlier releases without ever reaching an install.

v1.43.0 is the harness release. The headline: an update no longer costs you your own edits. The update command walks each release's packs with you, works out what the release actually changed versus what you edited, and proposes that difference on top of your version - one file, one diff, one yes, never a batch. On a genuine conflict it puts your file back and applies nothing until you choose, because a refused update is a working install and a silently merged one might not be. A new `os-config.yaml` records which parts of the OS you actually run, so updates skip what you never adopted, and holds your document font and author name so the ship gate reads them instead of guessing. Around that: four doctrine files on how the OS stays maintainable as it grows (the standing rule stated plainly - it proposes, you decide), a morning loop of at most four questions whose answers land in the files that own them and close the thing that raised them, a founder review that scores you rather than your work from your own files, and four new scripts - all standard library, nothing to pip install, no key.

v1.42.1 is the clean-machine patch: what a full end-to-end install test on a pristine machine surfaced, fixed. The blocker first: setup used to offer the founder's own name as a privacy-guard pattern, then track their identity file - so the guard it had just installed blocked setup's own commit and every later save that touched their name. The guard now protects names that should never enter your files (a client under NDA), never your own, and a mangled pattern warns out loud instead of silently matching nothing. Hooks got sturdier before setup ever runs: each hook command now tries all three Python spellings, so the session brief fires on a fresh extract on macOS boxes with only python3 and Windows boxes with only the py launcher. The save-before-you-forget instruction now reaches the model through Claude Code's supported hook channel instead of a print nothing reads. And a set of smaller honesty fixes: the in-place install no longer overwrites the private-tag exclusion rules, git authorship is confirmed rather than assumed on shared machines, session tools never read a parallel session's change log, Facebook counts as a main channel, accounting software gets a real field in the stack instead of a note nothing reads, and the voice gate points at the interview that actually fills it.

v1.42.0 is the install-and-honesty patch. The headline sits under the hood: every hook now runs through one cross-platform Python dispatcher instead of a bash script paired with a PowerShell script. A Windows box with no bash, or a Linux box with no PowerShell, used to print an interpreter-not-found error on every session event - now there is no shell to be missing, and the session-close handlers run in a fixed order, so the change manifest and the revenue check always read the tree before the auto-save commits it. The install path caught up with the ZIP the README already leads with: a ZIP extract is now detected as its own install and set up in place, git identity is set before the first commit instead of after, and the Python check runs before the interview instead of twenty minutes into it. Updates stopped overwriting what you wrote: your CLAUDE.md, rules, and settings are proposed as a migration you can read and accept, not replaced wholesale, and rollback now restores the real pre-update state instead of leaving a partial mix. And a pass over the copy made the claims match the code: the revenue-loop check actually fires now (it reads the session-change record instead of a git status that was always empty on a fresh install), the undo manifest only offers a restore for files it can truly put back, the PreCompact line says what the hook really does, and the README no longer says nothing leaves your machine without the plain version - files stay on your disk, what you read into a session goes to Anthropic under your plan terms, and ARCAS receives nothing, runs no server, keeps no telemetry. The health check got stricter with it: verify now fails a data folder whose engine is missing, syntax-checks every shipped script including the new dispatcher, and checks all six hook events instead of one. Same floor as always: one Claude plan, no key, nothing to pip install - with one named exception: the optional scrape helper asks for three packages and falls back to the built-in fetcher when they are absent; every other shipped script is standard library only.

v1.41 is the proof patch on the Second Brain release. Setup now ends by running its own health check automatically and reading the result back to you, so you never leave on trust that the wiring landed - a partial install shows up in the last minute of setup instead of days later mid-task. And session one now closes with your first real proposal run in the flow: the OS reads the snapshot it just wrote and names your single next move toward a paying customer, with the plain statement of how it compounds - every session feeds the brain, so the moves sharpen because they are read from your real state, not guessed. (v1.41.1 removed a rendered HTML card that shipped hours earlier in v1.41.0: an artifact you have to open somewhere else adds friction instead of removing it, and the in-flow proposal plus the growing brain files are the real proof. It also names git as the recommended steady state: the ZIP gets you in, and one yes later the OS installs git for you - after which updates and history maintain themselves.) Same floor: one Claude plan, no key, your files stay on your disk - reading them into a session sends them to Anthropic under your plan terms, and ARCAS receives nothing, runs no server, keeps no telemetry.

v1.40.1 is the Second Brain release's second wave: memory and money. A PreCompact hook fires before the context is compacted: it asks the summary to keep every unwritten session fact and tells the assistant to write those facts into the brain files right after, so nothing load-bearing dies in a summary. The hook hands that instruction to the session through Claude Code's hook context channel; it does not write the files itself. Boot got cheaper on grown installs - the OS orients from a compact snapshot and opens the full files only when the task needs them. A housekeeping sweep keeps a months-old brain honest: one screen of accumulated debt with a fix command per line, and a supervised fix mode for the reversible half. And the OS now knows how your business makes money - a business-model axis captured at setup drives which numbers lead in every money conversation, with a plainly stated honesty rule for regulated and deep-tech operators: accounting math yes, invented domain assumptions never.

v1.40.0 is the Second Brain release. It attacks the distance between you and owning the system. Install is now three steps and nothing typed: download the ZIP, extract, say "set up Founder OS" - git is gone from the prerequisites, and when you want full version history the OS installs and wires git itself on one consent-gated yes ("own my history"). Until then a pre-git undo floor covers you: every file the OS edits through its editing tools is snapshotted before the write, and "what did you change" returns the per-session manifest with a one-command restore for each snapshotted file (files over 2 MB are listed without a restore; a file a shell command writes directly is outside the net). Capture now works away from the laptop: drop phone dictations, voice-note exports, or pasted saved-messages piles anywhere they can land as text, say "catch up", and the OS files them into the brain through a self-teaching names glossary that corrects known mis-hearings and never guesses unknown ones. The local-first security story is now written down with the 2026 record as the counterfactual (docs/why-local-first.md), and CI gained a hooks-parity gate so every hook provably ships for both bash and PowerShell.

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
