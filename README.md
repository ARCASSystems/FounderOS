# Founder OS

The operating layer for the person running the business. Six files run your company. Claude reads them every session.

Owned by you. Runs locally in Claude Code. Talk to it.

**Setup ladder (40 min total, do in this order):**

1. **Install** - pick an [install path](#install) below (5 min). Run `./scripts/install-git-hooks.sh` to activate the privacy pre-commit hook (operator-only).
2. **Say "set up Founder OS"** (or run `/founder-os:setup`) - the wizard builds your operating layer from your answers (15 min)
3. **Say "set up my voice profile"** (or run `/founder-os:voice-interview`) - so every writing skill sounds like you, not Claude (10 min)
4. **Say "set up my brand profile"** (or run `/founder-os:brand-interview`) - so every deliverable looks like you (10 min)

After that, `/founder-os:status` audits the OS anytime, `/today` gives a one-screen view of today, and `/next` recommends one action. Full first-day path in [docs/first-day.md](docs/first-day.md). Full per-command reference in [docs/commands.md](docs/commands.md). Full per-skill reference (outcome, reads, writes, voice rules, prereqs, follow-ups) in [docs/skills.md](docs/skills.md).

> **Path B users (manual git clone):** drop the `/founder-os:` prefix. Commands are bare names: `/setup`, `/voice-interview`, `/brand-interview`, `/today`, etc. The plugin namespace only activates on Path A. See [docs/install.md](docs/install.md) for the exact commands per path.

---

## What you actually get

Three layers, in plain English. Skills read and write across all of them.

- **Operating files** - priorities, clients, decisions, today, weekly. The state of the business right now.
- **Brain layer** - log, flags, patterns, parked decisions, rants, knowledge. The memory that captures what happened, what is stuck, and what is worth reusing.
- **Wiki layer** - `[[cross-references]]` between files plus a source archive (`raw/`) for articles, transcripts, and anything you want preserved.

Areas for searching across the 45 skills:

- **Daily ops:** today, weekly-review, priority-triage, brain-log, decision-framework, session-handoff, meeting-prep, knowledge-capture, founder-coaching, unit-economics, strategic-analysis, pre-send-check, sop-writer, forcing-questions, blind-spot-review, ship-deliverable
- **Voice and brand:** voice-interview, brand-interview, your-voice, your-deliverable-template
- **Voice-coupled writers:** linkedin-post, client-update, proposal-writer, email-drafter, content-repurposer
- **Setup and audit:** founder-os-setup, readiness-check, business-context-loader, query, audit
- **Wiki and safety layer:** ingest, lint, wiki-build, approval-gates, handoff-protocol, context-persistence, data-security, bottleneck-diagnostic
- **As-needed (not daily, high value when needed):** legal-compliance

**Four roles as behavioural modes:** COO (default), BD, CMO, Chief of Staff. Claude switches mode based on what you are actually doing.

A **SessionStart brief** runs on every Claude Code session open and surfaces stalls, stale cadence, and items past their decay date in one screen. Background plumbing the wizard sets up. You do not need to think about it. The brief, the Stop hook, and slash commands are Claude Code-only - on Cowork or Cloud Claude they do not fire. Details under [Substrate details](#substrate-details) below if curious. Surface-by-surface compatibility table in [docs/tools-and-mcps.md](docs/tools-and-mcps.md).

**The legal layer (as-needed, not daily).** Most founders won't open this every day. But when a question lands - "can I let someone go", "what's our VAT obligation", "is this NDA enforceable", or you have a meeting with a lawyer next week and need to ask the right questions - the OS already knows your jurisdiction, holds the gazetted source documents, and surfaces compliance deadlines on its own. UAE founders get a full reference set out of the box (10 domain files covering company formation, employment, tax, visas, contracts, IP, data protection, dispute resolution, and industry permits, with 27 primary government sources tracked for freshness). Founders elsewhere run `/founder-os:legal-setup`, name their jurisdiction, and load their own gazetted sources via `/founder-os:legal-add-source <url-or-pdf>`. The skill never invents law - it quotes from sources you've loaded and tells you when a source is missing. SessionStart surfaces anything in `context/compliance.md` that's overdue or due within 30 days, so a license renewal, VAT return, or visa expiry doesn't slip past you. Details below under [Legal layer](#legal-layer).

**The capture-and-cite loop.** `/rant` qualifies a raw thought dump with one question, then routes it to a decision, draft, plan, log, or capture path. `/dream` distils captured rants into patterns, flags, parked decisions, and needs. Every new brain entry gets a stable `<channel>-YYYY-MM-DD-NNN` ID stamped at write time. The dream digest cites those IDs in one line each instead of restating content. `knowledge-capture` writes distilled takeaways from books, calls, and articles into `brain/knowledge/` with the same ID convention so proposal-writer and strategic-analysis can read them back. Optional: opt in to a tool-call observation log with `FOUNDER_OS_OBSERVATIONS=1` and `/dream` rolls each day's activity into an OBSERVED section.

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
- Notion duplication template (not shipped in v1.22; community forks welcome)
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
- Escalation level on every response: 🟢 confident / 🟡 confirm with a lawyer / 🔴 lawyer required
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

## Who this is for

You run the business or run a P&L inside one. Owner, operator, agency lead, consultancy head, head of department. If the buck stops with you, this is for you.

You are sharp but your day is chopped into thirty-minute pieces. You have tried productivity templates that promised the world and quietly stopped getting opened by week three.

You are not installing a template. You are installing an operating layer. It listens, routes, forgets nothing, and pushes back when you are about to ship something half-baked.

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

## What makes this different

- **Stall detection built in.** The system watches for rolling items and forces keep/kill/escalate decisions. Every retro.
- **Revenue loop enforcement.** Every outreach or content action must log same-session. Catches the gap between "I'll do X" and "I did X."
- **Role as router.** COO, BD, CMO, Chief of Staff are behavioural modes, not personas. The right mode activates based on what you are actually doing.
- **Plan A defines Plan B.** This product is a derivative of an actual founder's daily use. Features graduate from personal use into the product only after surviving contact with live P&L.
- **Talk to it.** Built around dictation. Claude Code's built-in dictation is the primary input. Wispr Flow is an optional power-user upgrade. Claude Code is desktop-only today. There is no native mobile execution surface.
- **Decay-driven keep/kill.** Set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires. The OS does not auto-kill, you decide.

---

## Cloud Claude (web, desktop, mobile)

The Notion Starter Kit was scoped but not shipped in v1.22; community forks welcome. The system prompt at [`notion-package/system-prompts/founder-os-project-prompt.md`](notion-package/system-prompts/founder-os-project-prompt.md) is available for preview and testing only. Use the Claude Code path for the full setup experience.

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

Version 1.23.0. Final release. Public push week of 2026-05-15.

v1.23 closes the central promise from v1.22. A new UserPromptSubmit hook now classifies every prompt against four shapes - rant, named-entity near a meeting verb, status update, preference utterance - and emits a capture suggestion Claude honors before responding. Rants are eagerly written to `brain/rants/<date>.md` so the text is safe on disk even if you walk away mid-thought. SessionStart prints a welcome banner on fresh installs missing `core/identity.md`, surfaces unprocessed-rant count, and nudges `/dream` when rants accumulate. Five operator-vocabulary phrases ("journal", "schedule", "goals", "customers", "I decided") route into the right skill without you knowing the OS-internal name. Named-entity detection filters common title-case nouns and requires the candidate to sit within 80 characters of the meeting verb, so prompts like "I just called Python from my bash script" do not falsely fire. v1.22's full feature set is intact: three-role setup wizard, `<private>` exclusion tag, weekly observation rollup, end-to-end critical path tests. 45 skills, 27 commands, 297 tests.

v1.21 closes the gap on what FounderOS shows. A new execution queue (`cadence/queue.md`) surfaces
what is moving in the first three lines of every session. The queue skill manages five operations -
read, add, start, done, park - and enforces a 3-item ACTIVE cap that forces a keep/kill decision
before a fourth thing starts. The queue rolls into the weekly review automatically. A new verify
skill runs a read-only health check across 8 substrate points (hooks, scripts, wiki integrity,
cadence freshness, free-tier floor, MCP state, plugin surface, auto-memory) so founders can see
substrate state without reading individual files. Five writing skills (email-drafter, sop-writer,
content-repurposer, client-update, proposal-writer) now read `brain/.snapshot.md` at task time,
completing the snapshot-consumer wiring started in v1.10. A multi-archetype trace pass against two
non-founder-shaped personas (Maya, B2C meditation app; Dev, ops-not-founder) surfaced 5 gaps, 1
patched in v1.21 (weekly-review balance check now skips for non-owner operators). 44 skills, 26
commands, 182 tests.

v1.20.3 deepens the voice profile with anti-examples. The voice interview now asks for contrarian takes, aesthetic crimes, red flags, and 3 to 6 BAD/GOOD writing pairs. The profile stores those under `voice.anti_examples`, and the five voice-coupled writing skills run a final filter that scans for the user's rejected patterns before returning a draft. Trace files show the Marcus pre/post LinkedIn pass on a topic with no prior buyer phrase.

v1.20.2 closes the intake-to-output loop. The setup wizard now captures positioning, the voice interview captures buyer language, and the brand interview records existing visual proof so first drafts have the buyer, offer, pain, and brand references they need. `/rant` now asks one qualifying question and routes to a decision, draft, plan, log, or capture path instead of always writing a dump. The writing skills stop when voice data is empty instead of quietly drafting from defaults. The README setup ladder is natural-language-first, `skills/today` covers "what's on for today?", and SessionStart Tip detection now counts explicit action tags instead of planning mentions.

v1.20.1 closes Codex CTO findings against v1.20.0. Real fixes, not cosmetic. The menu skill now has an actual engine: `scripts/menu.py` reads state and scores capabilities deterministically instead of asking the model to do it inline. The SessionStart Tip line no longer surfaces on a fresh install with no log history. The setup wizard now has test coverage for the 4 + 4 multi-choice tool-stack and work-style prompts. Skill count corrected from 39 to 40 across README, manifests, ROADMAP, CHANGELOG, and `skills/index.md` (the v1.20.0 release added the `menu` skill but the docs never caught up). 56 tests still pass plus new coverage for menu engine, tip gate, and wizard MC structure.

v1.20.0 is the discoverability release. FounderOS now routes on natural language. Slash commands stayed but became parenthetical shortcuts. Every command and skill description leads with the natural-language phrasing the founder would actually say in chat. A new `/founder-os:menu` (say "show me what you can do") returns 5 to 7 capability suggestions tailored to your current state, scored against `brain/.snapshot.md`, this week's commitments, the last 7 days of `brain/log.md`, and the presence of voice and brand profiles. README adds a third "Or say…" column to the slash command table and a new "How to use it - talk to Claude" section near the top. The release also closes two pass-1 findings deferred from v1.19.6: `scripts/query.py` now returns a no-positive-match block instead of graph-popular junk on a zero-score query, includes rants when the question contains "rant", "dump", "avoidance", "vent", or "raw", and applies stop-word filtering, light stemming, and a recency bonus; the setup wizard's tool-stack and work-style questions are now 4 + 4 short multi-choice prompts instead of two long open-ended walls. 21 commands now (added `menu`). 56 tests still pass plus new tests for menu, tip, query scoring, and the MC wizard.

v1.19.6 was a hotfix from a two-pass external review. Three things closed. The setup wizard's final orientation now detects whether the user installed via Path A (plugin namespace) or Path B (manual git clone) and renders the right command form for the path they used. Before this patch, a Path B user reading the post-setup checklist would have hit "command not found" on every namespaced command. The same review found a self-introduced prefix rendering bug that would have rendered Path B commands without a leading slash; fixed in the same release. Separately, the README's SessionStart claim was qualified to "every Claude Code session open" (it does not fire on Cowork or Cloud Claude), a Path D Cowork section was added to the README, and `docs/install.md` gained a full Cowork mode setup recipe plus `/today` and `/next` in the After-install checklist. Finally, the orientation tone across the wizard and install doc was flipped from slash-command-led to natural-language-led: real users do not memorize a 20-command surface, and Cowork mode does not fire slash commands at all, so the orientation now leads with "say 'set up my voice profile'" and treats slash commands as parenthetical shortcuts. No script changes; 56 tests still pass.

v1.19.5 was a maintainability cleanup. The v1.19.4 narrative described the parser as using a "single shared helper" for both flat and nested quoted-value handling, but the nested branch still had the unescape logic inlined. Behavior was identical, but the duplication was a future-drift trap of the same kind that produced earlier review findings. The nested branch now routes through the same `unquote()` helper. No behavior change; 56 tests still pass.

v1.19.4 closes one follow-up from a fifth review pass. The quote-aware unescape introduced in v1.19.2 and narrowed in v1.19.3 was only applied to the nested `wiki_links:` list path. The flat curated path (`source: "..."` / `target: "..."` / `from: '...'` / `to: '...'`) was still using the older "strip outer quotes only" logic, so a flat double-quoted value with an inner `\"` parsed as `foo\"bar` instead of `foo"bar`. Both paths now share a single `unquote` helper that strips outer quotes and reverses only the matching escape. Three new tests cover the flat-path round-trip in both quote shapes plus the literal-backslash preservation case. 39 skills, 20 commands, 56 tests.

v1.19.3 closes two follow-ups from a fourth review pass. The v1.19.2 escape-unescape fix was applied symmetrically to both quote characters, which over-applied: a hand-written single-quoted YAML target like `'foo\"bar'` would have parsed as `foo"bar`, losing the literal backslash that belongs to the user's content. The unescape is now quote-char-aware (only `\"` inside `"..."`, only `\'` inside `'...'`). And the ROADMAP `v1.19.0` shipped bullet still summarised "Six fixes" and credited v1.19.0 with the `WSLENV/p` fix; CHANGELOG and README had been corrected, ROADMAP had not. Now matches. One new test locks the single-quote round-trip in. 39 skills, 20 commands, 53 tests.

v1.19.2 closes three follow-ups from a third review pass. The v1.19.1 narrative reintroduced the previous reviewer's tool name while explaining its earlier removal (cleaned up). The v1.19.0 narrative still summarised the WSL fix as if it had landed in v1.19.0 (it didn't fully land until v1.19.1, now reflected). And `parse_edges()` was reading `\"` literally inside a quoted target instead of unescaping it back to `"` (the wiki-build serializer escapes the quote on output, so the round-trip was asymmetric for any target containing a literal double-quote). One new test covers the escape round-trip. 39 skills, 20 commands, 52 tests.

v1.19.1 is a follow-up patch from a second review pass over v1.19.0. Four real fixes: the WSL test path-conversion hardened (the v1.19 fallback returned the cwd `.` because `TARGET_PATH` did not propagate into WSL bash without `WSLENV/p`; the probe now sets `WSLENV` and validates the result), `candidate_files()` now walks every prefix in `INCLUDE_PREFIXES` so cadence files, `context/clients.md`, and `core/*.md` can surface as query results (the v1.19 widening only added `roles/` and `rules/`), `parse_edges()` keeps quoted targets that happen to start with `source:` / `target:` (the new state machine was treating them as record boundaries and dropping the edge), and parked-decision decay prose now matches the hook's actual behavior (the hook does not evaluate trigger conditions; parked decisions surface manually during the Chief of Staff scan unless the operator sets an explicit `Decay after:` line). Also: tool-branding attribution removed from the v1.19 narrative per `rules/commit-naming.md:11`. Three new tests cover the quoted-target edge case and the wider candidate scope. 39 skills, 20 commands, 51 tests.

v1.19.0 closes an external review pass on v1.15.0. Five user-visible fixes plus an attempted WSL bash test fix that did not fully land. Search now reads the wiki connections you build between files (the parser was silently dropping every auto-generated edge during traversal). Search now covers your role and rule files (v1.14 added them to the wiki graph; this release catches up the search side). Fresh installs run clean again (lint stopped flagging the seeded parked-decisions example as a "stale entry" warning). The manual-clone install gets correct command guidance on Day 1 (`docs/first-day.md` now carries a Path B note at the top; before, you would hit "command not found" on the first command). And the plugin marketplace shows the right version (the manifests had been stamped at v1.13.0 since that release, even after v1.14-v1.18 shipped). The WSL test path conversion got an attempted fix (a `wslpath` probe added on top of `cygpath`) but the path argument did not propagate into WSL bash, so the probe still returned the cwd and the suite still failed there; v1.19.1 closes the gap with `WSLENV/p` and result validation. Plus three smaller doc-and-surface fixes. Five new tests cover the search/wiki connection logic. 39 skills, 20 commands, 48 tests.

v1.18.0 closes the third layer of doc drift. v1.16 caught the root-level docs and v1.17 caught the first-day/bootloader inventory. v1.18 catches the per-skill and per-command reference docs (`docs/skills.md` and `docs/commands.md`), which described the lint outcome with the pre-v1.15 surface (no decay-gap, no log-cap, ambiguous slugs only listed candidates instead of naming the deterministic pick). Both reference files now describe what `/founder-os:lint` actually prints. No code changes. 39 skills, 20 commands, 43 tests.

v1.17.0 closes the second layer of doc drift caught in the v1.16 sync. `docs/first-day.md` had a "What SessionStart shows you (v1.4)" section listing the brief's surfaces - the inventory was frozen at v1.4 and missed two items added since: the `clients/<slug>/` auto-memory diff (v1.12) and the `Observations:` line (v1.15). `templates/bootloader-claude-md.md` (the file every fresh `/founder-os:setup` writes as the user's CLAUDE.md) had the same stale inventory. A new user reading first-day.md or their newly-installed CLAUDE.md would see fewer brief surfaces than the hooks actually print. Both files now name all nine surfaces. No code changes. 39 skills, 20 commands, 43 tests.

v1.16.0 is the docs-sync release. README, ROADMAP, CLAUDE.md, and AGENTS.md were claiming v1.13 surface state after v1.14 and v1.15 had already shipped. New users cloning the repo would see version drift in the first thirty seconds. v1.16 catches the docs up: README "Production" stamp now reads v1.16.0, the Status section names v1.14 + v1.15 prose, ROADMAP Shipped list extends to v1.15, and the SessionStart-brief inventory in CLAUDE.md and AGENTS.md names the new `Observations:` line. No code changes. 39 skills, 20 commands, 43 tests.

v1.15.0 is the wiki-hardening Phase 2 release. After v1.14 closed four wiki-integrity issues, the same audit surfaced five more places where the OS quietly degrades without telling the user. Lint now flags entries that lack `Decay after:` (silent decay miss across flags, patterns, and parked decisions), `brain/log.md` past its 300-line cap, and names the deterministic pick on ambiguous bare slugs (resolution order is `INCLUDE_PREFIXES` then alphabetical, first match wins). SessionStart brief now surfaces `FOUNDER_OS_OBSERVATIONS` state on every open so the silent-disable case is visible. `docs/tools-and-mcps.md` Obsidian section names the day-0 empty-graph expectation and the bare-slug ambiguity rule. 39 skills, 20 commands, 43 tests. No script changes; lint and doc surfaces only.

v1.14.0 is the wiki integrity release. An audit prompted by an Obsidian-vault user question surfaced four issues that quietly degrade the memory and operational layer: cross-references inside `roles/` and `rules/` were silently dropped from `brain/relations.yaml`, `[[file]]` and `[[file.md]]` produced two unrelated graph nodes, lint flagged most seeded root files as orphans on a fresh install, and one stale-content rule named a field that no template uses. All four closed. 39 skills, 20 commands, 43 tests. No new skills, no new commands.

v1.13.0 is the install-ergonomics and hardening release. A full audit caught a handful of walls a first-time user would hit cold from the README. Path B told users to run `/founder-os:setup` when the bare command for a manual clone is `/setup`. Path A had no signal that `/reload-plugins` is sometimes needed before the namespace activates. `CLAUDE.md` referenced a `/loop weekly` command and a `skill-creator` skill that do not ship. The v1.12 memory-diff hook used `python` only and silently no-op'd on macOS PowerShell. The setup wizard was shipping the un-refactored template copy of `wiki-build.py` over the fixed one. `/founder-os:query` interpolated user input into a shell line, which would execute `;`, `|`, backticks, and `$(...)`. v1.13 closes all of those, plus a set of cross-platform fixes in the audit scripts, the bash hook, and the tests. No new skills, no new commands. 39 skills, 20 commands, 43 tests - same surface, install paths that actually work.

v1.12.0 closes a cross-session memory gap. When a cloud Claude session, a parallel local session, or a teammate creates a new `clients/<slug>/` folder with intel and prep, the next local session boots blind to it because `MEMORY.md` does not auto-populate from filesystem changes. A new helper at `scripts/memory-diff.py` (template-mirrored to `templates/scripts/memory-diff.py`) runs from the SessionStart hook on every session open. It walks `clients/<slug>/`, checks each slug against your auto-memory index and per-file `project_*.md` entries, and prints any uncovered slugs with a one-line nudge to write a memory entry. Stdlib only. Free-tier accessible. Hook-only feature - no new skill, no new command. Setup wizard now copies five Python helpers (was four) so fresh installs get the helper out of the box. 39 skills, 20 commands, 43 tests (nine new memory-diff tests) - no surface change beyond the helper itself.

v1.11.0 was the launch-hardening release. v1.10 shipped the runtime brain context, but a few install-time gaps quietly broke the marquee feature for fresh users. v1.11 closes those gaps. The setup wizard now copies all four runtime helpers (was two) so brain-snapshot and brain-pass actually work after Path A install. `/founder-os:wiki-build` now runs on a fresh clone (the script was missing). `/founder-os:update` and `/founder-os:uninstall` now cover scripts, rules, docs, and AGENTS.md (previously omitted, so updates would silently miss new code). PowerShell hooks fixed for non-English Windows locales. Bash hooks gained exit guards on path resolution. New `.gitattributes` enforces LF on shell and Python so Windows clones don't break Bash hooks with CRLF. CLAUDE.md and AGENTS.md catch up to the v1.10 surface (39 skills, 20 commands, brain-pass / brain-snapshot rows). README mobile and kill-criteria claims corrected. End-to-end audit pass on leaks, code, docs, install flow, and skill integrity. No new surface. Just the finish.

v1.10.0 was the runtime brain context release. A small deterministic snapshot (open flags, this week's must-do, recent decisions, voice and brand fields, staleness) regenerates on demand at `brain/.snapshot.md`. Nine output-producing skills (meeting-prep, weekly-review, strategic-analysis, decision-framework, founder-coaching, knowledge-capture, unit-economics, priority-triage, brain-log) read it at task time so output reflects current state instead of starting cold. A `brain-pass` skill (`/founder-os:brain-pass "<question>"`) synthesises answers across the brain layer with stable-ID citations - no embeddings, no API call, free-tier accessible. `meeting-prep` and `linkedin-post` auto-invoke brain-pass before producing output.

Full release history in [`CHANGELOG.md`](CHANGELOG.md). Current limits in [`notion-package/pages/05-current-limits.md`](notion-package/pages/05-current-limits.md).

---

## Maintenance and forking

FounderOS v1.22 was the final feature release from ARCAS Systems. v1.23 ships review-driven patches only (privacy sweeps, hook fixes, false-positive closures from final-release audits). No new skills, commands, or features land on the upstream after v1.22. The repo is in maintenance mode: critical-breakage patches only, community forks encouraged. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the issue-triage policy and [`docs/forking.md`](docs/forking.md) for extension points.

## Contributing and security

- Bugs and small fixes: open an issue or PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for what we accept and what stays in the upstream private repo.
- Security: report vulnerabilities to `solutions@arcassystems.com`. See [`SECURITY.md`](SECURITY.md) for scope and response times.

## License

MIT. Copyright (c) 2026 ARCAS Systems. See [`LICENSE`](LICENSE).

---

Built by [ARCAS Systems](https://arcassystems.com).
