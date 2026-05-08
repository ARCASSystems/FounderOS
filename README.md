# Founder OS

The operating layer for the person running the business. Six files run your company. Claude reads them every session.

Owned by you. Runs locally in Claude Code. Talk to it.

**Setup ladder (40 min total, do in this order):**

1. **Install** - pick an [install path](#install) below (5 min)
2. **`/founder-os:setup`** - the wizard builds your operating layer from your answers (15 min)
3. **`/founder-os:voice-interview`** - so every writing skill sounds like you, not Claude (10 min)
4. **`/founder-os:brand-interview`** - so every deliverable looks like you (10 min)

After that, `/founder-os:status` audits the OS anytime, `/today` gives a one-screen view of today, and `/next` recommends one action. Full first-day path in [docs/first-day.md](docs/first-day.md). Full per-command reference in [docs/commands.md](docs/commands.md). Full per-skill reference (outcome, reads, writes, voice rules, prereqs, follow-ups) in [docs/skills.md](docs/skills.md).

> **Path B users (manual git clone):** drop the `/founder-os:` prefix. Commands are bare names: `/setup`, `/voice-interview`, `/brand-interview`, `/today`, etc. The plugin namespace only activates on Path A. See [docs/install.md](docs/install.md) for the exact commands per path.

---

## What you actually get

Three layers, in plain English. Skills read and write across all of them.

- **Operating files** - priorities, clients, decisions, today, weekly. The state of the business right now.
- **Brain layer** - log, flags, patterns, parked decisions, rants, knowledge. The memory that captures what happened, what is stuck, and what is worth reusing.
- **Wiki layer** - `[[cross-references]]` between files plus a source archive (`raw/`) for articles, transcripts, and anything you want preserved.

Areas for searching across the 39 skills:

- **Daily ops:** weekly-review, priority-triage, brain-log, decision-framework, session-handoff, meeting-prep, knowledge-capture, founder-coaching, unit-economics, strategic-analysis, pre-send-check, sop-writer, forcing-questions, blind-spot-review, ship-deliverable
- **Voice and brand:** voice-interview, brand-interview, your-voice, your-deliverable-template
- **Voice-coupled writers:** linkedin-post, client-update, proposal-writer, email-drafter, content-repurposer
- **Setup and audit:** founder-os-setup, readiness-check, business-context-loader, query, audit
- **Wiki and safety layer:** ingest, lint, wiki-build, approval-gates, handoff-protocol, context-persistence, data-security, bottleneck-diagnostic

**Four roles as behavioural modes:** COO (default), BD, CMO, Chief of Staff. Claude switches mode based on what you are actually doing.

A **SessionStart brief** runs on every session open and surfaces stalls, stale cadence, and items past their decay date in one screen. Background plumbing the wizard sets up. You do not need to think about it. Details under [Substrate details](#substrate-details) below if curious.

**The capture-and-cite loop.** `/rant` captures a raw thought dump. `/dream` distils unprocessed rants into patterns, flags, parked decisions, and needs. Every new brain entry gets a stable `<channel>-YYYY-MM-DD-NNN` ID stamped at write time. The dream digest cites those IDs in one line each instead of restating content. `knowledge-capture` writes distilled takeaways from books, calls, and articles into `brain/knowledge/` with the same ID convention so proposal-writer and strategic-analysis can read them back. Optional: opt in to a tool-call observation log with `FOUNDER_OS_OBSERVATIONS=1` and `/dream` rolls each day's activity into an OBSERVED section.

---

## Install

Three install paths. Pick the one that matches your stack. Full details in [docs/install.md](docs/install.md).

### Path A - Claude Code plugin (cleanest)

```
/plugin marketplace add ARCASSystems/FounderOS
/plugin install founder-os@founder-os-marketplace
/founder-os:setup
```

Requires Claude Code with a Pro or Max plan. If `/founder-os:setup` is not recognised after install, run `/reload-plugins` (or restart Claude Code) so the plugin namespace activates, then try again. If the plugin install still does not work, fall back to Path B.

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
/setup
```

> Path B uses bare command names (`/setup`, `/today`, etc.) because the plugin namespace only activates on Path A. See [docs/install.md](docs/install.md) for the exact mapping.

The setup wizard walks through about 15 to 20 prompts across six phases (identity, business, priorities, voice/brand seed, tool stack, file generation) and generates your full operating system locally. 15 to 20 minutes the first time.

### Path C - Cloud Claude (read-only)

Open Claude.ai, attach this repo's README and CLAUDE.md as Project context, and use the safe fallback prompt below. Cloud Claude cannot run slash commands or write to local disk - it's a read-only operating mode until the Notion Starter Kit ships. See [docs/install.md](docs/install.md) for the full instructions.

---

## What ships in this repo

### Skills (39)

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
| forcing-questions | Six yes/no answers and a verdict on whether to start, kill, or postpone the initiative. Catches vague done states, phantom users, scope creep, false urgency. Read-only. |
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

### Slash commands (20)

Each row tells you the **outcome** (what you see when it finishes) and whether it **writes** anything. Detailed behaviour, sample output, args, and follow-ups live in [`docs/commands.md`](docs/commands.md).

| Command | What you get |
|---|---|
| `/founder-os:setup` | A guided interview that ends with your full operating layer on disk: identity, priorities, decisions, clients, daily anchor, weekly commitments, brain log, flags. Writes 8+ files under `core/`, `context/`, `cadence/`, `brain/`. 15 min. |
| `/founder-os:voice-interview` | A `core/voice-profile.yml` that captures how you actually write. Every voice-coupled writing skill (LinkedIn, email, proposal, client update) reads it on every output. 10 min. |
| `/founder-os:brand-interview` | A `core/brand-profile.yml` plus an assets folder. Every branded deliverable (proposal, deck, one-pager) inherits these colors, fonts, and logo. 10 min. |
| `/founder-os:status` | A weighted readiness score plus the next 3 high-impact moves to run right now. Read-only. |
| `/founder-os:ingest <source>` | A new file in `raw/<source>.md` with provenance frontmatter, plus proposed wiki updates you approve before they land. Writes `raw/`, optionally updates `brain/relations.yaml`. |
| `/founder-os:lint` | A list of broken `[[wikilinks]]`, orphan files, stale entries past their decay date, provenance gaps, and possible contradictions. Read-only. |
| `/founder-os:wiki-build` | A refreshed `brain/relations.yaml` graph extracted from every `[[wikilink]]` in your OS. Idempotent. Writes `brain/relations.yaml`. |
| `/founder-os:query <question>` | The top 3 to 5 OS nodes that match your question, each with a stable ID and the path that reached it. `--mode timeline --anchor <slug>` returns entries within 7 days of an anchor. `--mode full --ids <a,b,c>` returns full bodies. Read-only. |
| `/founder-os:brain-pass "<question>"` | A synthesised answer with stable-ID citations: Answer, Evidence, Confidence, Gaps. Use when a question spans multiple brain files and a keyword query is too noisy. Read-only. |
| `/founder-os:audit` | One composite health report covering readiness, wiki integrity, brain staleness, voice completeness, and quarantine state. Read-only. |
| `/founder-os:forcing-questions <initiative>` | Six yes/no answers plus a scope-creep verdict on whether to start, kill, or postpone the initiative. Read-only. |
| `/founder-os:ship-deliverable <path>` | A pass or fail verdict across template fit, anti-AI scan, blind-spot review, and pre-send checks. Names every issue. Nothing ships if anything fails. Read-only. |
| `/founder-os:update` | A diff of System Layer files (skills, templates, commands, hooks) refreshed from the latest release. Your personal data (`core/`, `context/`, `cadence/`, `brain/`) is never touched. Subcommands: `check`, `rollback`. |
| `/founder-os:uninstall` | A confirmation list of every file that will be removed, plus the actual cleanup. Default preserves your data. `--purge` removes everything. |
| `/founder-os:rant` | A new `brain/rants/<YYYY-MM-DD>.md` file holding your raw dump verbatim. No structure asked. The `/dream` command processes it later. Writes `brain/rants/`. |
| `/founder-os:dream` | A 5-line digest in `brain/log.md` plus stable-ID entries in `brain/patterns.md`, `brain/flags.md`, `brain/decisions-parked.md`, `brain/needs-input.md` as warranted. Each rant marked processed. Writes 5+ files. |
| `/today` | A 20-line one-screen view: today's anchor, top open decisions, active flags, last 3 log entries, next calendar event. Read-only. |
| `/next` | One recommended next action across priorities, deals, and cadence. Not a list, one action. Read-only. |
| `/pre-meeting <subject>` | Pass or fail on the pre-meeting gate (capture artifact present, ask defined). Logs an intent entry to `brain/log.md` on pass. |
| `/capture-meeting <subject>` | A routed summary: meeting log entry in `brain/log.md`, updated client status in `context/clients.md`, and any new open commitments. Writes 2 to 3 files. |

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

Most of the 39 skills work end-to-end with zero MCPs. A few skills, including `email-drafter`, `meeting-prep`, `knowledge-capture`, and `session-handoff`, function without MCPs but produce better output with the relevant integration connected.

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

You need shared state across a team. Founder OS is single-user. The Company OS layer (planned, not shipped) is what handles team coordination.

You want push notifications, automated triggers, or anything that fires while you sleep. Founder OS is the thinking layer. n8n, Make, Zapier, or your own scripts handle offline triggers.

You want a tool you install and forget. This is an operating layer that needs you to engage daily and review weekly. If you are not going to do that, this will sit unused like every other system.

---

## The repos

Three repos. One architecture. FounderOS is production. The siblings are in development.

| Repo | Status | For | Entry point |
|---|---|---|---|
| **FounderOS** (this repo) | Production v1.13.0 | Owners and operators running a business | [github.com/ARCASSystems/FounderOS](https://github.com/ARCASSystems/FounderOS) |
| **PersonalOS** | In development, ETA late May 2026 | Individuals - career changers, freelancers, side hustlers, learners, creators | [github.com/ARCASSystems/PersonalOS](https://github.com/ARCASSystems/PersonalOS) |
| **AgentOS** | In development, ETA June 2026 | Builders who want to ship a custom OS to a client or team | [github.com/ARCASSystems/AgentOS](https://github.com/ARCASSystems/AgentOS) |

All three are Claude Code plugins. All three are local-first. FounderOS and PersonalOS are migrations of AgentOS with personal data stripped out. If you want a polished operating layer right now, FounderOS is the one to use. The siblings are previews.

The three repos share one architecture: User OS (Layer 1) / Company OS (Layer 2) / Knowledge Base (Layer 3). FounderOS lives at Layer 1 today. PersonalOS lives at Layer 1 with a personal lens. AgentOS will be the platform a builder ships to a client or team and adds Layer 2 (Company OS) and Layer 3 (Knowledge Base) on top of Layer 1. The deeper architecture write-up will land in the AgentOS repo when AgentOS reaches public preview. Until then, FounderOS is the production layer-1 system on its own.

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
- **Talk to it.** Built around dictation. Claude Code's built-in dictation is the primary input. Wispr Flow is an optional power-user upgrade. Claude Code is desktop-only today. There is no native mobile execution surface.
- **Decay-driven keep/kill.** Set `Decay after: 14d` on a flag and the SessionStart brief surfaces it for keep/kill review when it expires. The OS does not auto-kill, you decide.

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
| Set up after install | `/founder-os:setup` (Path A) or `/setup` (Path B) |
| Check today after setup | `/today` |
| Check OS health | `/founder-os:status` |
| Update System Layer later | `/founder-os:update check` |
| Cleanly remove | `/founder-os:uninstall` |
| Business inquiry, install help, speaking | `solutions@arcassystems.com` |

---

## Status

Version 1.13.0. Public push week of 2026-05-07.

v1.13.0 is the install-ergonomics and hardening release. A full audit caught a handful of walls a first-time user would hit cold from the README. Path B told users to run `/founder-os:setup` when the bare command for a manual clone is `/setup`. Path A had no signal that `/reload-plugins` is sometimes needed before the namespace activates. `CLAUDE.md` referenced a `/loop weekly` command and a `skill-creator` skill that do not ship. The v1.12 memory-diff hook used `python` only and silently no-op'd on macOS PowerShell. The setup wizard was shipping the un-refactored template copy of `wiki-build.py` over the fixed one. `/founder-os:query` interpolated user input into a shell line, which would execute `;`, `|`, backticks, and `$(...)`. v1.13 closes all of those, plus a set of cross-platform fixes in the audit scripts, the bash hook, and the tests. No new skills, no new commands. 39 skills, 20 commands, 43 tests - same surface, install paths that actually work.

v1.12.0 closes a cross-session memory gap. When a cloud Claude session, a parallel local session, or a teammate creates a new `clients/<slug>/` folder with intel and prep, the next local session boots blind to it because `MEMORY.md` does not auto-populate from filesystem changes. A new helper at `scripts/memory-diff.py` (template-mirrored to `templates/scripts/memory-diff.py`) runs from the SessionStart hook on every session open. It walks `clients/<slug>/`, checks each slug against your auto-memory index and per-file `project_*.md` entries, and prints any uncovered slugs with a one-line nudge to write a memory entry. Stdlib only. Free-tier accessible. Hook-only feature - no new skill, no new command. Setup wizard now copies five Python helpers (was four) so fresh installs get the helper out of the box. 39 skills, 20 commands, 43 tests (nine new memory-diff tests) - no surface change beyond the helper itself.

v1.11.0 was the launch-hardening release. v1.10 shipped the runtime brain context, but a few install-time gaps quietly broke the marquee feature for fresh users. v1.11 closes those gaps. The setup wizard now copies all four runtime helpers (was two) so brain-snapshot and brain-pass actually work after Path A install. `/founder-os:wiki-build` now runs on a fresh clone (the script was missing). `/founder-os:update` and `/founder-os:uninstall` now cover scripts, rules, docs, and AGENTS.md (previously omitted, so updates would silently miss new code). PowerShell hooks fixed for non-English Windows locales. Bash hooks gained exit guards on path resolution. New `.gitattributes` enforces LF on shell and Python so Windows clones don't break Bash hooks with CRLF. CLAUDE.md and AGENTS.md catch up to the v1.10 surface (39 skills, 20 commands, brain-pass / brain-snapshot rows). README mobile and kill-criteria claims corrected. End-to-end audit pass on leaks, code, docs, install flow, and skill integrity. No new surface. Just the finish.

v1.10.0 was the runtime brain context release. A small deterministic snapshot (open flags, this week's must-do, recent decisions, voice and brand fields, staleness) regenerates on demand at `brain/.snapshot.md`. Nine output-producing skills (meeting-prep, weekly-review, strategic-analysis, decision-framework, founder-coaching, knowledge-capture, unit-economics, priority-triage, brain-log) read it at task time so output reflects current state instead of starting cold. A `brain-pass` skill (`/founder-os:brain-pass "<question>"`) synthesises answers across the brain layer with stable-ID citations - no embeddings, no API call, free-tier accessible. `meeting-prep` and `linkedin-post` auto-invoke brain-pass before producing output.

Full release history in [`CHANGELOG.md`](CHANGELOG.md). Current limits in [`notion-package/pages/05-current-limits.md`](notion-package/pages/05-current-limits.md).

---

## Contributing and security

- Bugs and small fixes: open an issue or PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for what we accept and what stays in the upstream private repo.
- Security: report vulnerabilities to `solutions@arcassystems.com`. See [`SECURITY.md`](SECURITY.md) for scope and response times.

## License

MIT. Copyright (c) 2026 ARCAS Systems. See [`LICENSE`](LICENSE).

---

Built by [Alistair Aranha](https://github.com/ARCASSystems) at [ARCAS Systems](https://arcassystems.com).
