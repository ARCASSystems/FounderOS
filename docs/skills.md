# Founder OS Skills Reference

> Long-form mirror of the canonical registry in [`../skills/index.md`](../skills/index.md). That registry is the single source for the skill list and the counts; this file expands each skill into the eight labels below. If the two ever disagree, `skills/index.md` wins - update it first, then mirror the change here.

The full reference for every skill. The registry in [`../skills/index.md`](../skills/index.md) names the **outcome** in one line; this file tells you everything else: how to invoke each skill in plain English, what it reads, what it writes, whether it inherits your voice, what must exist before it works, and what to run after.

**You do not memorize commands. You talk to Claude.** Most skills auto-trigger from natural-language phrases like "set up my voice profile" or "what should I focus on next." The slash command appears at the end of each entry as an optional shortcut, not the primary way in. The new `/founder-os:menu` (or "show me what FounderOS can do") returns a tailored shortlist when you don't know what to ask for.

Each skill has eight labels.

- **Say.** The natural-language phrase that triggers the skill. Lead with this.
- **Outcome.** What appears in chat or on disk after the skill finishes.
- **Reads.** OS files the skill consumes for context.
- **Writes.** Files created or updated. `Read-only` if nothing.
- **Voice rules.** Whether `core/voice-profile.yml` shapes the output.
- **Prereqs.** What must already exist for the skill to work.
- **When to run.** The signal that makes this skill the right next move.
- **Follow-up.** What to run after.

If a skill has a slash command that wraps it, that command is named at the end as a shortcut. See [`docs/commands.md`](commands.md) for the command-side reference.

---

## Version control (invisible git)

### save

- **Say.** "save my work", "save this", "save my progress", or "checkpoint this".
- **Outcome.** Your current work is recorded as a new version. The OS stages every changed file by path and commits locally. You see what was saved in plain language.
- **Reads.** `git status` for the changed files.
- **Writes.** A local git commit. Never pushes.
- **Voice rules.** No.
- **Prereqs.** Founder OS set up. `scripts/caveman_git.py` present.
- **When to run.** Any time you want a restore point, and often. The auto-save hook also saves at session end once your name guard is active.
- **Follow-up.** `history` to see versions, `restore` to undo. Say "save my work".

### history

- **Say.** "what changed", "show my history", "version history", or "what did I save".
- **Outcome.** Your saved versions as readable dated events, newest first, grouped by day. No SHAs.
- **Reads.** The git log.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** Founder OS set up. Handles a fresh repo with nothing saved yet.
- **When to run.** Before an undo, or to confirm your work is being saved.
- **Follow-up.** `restore` to undo to one of the versions. Say "what changed".

### restore

- **Say.** "undo to before this morning", "restore to yesterday", "roll back", or "go back to last week".
- **Outcome.** Your OS is returned to an earlier version, non-destructively. It safety-saves your current work first, aborts if that save is blocked, and records the undo as a new version so it is itself reversible.
- **Reads.** The git log and the target version.
- **Writes.** A safety commit, then a new commit recording the undo. Never rewrites history, never `git reset --hard`, never loses work.
- **Voice rules.** No.
- **Prereqs.** Founder OS set up. At least one saved version to return to.
- **When to run.** When you want to undo a session, a day, or a stretch of changes.
- **Follow-up.** `history` to confirm the prior state is still recoverable. Say "undo to ...".

### backup

- **Say.** "back this up", "back up my OS", "set up a backup", or "mirror this offsite".
- **Outcome.** An offsite copy of your OS, to a destination you choose: GitHub (recommended), OneDrive, Notion (reference mirror only), or stay local. On command only.
- **Reads.** Your OS folder and git state.
- **Writes.** Depends on the destination. The GitHub path reuses `github-ops` to create a private repo you own and push. Never force-pushes, never without your yes.
- **Voice rules.** No.
- **Prereqs.** Founder OS set up. For GitHub, the `gh` CLI authenticated.
- **When to run.** After a big session, once you have picked a backup destination. Optional: local version control works fully without it.
- **Follow-up.** Re-run after future sessions to keep the offsite copy current. Say "back this up".

### own-your-history

- **Say.** "own my history", "turn on version history", "turn on full history", or "install git".
- **Outcome.** A git-less install (usually the ZIP path) graduates to full version history: with your explicit yes, the OS installs git itself, turns the folder into a repository, wires the privacy guard before the first commit, and records version one. You never type a git command.
- **Reads.** `core/identity.md` for the history identity; the install's git state.
- **Writes.** The git install (consent-gated, exact command shown first), `git init`, local git config, the first commit.
- **Voice rules.** No.
- **Prereqs.** Founder OS set up. Only does anything when version history is off.
- **When to run.** Once the OS has proven useful - usually week one. Until then, session snapshots cover undo.
- **Follow-up.** `save`, `history`, and `restore` now run at full power. Say "save my work" after your next session.

---

## Setup and identity

### founder-os-setup

- **Say.** "set up Founder OS", "run the setup wizard", or "install Founder OS".
- **Outcome.** A 6 to 7 question interview ends with your full operating layer on disk.
- **Reads.** `templates/` for the file scaffolds. Also reads `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, and any existing project CLAUDE.md during the audit phase.
- **Writes.** `core/identity.md`, `context/priorities.md`, `context/decisions.md`, `context/clients.md`, `context/companies.md`, `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, `brain/log.md`, `brain/flags.md`, `MEMORY.md`.
- **Voice rules.** No.
- **Prereqs.** Founder OS plugin or repo present.
- **When to run.** First session. Or when you want to redo setup with fresh answers.
- **Follow-up.** `voice-interview`, then `brand-interview`. Slash command: `/founder-os:setup`.

### voice-interview

- **Say.** "set up my voice profile", "set up my voice", or "voice interview".
- **Outcome.** A voice profile that captures rhythm, openings, closings, contractions, idiosyncrasies, buyer language, anti-examples, reading level, preferred and banned words, plus 3 reference samples.
- **Reads.** `templates/voice-profile.yml.template` for the schema. Your pasted writing samples drive the inference.
- **Writes.** `core/voice-profile.yml`.
- **Voice rules.** This is the source.
- **Prereqs.** `founder-os-setup` complete. You have 2+ writing samples ready to paste.
- **When to run.** Day 1, after setup. Or when your voice has shifted and writing skills no longer sound like you.
- **Follow-up.** `brand-interview`. Test the result with `linkedin-post` on a small idea. Slash command: `/founder-os:voice-interview`.

### brand-interview

- **Say.** "set up my brand profile", "set up my brand", or "brand interview".
- **Outcome.** A brand profile capturing colors, fonts, logo paths, existing visual proof, footer text, page size, and margins. Plus an empty `core/brand-assets/` folder ready for your logo files.
- **Reads.** `templates/brand-profile.yml.template` for the schema.
- **Writes.** `core/brand-profile.yml`, `core/brand-assets/`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Once Day 1 is otherwise stable. Skip if you do not produce branded deliverables.
- **Follow-up.** Drop your logo files into `core/brand-assets/` per the captured paths. Test with `your-deliverable-template`. Slash command: `/founder-os:brand-interview`.

### profile-router

- **Say.** "update my profile", "what should the OS lead with for me", "set my profile", or "re-detect my profile". Also runs inside the setup wizard.
- **Outcome.** A confirmed operator variant (founder, career-mover, builder, student, team-internal) written to `core/profile.md`, with the lead surfaces and frame the OS opens with for you. Nothing is locked - every skill stays available to every variant; the variant only changes what leads.
- **Reads.** `core/profile.md`, `core/identity.md`, and the setup discovery answers when run during onboarding.
- **Writes.** `core/profile.md` (variant, signals, lead surfaces, frame, technical comfort).
- **Voice rules.** No.
- **Prereqs.** None to read you at setup. Writes a fuller profile once `core/identity.md` exists.
- **When to run.** Automatically at setup. Again whenever your situation changes - a new job search, a shift from building to selling, a move from learning to shipping.
- **Follow-up.** The SessionStart brief and `menu` open with your variant's surfaces. No dedicated slash command.

---

## Discovery

### menu

- **Say.** "show me what you can do", "what can FounderOS do", "what should I try next", or "what's relevant right now".
- **Outcome.** A ranked list of 5 to 7 capabilities tailored to your current state. Each row leads with the natural-language phrase, the slash command appears parenthetically. Closes with a reminder that plain English routes most of the OS, not slash commands.
- **Reads.** `brain/.snapshot.md` if present, `brain/flags.md`, `cadence/weekly-commitments.md`, last 7 days of `brain/log.md`, `core/voice-profile.yml`, `core/brand-profile.yml`, `context/priorities.md`, `drafts/` directory.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** None. Works on a brand-new install (returns the Day-1 starter set).
- **When to run.** When you forget what to ask for. When new to FounderOS. When you want a periodic nudge on capabilities you have not used.
- **Follow-up.** Say one of the natural-language phrases the menu surfaces. Slash command: `/founder-os:menu`.

### today

- **Say.** "what's on for today?"
- **Outcome.** A 20-line one-screen view of today's anchor, open decisions, active flags, last 3 log entries, and next event.
- **Reads.** `cadence/daily-anchors.md`, `context/decisions.md`, `brain/flags.md`, `brain/log.md`.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** Founder OS setup complete.
- **When to run.** At the start of a work session, especially in Cowork mode where slash commands do not fire.
- **Follow-up.** Work the named anchor or ask "what should I focus on next?" Slash command: `/today`.

---

## Audit and health

### readiness-check

- **Say.** "check my OS readiness", "how am I doing", or "where are the gaps".
- **Outcome.** A weighted readiness score across six buckets (Core, Voice and Brand, Cadence, Business Context, Brain Layer, Queue) plus the next 3 high-impact moves. The Business Context bucket counts operator companies only (`companies/<slug>-business.md`); prospect files under `companies/prospects/` are tracked separately and not in this score.
- **Reads.** `core/identity.md`, `core/voice-profile.yml`, `core/brand-profile.yml`, `context/priorities.md`, `context/companies.md`, `cadence/`, `brain/flags.md`, `brain/log.md`, `brain/patterns.md`, `cadence/queue.md`.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Any time. Especially after a break, before a big push, or when stuck.
- **Follow-up.** Run the top recommended move. Slash command: `/founder-os:status`.

### audit

- **Say.** "audit the OS", "check OS health", or "full audit".
- **Outcome.** One composite health report with pass or fail per dimension: readiness, wiki state, brain staleness, voice completeness, quarantine.
- **Reads.** Composes `readiness-check`, `lint`, `wiki-build` (read-only check), brain folder, `core/voice-profile.yml`, `system/quarantine.md`.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Weekly. Or before a major rebuild.
- **Follow-up.** Each failed section names the skill that fixes it. Slash command: `/founder-os:audit`.

### housekeeping

- **Say.** "run housekeeping", "clean up the OS", or "what maintenance is due".
- **Outcome.** Detect mode (default): one read-only screen of every piece of accumulated debt - stale cadence, aging rants, log bloat, stale wiki graph and snapshot, broken links, decay-due flags, memory gaps, quarantine, skill health - each with severity and the exact fix command. Fix mode ("housekeeping fix"): the reversible fixes run in dependency order, then a punch-list of the judgment calls plus a verify table filled by re-reading each side-effect.
- **Reads.** Cadence headers, `brain/rants/`, `brain/log.md`, `brain/relations.yaml`, `brain/flags.md`, `system/quarantine.md`, `brain/.snapshot.md`; runs `scripts/memory-diff.py` and `scripts/skill_health.py`.
- **Writes.** Detect: nothing. Fix: only the reversible AUTO items (anchor bump, dream, log archive, unambiguous pointer repoints, wiki-build, snapshot refresh).
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Weekly, a natural pair with the weekly review. Detect any time.
- **Follow-up.** Clear the punch-list items yourself - the skill never makes judgment calls. Slash command: `/founder-os:housekeeping [fix]`.

### lint

- **Say.** "lint the wiki", "find broken links", or "what's stale".
- **Outcome.** A list of broken `[[wikilinks]]` (ambiguous slugs now name the deterministic pick the resolver would choose, not just the candidate list), orphan files (no inbound links), entries past `Decay after:` date, entries that LACK a `Decay after:` field where the anchor date is 30+ days old (soft signal, prefixed `decay-gap`, not a defect), `brain/log.md` past its 300-line cap (reminder, prefixed `log-cap`, not a defect), provenance gaps in `raw/`, possible contradictions across files.
- **Reads.** Every markdown file in scope (skips `.git`, `archive`, `tests`).
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Weekly. After a heavy `/dream` session. Before `audit`.
- **Follow-up.** Fix named files manually. Run `wiki-build` to refresh the graph. Slash command: `/founder-os:lint`.

### wiki-build

- **Say.** "rebuild the wiki graph", "refresh relations", or "extract wikilinks".
- **Outcome.** A refreshed wiki graph extracted from every `[[wikilink]]` across markdown files. Reports edges added and removed.
- **Reads.** All in-scope markdown.
- **Writes.** `brain/relations.yaml` (auto section between markers, manual edges preserved).
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** After adding cross-references in a session. Before `lint`.
- **Follow-up.** `lint` to verify. `query` to traverse. Slash command: `/founder-os:wiki-build`.

### log-archive

- **Say.** "archive my log", "my log is getting long", or "trim the brain log".
- **Outcome.** The oldest entries in `brain/log.md` move into monthly archives at `brain/archive/log-YYYY-MM.md`, the most recent entries stay, and a one-line pointer is left at the foot of the log. Keeps the file every skill reads small as the install ages. Deterministic, no LLM call, free-tier safe.
- **Reads.** `brain/log.md`.
- **Writes.** `brain/archive/log-YYYY-MM.md` (per month) and a trimmed `brain/log.md` with a pointer footer. `--dry-run` writes nothing.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete (the script ships to `scripts/log-archive.py`).
- **When to run.** When the log grows past its 300-line cap, or a long session feels heavy. Idempotent: a re-run while under the cap does nothing.
- **Follow-up.** None. The pointer names where history went. Run `python scripts/log-archive.py` or say "archive my log".

### observation-rollup

- **Say.** "roll up observations" or "compress old logs".
- **Outcome.** JSONL observation files older than 10 days grouped by ISO week and compressed into `brain/observations/_rollups/YYYY-Wnn.md`. Source JSONL files deleted only after the rollup is verified written. Reports counts: rolled, pending, already rolled.
- **Reads.** `brain/observations/*.jsonl`.
- **Writes.** `brain/observations/_rollups/YYYY-Wnn.md` per compressed week. Removes source JSONLs after verified write.
- **Voice rules.** No.
- **Prereqs.** `FOUNDER_OS_OBSERVATIONS=1` was set at some point (no JSONL files otherwise; the skill exits cleanly).
- **When to run.** When the SessionStart brief surfaces "N JSONL files older than 10 days". Safe to run anytime - idempotent.
- **Follow-up.** None. The rollup file is the durable record. Slash command: `/founder-os:observation-rollup`.

### cross-link

- **Say.** "cross-link this file", "wikilink the references in", "convert backticks to wikilinks", or "retrofit links in".
- **Outcome.** A proposal that converts backtick-quoted paths and bare prose paths in one markdown file into `[[wikilinks]]`, shown as a list and a unified diff before anything is written. Companion to `wiki-build` - cross-link writes the edges, wiki-build extracts them. Pure regex over the filesystem index, no model reasoning, free-tier accessible.
- **Reads.** The one target file plus the filesystem index of existing wiki files. Uses `scripts/cross-link.py` if present, falls back to inline detection if not.
- **Writes.** Read-only by default. On your approval, edits the same file in place, then runs `wiki-build` to refresh the graph and appends one line to `brain/log.md`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. The target file exists.
- **When to run.** After a session edits a file whose prose names another wiki node by path. One file per run, not a back-catalog sweep.
- **Follow-up.** `wiki-build` to refresh `brain/relations.yaml`, then `lint` to catch broken refs. No dedicated slash command.

### memory-pass

- **Say.** "run a memory pass", "check my memory", or "is my memory stale".
- **Outcome.** A contradiction table that checks each Active Project Context entry in `MEMORY.md` against current file state, marking each STALE, FRESH, or CHECK. For every STALE or CHECK row you get a one-line proposed edit and approve it per row. Never touches Behavioral Guards.
- **Reads.** `MEMORY.md` (Active Project Context only), `brain/log.md`, `context/clients.md`, `context/decisions.md`, `context/leads.md` and `brain/flags.md` if present.
- **Writes.** Nothing without an explicit per-row yes. On yes, edits the linked memory file and the `MEMORY.md` index line, then appends one maintenance line to `brain/log.md`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete (it sets up the auto-memory file).
- **When to run.** First session after a 7-day-plus gap. After any close, block, unblock, or relationship reversal. When something said in chat contradicts what memory claims.
- **Follow-up.** None. The corrected memory is on disk. No dedicated slash command.

### since-last-session

- **Say.** "what changed since last session", "what did I miss", or "catch me up since I was last here".
- **Outcome.** A 5-section delta report scoped to the gap since this skill last ran: hours elapsed, `brain/log.md` entries added, flags decayed, commitments now overdue, and files modified in `context/`. The marker advances at the end so the next run scopes to the next gap. First run seeds the marker and prints a one-line note with no delta.
- **Reads.** `brain/.last-session` (the marker), `brain/log.md`, `brain/flags.md`, `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, `brain/.snapshot.md` if present. One `git log` call lists changed files in `context/`.
- **Writes.** `brain/.last-session` only. No other file is touched.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. Works without git (Section 5 reports the gap if the install is not a repo).
- **When to run.** At the start of a working session after a gap, before any planning work.
- **Follow-up.** `strategic-read` if you want a fuller orientation after the delta. Slash command: `/founder-os:since-last-session`.

### strategic-read

- **Say.** "give me a strategic read", "where am I", or "read across my brain and tell me where I stand".
- **Outcome.** A 5-section state-of-the-OS report: Identity anchor, Active commitments and pipeline, Open decisions, Active flags, Next 3 recommended moves. Pass a section key (`identity`, `commitments`, `decisions`, `flags`, `next-moves`) to render only that section. Prepends a STALE line if a cadence header is out of date.
- **Reads.** `core/identity.md`, `context/priorities.md`, `context/decisions.md`, `context/clients.md`, `context/leads.md` if present, `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, `brain/flags.md`, last 20 `brain/log.md` entries, `brain/.snapshot.md` if present.
- **Writes.** Read-only. Nothing is modified.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Returning after a gap and needing one orientation pass. Before a planning session. When a question spans priorities, pipeline, decisions, and flags at once.
- **Follow-up.** `priority-triage` if the read shows overload, or `today` for the day view. Slash command: `/founder-os:strategic-read`.

---

## Retrieval

### query

- **Say.** "search the OS for <topic>", "what blocks <priority>", or "what connects to <client>".
- **Outcome.** Top 3 to 5 OS nodes matching your question, with stable IDs and the multi-hop path that reached them. Three modes: `index` (default), `timeline --anchor <slug>`, `full --ids <a,b,c>`.
- **Reads.** `brain/relations.yaml` plus core operating files.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. `brain/relations.yaml` exists (run `wiki-build` once).
- **When to run.** Topic remembered, file forgotten. Want surrounding entries by date. Have a known ID and need the body.
- **Follow-up.** If too many matches, use `brain-pass` for synthesis. Slash command: `/founder-os:query`.

### brain-pass

- **Say.** "synthesise an answer on <topic>", "ask the brain about <topic>", or "what does the brain say about <topic>".
- **Outcome.** A synthesised answer in four sections: Answer (2 to 4 lines), Evidence (cited entry IDs), Confidence (high or medium or low with reason), Gaps (what the brain does not know that would change the answer).
- **Reads.** `brain/log.md`, `brain/decisions-parked.md`, `context/decisions.md`, `brain/knowledge/`, `brain/flags.md`, `brain/patterns.md`, `brain/needs-input.md`, `cadence/`. Picks 2 to 4 most likely files. Does not load all.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Question spans multiple brain files. Keyword query is too noisy. You want reasoning, not raw text dumps.
- **Follow-up.** Open cited IDs with `query --mode full --ids <ids>` if you need source content. Slash command: `/founder-os:brain-pass`.

### brain-snapshot

- **Say.** "refresh the brain snapshot" or "rebuild context".
- **Outcome.** A small deterministic markdown payload at `brain/.snapshot.md`: open flags (top 3), this week's must-do, recent decisions, voice and brand fields, staleness state.
- **Reads.** `core/voice-profile.yml`, `core/brand-profile.yml`, `brain/flags.md`, `cadence/weekly-commitments.md`, `cadence/daily-anchors.md`, `context/decisions.md`.
- **Writes.** `brain/.snapshot.md` (gitignored, per-user).
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** After `/dream`. After rolling the daily anchor. At session start of a long working block. Output-producing skills regenerate it on demand if missing.
- **Follow-up.** None directly. Skills consume it automatically. No slash command.

---

## Cadence and review

### what-to-change

- **Say.** "what should I change", "what to change in my business", "what's the most important thing to fix", or "monthly review".
- **Outcome.** The flagship routine: exactly three ranked changes worth making now, each in a plain-language urgent/important matrix and each carrying a resolvable `[source: file#anchor]` you can open. If fewer than three have real dated signal it says so rather than padding. Closes by proposing one concrete skill improvement for you to approve.
- **Reads.** `scripts/what-to-change.py gather` (the deterministic candidate gatherer: dated signal from `brain/flags.md` OPEN/ESCALATED and recent `brain/log.md`, with parked / paused / resolved items and everything in `brain/decisions-parked.md` excluded). `core/identity.md`.
- **Writes.** Read-only. Never auto-edits a skill - the recursive prompt proposes and waits for your yes.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. `scripts/what-to-change.py` present. Some dated signal in the brain layer (otherwise it honestly says nothing qualifies).
- **When to run.** Monthly, or whenever you feel busy but unsure what matters.
- **Follow-up.** Say "more on 1/2/3" to drill into the evidence and first step. `routines` to see the whole heartbeat. No dedicated slash command - say "what should I change".

### routines

- **Say.** "what are my routines", "what runs automatically", "run my morning brief", "turn on the weekly review", or "how does the heartbeat work".
- **Outcome.** A plain-English map of your routines and how each runs: the on-open daily brief (automatic), weekly-review and the what-to-change flagship on demand, and the opt-in unattended remote upgrade. Triggers any routine you name.
- **Reads.** `core/identity.md`. Routes to the relevant routine skill.
- **Writes.** Read-only itself; the routine it triggers does its own writes.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** When you want to know what the OS does on its own, or to fire a routine by name.
- **Follow-up.** Wrap a routine with `/loop` to repeat it in a session. `backup` to start the sync path for unattended runs. No dedicated slash command - say "what are my routines".

### weekly-review

- **Say.** "run my weekly review", "weekly retro", or "roll the sprint".
- **Outcome.** A Must / Should / Did bucket per priority for last week, plus a keep / kill / escalate verdict on every open flag.
- **Reads.** `cadence/weekly-commitments.md`, `context/priorities.md`, `brain/log.md`, `brain/flags.md`, `cadence/daily-anchors.md`, `brain/.snapshot.md` if present.
- **Writes.** Rolls `cadence/weekly-commitments.md` forward to the new week with previous-week retro folded in. Updates `context/priorities.md` if priorities shifted. Appends a retro entry to `brain/log.md`. Updates `brain/flags.md` on keep / kill / escalate. Optional git commit at the end.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. At least one week of cadence data.
- **When to run.** Friday EOD or Monday AM. Weekly.
- **Follow-up.** `priority-triage` if the new week feels overloaded. No dedicated slash command yet.

### priority-triage

- **Say.** "I'm overwhelmed", "what should I focus on next", or "help me prioritize".
- **Outcome.** A top 3 list with everything else explicitly cut and the reason for each cut.
- **Reads.** `context/priorities.md`, `context/decisions.md`, `context/clients.md`, `cadence/weekly-commitments.md`, `brain/flags.md`, `brain/.snapshot.md` if present.
- **Writes.** Updates `cadence/daily-anchors.md` with today's anchor. May move items between Must Do, Should Do, and Could Do tiers in `cadence/weekly-commitments.md`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** When overwhelmed. When the priority list grew past 5. When you cannot decide what to start.
- **Follow-up.** None directly. The triage results are already on disk. No dedicated slash command yet.

### brain-log

- **Say.** "capture this", "log this", "flag this", "park this decision", or "note this".
- **Outcome.** A new entry in `brain/log.md` with a stable `log-YYYY-MM-DD-NNN` ID and one of three tags: `#context` (log only), `#xref:<file>` (log with cross-reference), `#acted` (log and act).
- **Reads.** `brain/.snapshot.md` if present.
- **Writes.** `brain/log.md`. Optionally the cross-referenced file (Mode B). Optionally other files (Mode C, the acted-on target).
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Whenever you have a thought worth keeping but no specific structured action.
- **Follow-up.** None directly. `/dream` later rolls unprocessed signals up. No dedicated slash command (the skill auto-routes mode).

---

## Decision and coaching

### decision-framework

- **Say.** "help me decide", "should I", "I'm stuck between", or "weigh these options".
- **Outcome.** A structured decision document: criteria, options, trade-offs, kill criteria, plus a lead-with block matched to your decision style (gut, data, dialogue, mixed) from your identity.
- **Reads.** `core/identity.md` (decision style), `context/decisions.md`, `brain/.snapshot.md` if present.
- **Writes.** Read-only. Output is the decision template in chat. You copy the resolved decision into `context/decisions.md` yourself when you commit to it.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** When weighing 2+ options. When stuck. When a decision has been pending for too long.
- **Follow-up.** Paste the resolved decision into `context/decisions.md`. Log it with `brain-log` if it has downstream effects. No dedicated slash command.

### founder-coaching

- **Say.** "check in on <person>", "do a founder review", "how is <person> doing", or "am I in wartime or peacetime".
- **Outcome.** A diagnostic across the four operating zones (peacetime, pre-war, wartime, recovery), a role and identity map, and a verdict on what to shed.
- **Reads.** `core/identity.md`, `context/priorities.md`, `brain/flags.md`, `brain/.snapshot.md` if present.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** When stuck. When burning out. When confusing busy with productive.
- **Follow-up.** `priority-triage` or `decision-framework` to act on what surfaced. No dedicated slash command.

### forcing-questions

- **Say.** "should I start this", "is this worth doing", or "force me to think this through".
- **Outcome.** Six yes / no answers (vague done state, phantom user, scope creep, false urgency, sunk-cost trap, opportunity cost) plus a verdict: GREEN (start), PARK (postpone), or KILL.
- **Reads.** `core/identity.md`, `context/priorities.md`. Initiative description from your prompt.
- **Writes.** On GREEN, appends a `#building` entry to `brain/log.md`. On PARK, appends a parked decision to `brain/decisions-parked.md` with a stable ID and a trigger condition. On KILL, read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Before starting any new initiative. When scope is creeping mid-task.
- **Follow-up.** If GREEN: document in `context/priorities.md`. If PARK: revisit when the trigger condition fires. Slash command: `/founder-os:forcing-questions`.

---

## Meeting and capture

### catch-up

- **Say.** "catch up", "process my inbox", "I sent myself some notes", or paste a pile of raw phone captures.
- **Outcome.** Everything captured away from the laptop lands in the brain: `capture/inbox/` drops, pasted text, and (when connected) meeting-notes transcripts are filed to `brain/rants/` with provenance and `processed: false`, names checked against your glossary, unknowns marked `(sp?)` and asked about once, in one batch.
- **Reads.** `capture/inbox/`, `context/names.md`, `stack.json` for a bound meeting-notes tool.
- **Writes.** `brain/rants/<date>-<slug>.md` per capture; swept inbox files move to `capture/inbox/.processed/`; confirmed corrections append to `context/names.md`.
- **Voice rules.** No. Your words are filed raw, never rewritten.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** First session back at the desk after time away. Any time the inbox has files.
- **Follow-up.** `/founder-os:dream` to distil the filed rants. Run via `/founder-os:catch-up`. Channel guide: `docs/capture-anywhere.md`.

### meeting-prep

- **Say.** "prep me for my call with [name]", "prep for a meeting", or "debrief this meeting".
- **Outcome.** A pre-meeting brief (attendees, prior interactions, talking points, questions, watch-fors) or a post-meeting debrief routed into the right files.
- **Reads.** `stack.json`, `context/clients.md`, `core/identity.md`, `brain/.snapshot.md` if present. Auto-invokes `brain-pass` on the meeting subject.
- **Writes.** Read-only for the brief. Debrief mode writes to `brain/log.md`, `context/clients.md`, and any open commitments.
- **Voice rules.** No (the brief is for you).
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** 10 to 30 minutes before any meeting that matters. Right after the meeting for the debrief.
- **Follow-up.** `pre-send-check` if the post-meeting follow-up is a deliverable. No dedicated slash command (composes with `/pre-meeting` and `/capture-meeting`).

### session-handoff

- **Say.** "package this for a new session", "hand this off", or "wrap this up for next time".
- **Outcome.** A handoff file naming what you did, what is open, and what the next operator needs to know.
- **Reads.** `brain/log.md`, `cadence/`, current task context.
- **Writes.** A file named `SESSION_HANDOFF_<project>_<YYYY-MM-DD>.md` at the location the operator names (typically the project root or `brain/handoffs/`).
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** End of a session you want to resume cleanly. Before a long break.
- **Follow-up.** Open the file at the start of the next session. No dedicated slash command.

### handoff-protocol

- **Say.** "hand this off to <person>", "build a handoff", or "delegate this".
- **Outcome.** A structured handoff artifact when work moves to a different person, role, or future session.
- **Reads.** Source context the operator describes.
- **Writes.** A handoff file at `brain/handoffs/<YYYY-MM-DD>-<topic>.md`, or appends to `brain/log.md`, or writes into your knowledge base, depending on scope.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Before delegating a task. Before a role change. Before parking a long thread.
- **Follow-up.** Notify the receiving operator. No dedicated slash command.

---

## Writers (voice-coupled)

### linkedin-start

- **Say.** "help me with my LinkedIn", "what can I do with my LinkedIn", or "give me my LinkedIn data".
- **Outcome.** You pick an outcome - leads, a better job, a louder brand, or a healthier network - and the OS aims your own LinkedIn export at it, then hands back a roadmap from your real baseline. The front door to the whole LinkedIn pack.
- **Reads.** `core/identity.md` and `core/profile.md` if present (to reuse what the OS already knows), then your LinkedIn export.
- **Writes.** Read-only, except one optional breadcrumb (`brain/.linkedin.md`) written only if you accept full setup.
- **Voice rules.** No. It routes; the skill it routes to owns any writing.
- **Prereqs.** Your LinkedIn data export (larger data archive). None other - a cold install can use it.
- **When to run.** Any open-ended LinkedIn ask, when you have not yet picked a specific job.
- **Follow-up.** Routes to `linkedin-network-scan`, `linkedin-power-audit`, `linkedin-brand-direction`, or `linkedin-warm-revival`. No dedicated slash command.

### linkedin-brand-direction

- **Say.** "what should I post on LinkedIn", "what's my content lane", or "give me a LinkedIn content direction".
- **Outcome.** A personalised, algorithm-aware content direction written to `brand-direction.json`: your topic lane (with the number behind it), positioning angle, format mix, cadence, and three concrete first posts - all traced to your real network and the dated algorithm facts.
- **Reads.** `linkedin-power-audit`'s `audit.json` if present (else the `network-scan.json` composition), `skills/linkedin-pack-references/linkedin-algorithm.md`, and your goal.
- **Writes.** `brand-direction.json` in your scan/audit output folder (outside any repo).
- **Voice rules.** No. It sets the direction; `linkedin-post` applies voice when it writes from it.
- **Prereqs.** Run `linkedin-power-audit` first for the richest input (or at least `linkedin-network-scan`).
- **When to run.** Before a content push, when you want the lane your network actually rewards instead of generic advice.
- **Follow-up.** `linkedin-post` reads the direction automatically on the next post request. No dedicated slash command.

### linkedin-power-audit

- **Say.** "audit my LinkedIn", "analyse my whole LinkedIn", or "where is my network thin".
- **Outcome.** A deep, deterministic `audit.json`: network composition (role clusters, stakeholder buckets, industries, top companies, founder pool), message warmth, content lanes, plus an optional network-gap read. The input the brand and revival skills need.
- **Reads.** Your UNZIPPED LinkedIn export folder (Complete export for the full audit).
- **Writes.** `audit.json` in an output folder you choose (outside any repo).
- **Voice rules.** No. Deterministic extract; any narrative you add applies voice separately.
- **Prereqs.** The unzipped export. Python (stdlib only, no pip install).
- **When to run.** When you want the whole shape of your network, not just a ranked list. Before `linkedin-brand-direction` or `linkedin-warm-revival`.
- **Follow-up.** `linkedin-warm-revival` and `linkedin-brand-direction` both read the `audit.json`. No dedicated slash command.

### linkedin-warm-revival

- **Say.** "who should I reconnect with", "revive my dormant contacts", or "who have I gone cold with".
- **Outcome.** A ranked list of dormant-but-valuable contacts who replied to you before, each with a one-line personal reopener. Nothing sent; outreach stays manual.
- **Reads.** `audit.json` from `linkedin-power-audit` (its prerequisite) - the message counterparties, warmth, and network composition.
- **Writes.** Read-only.
- **Voice rules.** Light - the reopeners should sound like you, grounded in real metadata only.
- **Prereqs.** `linkedin-power-audit` run first (on the Complete export, so warmth data exists).
- **When to run.** When you want to reactivate relationships that already exist instead of cold outreach.
- **Follow-up.** Send the reopeners manually. No dedicated slash command.

### linkedin-post

- **Say.** "write a LinkedIn post", "turn this into a post", or "post about this".
- **Outcome.** A LinkedIn post in your voice, anti-AI rules applied, hooks tested against the "see more" cutoff.
- **Reads.** `core/voice-profile.yml`, `brain/.snapshot.md` if present. Auto-invokes `brain-pass` on recent themes versus recent decisions.
- **Writes.** Read-only.
- **Voice rules.** Yes. Required.
- **Prereqs.** `voice-interview` complete (or it falls back to anti-AI baseline with a warning).
- **When to run.** When you have a post-worthy idea. After a `/dream` session that surfaces one.
- **Follow-up.** Paste, post, engage in the first 60 minutes. No dedicated slash command.

### email-drafter

- **Say.** "write an email", "draft a reply", "follow up with <person>", or "respond to this".
- **Outcome.** A draft email in your voice ready to copy-paste. Subject and body. Tone matched to recipient.
- **Reads.** `core/voice-profile.yml`, `core/identity.md`. Inbox via Gmail or Outlook MCP if connected. Otherwise the user pastes the thread.
- **Writes.** Read-only.
- **Voice rules.** Yes. Required.
- **Prereqs.** `voice-interview` complete.
- **When to run.** Any draft email. Cold outreach. Reply to a thread. Internal note.
- **Follow-up.** `pre-send-check` if it is a high-stakes send. No dedicated slash command.

### client-update

- **Say.** "update the client", "write a status update", or "weekly update for <client>".
- **Outcome.** A status update for a named client, framed in your voice with progress lifted from `context/clients.md`.
- **Reads.** `core/voice-profile.yml`, `context/clients.md`.
- **Writes.** Read-only. Optionally appends a touch-point to `context/clients.md` if the user asks.
- **Voice rules.** Yes. Required.
- **Prereqs.** `voice-interview` complete. The client must have a row in `context/clients.md`.
- **When to run.** Weekly cadence per client. After a milestone. When the client asks.
- **Follow-up.** Send via `email-drafter` or paste into the client's preferred channel.

### proposal-writer

- **Say.** "write a proposal", "draft a SOW", or "create a quote for <client>".
- **Outcome.** A full proposal document: scope, deliverables, timeline, terms, pricing. Voice and brand inherited.
- **Reads.** `core/voice-profile.yml`, `core/brand-profile.yml` if present, `context/clients.md`, `brain/knowledge/` for past wins.
- **Writes.** A proposal file at the path the operator names (typically under `core/drafts/` or `drafts/`). Branded if `your-deliverable-template` is invoked, plain text otherwise.
- **Voice rules.** Yes. Required.
- **Prereqs.** `voice-interview` complete. `brand-interview` only if you want the proposal branded.
- **When to run.** After a discovery call when a deal is hot. Inside 24 hours.
- **Follow-up.** `ship-deliverable` final gate. No dedicated slash command.

### content-repurposer

- **Say.** "repurpose this", "turn this into <channel>", or "make versions of this for <channels>".
- **Outcome.** One source piece reformatted across LinkedIn, Twitter, newsletter, and internal doc, all in your voice.
- **Reads.** `core/voice-profile.yml`. Source piece from prompt or path.
- **Writes.** Read-only. The user pastes outputs into the right channels.
- **Voice rules.** Yes. Required.
- **Prereqs.** `voice-interview` complete.
- **When to run.** When a single piece (talk, podcast, post) deserves multiple channel outings.
- **Follow-up.** `linkedin-post` to refine the LinkedIn draft. No dedicated slash command.

### sop-writer

- **Say.** "write an SOP", "document this process", or "create a runbook".
- **Outcome.** A structured SOP someone else could follow, captured from how you describe the process verbally.
- **Reads.** `core/voice-profile.yml` (`voice.rhythm` and `voice.reading_level`). Process description from prompt.
- **Writes.** Read-only by default. Operator saves the SOP at the path that fits.
- **Voice rules.** Yes. The skill mandates pulling rhythm and reading level from your voice profile so the SOP reads consistently with the rest of your writing.
- **Prereqs.** `voice-interview` complete (or it falls back to anti-AI baseline).
- **When to run.** When you catch yourself doing a process for the second time. Before delegating.
- **Follow-up.** Hand the SOP to the operator who will run it. No dedicated slash command.

### your-voice

- **Say.** "rewrite this in my voice", "voice this up", or "apply my voice".
- **Outcome.** Any text rewritten in your voice using `core/voice-profile.yml`.
- **Reads.** `core/voice-profile.yml`. Source text from prompt.
- **Writes.** Read-only.
- **Voice rules.** This is the engine.
- **Prereqs.** `voice-interview` complete (or it falls back to anti-AI baseline with a warning).
- **When to run.** Any other writing skill calls this internally. Direct invocation when you want to push a paragraph through the voice filter.
- **Follow-up.** None. No dedicated slash command.

### your-deliverable-template

- **Say.** "make a CV", "build a pitch deck", "create a one-pager", or "in my brand".
- **Outcome.** A branded document (proposal, deck, one-pager) inheriting colors, fonts, logo, footer, and page geometry from your brand profile.
- **Reads.** `core/brand-profile.yml`, `core/brand-assets/`. Content from prompt.
- **Writes.** A branded file under `core/drafts/` or `core/outputs/`.
- **Voice rules.** Inherits from the calling writer skill (loads `your-voice` for any text inside the document).
- **Prereqs.** `brand-interview` complete. Logo files dropped into `core/brand-assets/`.
- **When to run.** Whenever a writer skill produces a branded output. Called internally by `proposal-writer`.
- **Follow-up.** `ship-deliverable`. No dedicated slash command.

---

## Brand and content

### brand-voice-interview

- **Say.** "set up a brand voice", "capture our brand voice", "add a brand", or "set up brand voice for <name>".
- **Outcome.** An interview captures one brand's writing voice and positioning, then writes two files under `brands/<slug>/`. Different from `voice-interview`, which captures your own personal voice. This captures how a brand you run speaks, so it can survive after you stop writing every word yourself.
- **Reads.** `templates/brand-voice.yml.template`, `templates/brand-positioning.yml.template`. Scans `brands/<slug>/`, `clients/<slug>/`, `raw/<slug>/`, and `sources/<slug>/` for any brand writing already on disk before asking for fresh samples.
- **Writes.** `brands/<slug>/voice.yml`, `brands/<slug>/positioning.yml`. Creates `brands/<slug>/assets/` for logo files.
- **Voice rules.** This is the source for the named brand. Separate from `core/voice-profile.yml`.
- **Prereqs.** `founder-os-setup` complete. 2 to 5 real brand samples ready to paste (existing captions, product copy, customer emails the brand has sent).
- **When to run.** Once per brand you run. Re-run when a brand's voice or positioning shifts.
- **Follow-up.** `campaign-from-theme` or `review-responder` for the same brand. Slash command: `/founder-os:brand-voice-interview`.

### campaign-from-theme

- **Say.** "build a campaign", "campaign for <topic>", "plan a campaign", or "draft a launch campaign".
- **Outcome.** A campaign brief with sequencing rationale, then 3 to 7 content drafts in the right voice. The skill refuses to draft until five funnel-gating questions are answered: speaker, objective, audience segment plus temperature, channel-fit logic, and success metric. The gate is what makes the output usable on the first attempt.
- **Reads.** `brands/<slug>/voice.yml` and `brands/<slug>/positioning.yml` when a brand is the speaker, else `core/voice-profile.yml` and `core/identity.md`. Globs `brands/*/voice.yml` to list speakers.
- **Writes.** A campaign brief and drafts at `campaigns/<slug>-<date>.md` if you save. Creates `campaigns/` if it does not exist.
- **Voice rules.** Yes. Required. Every draft runs through `your-voice`.
- **Prereqs.** `founder-os-setup` complete. Voice profile filled. If a brand is the speaker, `brand-voice-interview` for that brand should be complete.
- **When to run.** Before any multi-piece campaign, launch, or sequenced content push.
- **Follow-up.** Run drafts through your usual approval flow. Slash command: `/founder-os:campaign-from-theme`.

### review-responder

- **Say.** "draft a reply to this review", "respond to this DM", "reply to this WhatsApp", or "answer this Google review".
- **Outcome.** A draft reply to an incoming customer message in the right voice for the channel and brand. Works for Google reviews, Trustpilot, Instagram DMs, WhatsApp Business inquiries, customer emails, Yelp, and Facebook comments. Asks one question first - whose voice, operator or which brand - then drafts. Public channels also get a "who else reads this" check.
- **Reads.** `core/voice-profile.yml` for operator voice, or `brands/<slug>/voice.yml` and `brands/<slug>/positioning.yml` when a brand is chosen. Globs `brands/*/voice.yml` to list speakers.
- **Writes.** Read-only by default. Returns the draft in chat. You copy and send.
- **Voice rules.** Yes. Required. A reply in the wrong voice erodes trust more than no reply.
- **Prereqs.** `founder-os-setup` complete. Voice profile filled. If responding as a brand, `brand-voice-interview` for that brand should be complete.
- **When to run.** Whenever a customer message arrives that needs a careful, on-voice reply.
- **Follow-up.** Copy the draft, edit if needed, send. Slash command: `/founder-os:review-responder`.

---

## Knowledge and analysis

### knowledge-capture

- **Say.** "capture this", "log this", "I just read", or "takeaways from <source>".
- **Outcome.** A new `brain/knowledge/<topic>.md` note with a stable `know-YYYY-MM-DD-NNN` ID, plus a row in the knowledge index.
- **Reads.** `brain/knowledge/`, `brain/.snapshot.md` if present. Source from prompt or path.
- **Writes.** `brain/knowledge/<topic>.md` (creates or appends), `brain/knowledge/README.md` (index row).
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** After reading a book, listening to a podcast, finishing an article, or running an experiment that produced a takeaway.
- **Follow-up.** `proposal-writer` and `strategic-analysis` will cite the new note automatically. No dedicated slash command.

### strategic-analysis

- **Say.** "analyze this market", "competitor map", "evaluate this opportunity", or "TAM SAM SOM".
- **Outcome.** A market scan, competitor map, opportunity assessment, or business-model evaluation grounded in your `brain/knowledge/` notes.
- **Reads.** `core/identity.md`, `context/companies.md`, `context/decisions.md`, `brain/knowledge/`, `brain/.snapshot.md` if present.
- **Writes.** Read-only. Optional analysis file under `drafts/strategy/`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. `brain/knowledge/` populated for the analysed market or competitor.
- **When to run.** When evaluating a new market entry. Before a pricing change. Before a positioning rewrite.
- **Follow-up.** `decision-framework` if a decision falls out. `proposal-writer` if a positioning play is ready. No dedicated slash command.

### unit-economics

- **Say.** "run the numbers", "what should I charge", "is this profitable", or "what's the unit economics".
- **Outcome.** The math on a deal, hire, pricing change, or new business line: CAC, LTV, gross margin, breakeven, payback period. Plus the sensitivity to the input the user is least sure about.
- **Reads.** Source numbers from prompt. `context/companies.md`, `context/clients.md` for context, `brain/.snapshot.md` if present.
- **Writes.** Read-only by default. The model output is a structured numbers block. The operator saves it where appropriate.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Before signing a deal. Before quoting a price. Before making a hire.
- **Follow-up.** `decision-framework` to choose, or `proposal-writer` to send. No dedicated slash command.

### bottleneck-diagnostic

- **Say.** "what's blocking me", "why does everything route through me", or "can the business run without me".
- **Outcome.** A founder-dependency score across decisions, clients, process, revenue, and growth capacity. Plus the highest-impact shed.
- **Reads.** `core/identity.md`, `context/`, `brain/log.md`, `brain/flags.md`.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. The diagnostic is more accurate with at least 2 weeks of cadence data, but does not enforce it.
- **When to run.** Quarterly. Or when you feel like everything routes through you.
- **Follow-up.** `sop-writer` for the shed candidate. `handoff-protocol` for the receiver. No dedicated slash command.

### founder-next-move

- **Say.** "what should I do next", "what's my next move", or "propose my next move".
- **Outcome.** The single highest-leverage move toward your next paying customer, with a three-option close (one big, two small) so you always leave with a step you can start today.
- **Reads.** `brain/.snapshot.md` (the four-field Founder Snapshot), `core/identity.md`, `core/profile.md`, `brain/log.md`, `context/clients.md`, `context/priorities.md`, `cadence/`, `brain/flags.md`.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete with a Founder Snapshot. Founder and team_of_one variants. A thin snapshot still proposes a capture move.
- **When to run.** Any morning, or any time you are unsure what to do next. Also surfaced as a nudge in the SessionStart brief once the brain is functional, and through `/next` for founders.
- **Follow-up.** `founder-scope-challenge` to stress-test the plan, or `decision-framework` for a structured choice. No dedicated slash command (reached via `/next` or natural language).

### founder-scope-challenge

- **Say.** "challenge my plan", "stress test this", "am I doing too much", or "talk me out of this".
- **Outcome.** A brutal read of the plan in one of three modes - Expand (too small), Hold (right-sized, defend it), or Reduce (bloated, cut to the one move) - against one test: does this reach a paying customer faster. Brutal on the plan, never on the person.
- **Reads.** `brain/.snapshot.md` (the Founder Snapshot), `cadence/weekly-commitments.md`, `context/priorities.md`, `brain/log.md`, `brain/flags.md`, or the plan you paste.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. Founder and team_of_one variants.
- **When to run.** Before committing weeks to a plan, or when you suspect it is too small, too bloated, or about to be abandoned for the next idea.
- **Follow-up.** `founder-next-move` for the immediate step on the rewritten plan, `decision-framework` to weigh a direction change, or `forcing-questions` before a brand-new initiative. No dedicated slash command.

---

## Ship gate

### pre-send-check

- **Say.** "check this before I send", "ready to send", or "final review".
- **Outcome.** A pass or fail verdict across voice, source truth, anti-AI scan, and personalization. Names every issue.
- **Reads.** The deliverable path. `rules/anti-ai-writing.md` if present.
- **Writes.** Read-only.
- **Voice rules.** Optional. Voice consistency is one of the checks but the skill does not load `core/voice-profile.yml` directly. Run `your-voice` first if you want a strict voice match.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Before any deliverable leaves your machine.
- **Follow-up.** Fix every named issue. Re-run. Then `ship-deliverable` for the composite gate. No dedicated slash command (called by `ship-deliverable`).

### blind-spot-review

- **Say.** "find blind spots", "what am I missing", or "review for risk".
- **Outcome.** A second-pass review across legal, contracts, data, timing, relationships, upside, and walkaway risk. Names risks before pre-send.
- **Reads.** The deliverable path.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** On any high-stakes deliverable before `pre-send-check`. Especially proposals and contracts.
- **Follow-up.** `pre-send-check`, then `ship-deliverable`. No dedicated slash command (called by `ship-deliverable`).

### ship-deliverable

- **Say.** "ship this", "is this ready to ship", or "run the ship checks".
- **Outcome.** One composite pass-or-fail across template fit, anti-AI scan, blind-spot evidence, and pre-send checks.
- **Reads.** The deliverable path. Composes `your-deliverable-template`, anti-AI scan, `blind-spot-review`, `pre-send-check`.
- **Writes.** Read-only.
- **Voice rules.** Inherited from the upstream chain. Does not load the voice profile directly.
- **Prereqs.** `founder-os-setup` complete. The chain still runs without `voice-interview` or `brand-interview`, but those checks degrade.
- **When to run.** Final gate. Before any deliverable leaves your machine.
- **Follow-up.** Fix every issue, re-run until pass. Slash command: `/founder-os:ship-deliverable`.

---

## Safety

### approval-gates

- **Say.** "does this need approval", "can I do this", or "check this against the rules".
- **Outcome.** An auto-run / ask-first / refuse verdict on a proposed action against `rules/approval-gates.md`.
- **Reads.** `rules/approval-gates.md`. Action description from prompt.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. `rules/approval-gates.md` populated.
- **When to run.** Before any action with downside risk that the OS could take on your behalf.
- **Follow-up.** Auto-run: proceed. Ask-first: pause for confirmation. Refuse: stop. No dedicated slash command (other skills call this internally).

### data-security

- **Say.** "is this safe to paste", "can I send this to <tool>", or "classify this data".
- **Outcome.** A data classification (Public, Internal, Confidential, Restricted) and a safe-path verdict before any paste, upload, or external tool use.
- **Reads.** `rules/data-handling.md` if present. Data sample from prompt.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Before pasting client data into an external tool. Before uploading anything to a third-party. Before sharing in a public channel.
- **Follow-up.** Honour the verdict. No dedicated slash command.

---

## Utility

### context-persistence

- **Say.** "what do we know about <topic>", "give me the prior context", or "remind me where we left off".
- **Outcome.** A source-cited answer to "what do we already know about X" before you re-explain.
- **Reads.** Targeted reads across `core/`, `context/`, `brain/`, `clients/`, `companies/`.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Before re-explaining context to the model. Before re-pasting client background. When the model asks for something you wrote down weeks ago.
- **Follow-up.** Use the cited paths in your next prompt. No dedicated slash command.

### business-context-loader

- **Say.** "load context for <company>", "what's next on <company>", or "give me an action on <company>".
- **Outcome.** A loaded per-company context file plus a list of what is missing or stale and the next obvious move.
- **Reads.** `companies/<slug>-business.md` (operator path; the company you run), `context/clients.md`.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. At least one operator company file at `companies/<slug>-business.md`.
- **When to run.** When switching focus to a different company or project you run. Start of a working block scoped to one operator entity.
- **Follow-up.** Skill named in the "next move". For prospect companies, use `prospect-init` instead. No dedicated slash command.

### prospect-init

- **Say.** "add a prospect", "track <company> as a prospect", "start tracking <company>", or "new prospect <company>".
- **Outcome.** A new lightweight prospect file at `companies/prospects/<slug>.md` capturing the minimum intel (company name, sector, why you are tracking them, current relationship stage, fit signals against your ICP).
- **Reads.** `templates/prospect-context.template.md`, optionally `companies/<slug>-business.md` (operator) for ICP and anti-ICP signals.
- **Writes.** `companies/prospects/<slug>.md` (new), `brain/log.md` (one-line trace).
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** When you first start tracking a company you are selling to or watching. Different from `business-context-loader`, which is for companies you run.
- **Follow-up.** `proposal-writer`, `strategic-analysis`, or `client-update` will read this file when they need company-specific context. No dedicated slash command.

### ingest

- **Say.** "ingest this", "process this source", or "save this transcript".
- **Outcome.** A new file in `raw/<source>.md` with provenance frontmatter (URL or path, captured date, source title), plus proposed wiki updates you approve before they land.
- **Reads.** Source URL, file, or pasted text.
- **Writes.** `raw/<source>.md` always. After your approval: `context/clients.md`, `context/decisions.md`, `brain/patterns.md`, `cadence/`, or company files under `companies/` (operator path `companies/<slug>-business.md` or prospect path `companies/prospects/<slug>.md`, whichever the proposal targets), plus a one-line trace in `brain/log.md`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Whenever you read or watch something worth preserving with provenance.
- **Follow-up.** `knowledge-capture` to distil. `wiki-build` to refresh the graph. Slash command: `/founder-os:ingest`.

### queue

- **Say.** "what's on my plate", "add to queue: [thing]", "start [item]", "mark done", or "park [item]".
- **Outcome.** ACTIVE item list (capped at 3), or state transition confirmation for the named item.
- **Reads.** `cadence/queue.md`.
- **Writes.** `cadence/queue.md` on add, start, done, and park operations.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** At the start of any work session to see what is moving. Use `add to queue` when a new item needs tracking.
- **Follow-up.** `weekly-review` rolls completed queue items into `brain/log.md`. Slash command: `/founder-os:queue`.

### log-reply

- **Say.** "log this reply", "I got a reply", "they responded", "log this thread", or "capture this exchange".
- **Outcome.** A pasted thread (WhatsApp export, Telegram dump, email body, voice memo transcript) is turned into one structured `brain/log.md` entry per conversation: participants, dates, key updates, commitments, action items, and mentions. Different from `meeting-prep` debrief, which is for a meeting you ran, and `brain-log`, which is for free-form thoughts. Asks you to label the source format rather than guessing.
- **Reads.** `core/identity.md`, `brain/log.md`. Greps `context/clients.md` and `context/leads.md` to cross-reference names. `rules/approval-gates.md` (or the template fallback) for the gate. `brain/.snapshot.md` if present.
- **Writes.** `brain/log.md` directly (one entry per conversation). Proposes, never auto-writes, updates to `context/clients.md` and `context/leads.md`. You confirm each proposed row before it lands. Strips any `<private>` blocks before writing.
- **Voice rules.** Plain language, mirror the operator's words. Not voice-profile coupled.
- **Prereqs.** `founder-os-setup` complete. A thread pasted in chat or available at a path.
- **When to run.** A reply or thread landed and you want it on disk and cross-referenced before the context decays.
- **Follow-up.** The new entries surface in the next `since-last-session` and `weekly-review`. Slash command: `/founder-os:log-reply`.

### web-fetch-extract

- **Say.** "scrape this page", "pull the team names from this URL", "get the pricing tiers from this page", or "what does this page say about <topic>".
- **Outcome.** A public web page is fetched and the data you asked for is extracted: bios, leadership teams, prices, OpenGraph tags, titles, recent posts, or an answer to an open question. Extraction is the model's own reasoning over the fetched text, so there is no paid API call and it works on a free plan. Other skills call it as a sub-step when they need page data.
- **Reads.** The supplied URL via `scripts/scrape.py`. Falls back to the `WebFetch` tool if the script is missing or fails twice.
- **Writes.** Read-only. Returns JSON for fields, a markdown table for lists, or a short paragraph for an open question.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. `scripts/scrape.py` plus its Python packages (`httpx`, `selectolax`, `tenacity`) for the default path. Playwright only for the `--render` flag on JS-walled pages.
- **When to run.** When any task needs data from a public page. Never on a URL you did not supply, and it does not follow links unless the goal says to.
- **Follow-up.** Feed the extracted data into the skill that needed it. No dedicated slash command ships for this skill.

### github-ops

- **Say.** "what GitHub issues are open", "review this PR", "check CI status", or "create a GitHub issue".
- **Outcome.** A GitHub operation runs through the `gh` CLI on any repo your CLI is authenticated against: triage issues, open or review pull requests, manage branches, inspect repo state, check CI, list releases. Any write operation (create, comment, close, label, PR, rerun) is confirmed with you first.
- **Reads.** `gh auth status` to confirm authentication. `rules/commit-naming.md` if present, before any commit or PR.
- **Writes.** Read-only for queries. Write operations (issue, comment, label, PR) only after you confirm. Never force pushes, never skips hooks, never adds AI attribution to a commit, never pushes without you asking.
- **Voice rules.** No.
- **Prereqs.** `gh` CLI installed and authenticated (`gh auth login`). The target repo identified, or `--repo owner/name` passed.
- **When to run.** Any time you want a fast GitHub action without leaving the session.
- **Follow-up.** Depends on the operation. No dedicated slash command.

### skill-creator

- **Say.** "create a skill", "make a skill for", "turn this into a skill", "improve this skill", "why isn't my skill triggering", or "tune the description".
- **Outcome.** A new skill drafted from scratch, an existing skill improved, or a description tuned for better triggering, with optional eval runs that benchmark the skill against a baseline. Runs a hard description-length check at every write (at or under 900 PASS, 901 to 1024 WARN, over 1024 STOP) so a skill never silently fails to install.
- **Reads.** Existing skills in `skills/` to match the frontmatter shape. Conversation history when you say "turn this into a skill". Any reference files the new skill needs.
- **Writes.** A new `skills/<name>/SKILL.md` and bundled resources. For evals, a `<skill-name>-workspace/` sibling with iteration and result files. Never overwrites a skill name on an update.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** When a workflow you repeat is worth capturing as a skill, or when an existing skill triggers on the wrong prompts.
- **Follow-up.** Run the test prompts the skill proposes, review the results, iterate. No dedicated slash command.

### connect

- **Say.** "connect Telegram", "connect my calendar", "connect my email", "set up notifications", or "hook up <tool>".
- **Outcome.** The named tool is linked the right way for its type. env-key tools (Telegram, ElevenLabs) get their key stored in the gitignored `.env` with a live reachability check; account-level MCP tools (calendar, email) are guided to the Claude Code MCP setup because the OS cannot hold their tokens; manual-link tools store a reference URL. A skipped or connected tool is recorded in `connectors/status.md`, which the SessionStart brief surfaces.
- **Reads.** `scripts/connect.py registry` for the connector list. `.env` (to check for an existing key, never echoed). `docs/tools-and-mcps.md` for the MCP-add steps.
- **Writes.** A secret only to the gitignored `.env` (the writer refuses any non-gitignored target). `connectors/status.md` (no secrets, gitignored per-user state). Never a tracked file.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. `scripts/connect.py` present. A local runtime for env-key connectors (web-only agents guide but cannot store the key).
- **When to run.** The first time you want a tool linked, or to re-record a connector you skipped. For a 401 on an already-connected tool, use `reconnect-prompt` instead.
- **Follow-up.** Confirm the test message arrived for env-key tools. If a connected tool later fails auth, `reconnect-prompt`. Slash command: none - say "connect <tool>".

### reconnect-prompt

- **Say.** "the integration broke", "my token expired", "reconnect <tool>", or "I got a 401".
- **Outcome.** One copy-paste reconnect prompt for the tool that failed, the `stack.json` key that broke, and a `Status: ACTIVE` entry in the quarantine catch-net so the dead connector surfaces at the next session. Never retries, never asks for credentials.
- **Reads.** `stack.json` to resolve the failed placeholder. `system/quarantine.md` (or its template) for the catch-net path.
- **Writes.** `system/quarantine.md` (one ACTIVE entry; flips to RESOLVED when you confirm the reconnect). Falls back to a one-line `brain/log.md` note if no catch-net file exists.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. Called by any integration-touching skill that hits an auth failure.
- **When to run.** When a connected tool returns a 401, an expired token, an invalid grant, or revoked consent.
- **Follow-up.** Reconnect the tool in its own settings, confirm, then rerun the skill that failed. No dedicated slash command.

### list-pruner

- **Say.** "prune this list", "clean my contact list", "remove duplicates", or "score this list".
- **Outcome.** A clean markdown table with duplicates removed, missing fields flagged, and each row scored High / Medium / Low. A CSV file only if you ask for one.
- **Reads.** A CSV path or a pasted table from your prompt.
- **Writes.** Read-only by default. Writes a clean CSV only on request and only after you confirm the path. Appends a one-line `#acted` trace to `brain/log.md`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. A contact list pasted in chat or available at a path.
- **When to run.** Before an outreach push, when a list assembled by hand or from another source may hold duplicates or half-filled rows.
- **Follow-up.** Add the High-scored rows to `context/leads.md` as new leads, then `email-drafter` for the outreach. Composes with `linkedin-network-scan`. No dedicated slash command.

### finance-import

- **Say.** "import this finance export", "parse this finance CSV", or "summarize this finance export".
- **Outcome.** A normalized markdown summary of a finance CSV with totals by category and warnings for missing fields, written to `finance/<period>/summary.md`. Read-only at the source - it never writes back to your accounting tool.
- **Reads.** A finance CSV path plus a reporting period (`YYYY-MM`) from your prompt.
- **Writes.** `finance/<period>/summary.md` (after you confirm the path), plus a one-line trace in `brain/log.md`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. A finance CSV export available at a path or pasteable.
- **When to run.** When you want financial context in the OS for planning, or to feed real numbers into `unit-economics`. PDF input is a manual path until a per-format parser is tested.
- **Follow-up.** `unit-economics` to run margins on the totals, or `strategic-analysis` to cite the mirror. Standalone - no upstream finance skill required. No dedicated slash command.

---

### verify

- **Say.** "verify the OS", "run a health check", or "check the substrate".
- **Outcome.** A structured health report across 8 substrate checks (plugin surface, hooks, scripts, MCPs, free-tier floor, wiki integrity, cadence freshness, auto-memory). Each check reports PASS / WARN / FAIL with a one-line reason.
- **Reads.** `skills/index.md`, `plugin.json`, `.claude/settings.json`, `scripts/`, `brain/relations.yaml`, `cadence/`, `MEMORY.md`.
- **Writes.** Nothing. Read-only. Never auto-fixes.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** After install, after update, or when something feels broken.
- **Follow-up.** Fix the issues named in FAIL lines, then re-run. WARN lines are degraded but not blocking. Slash command: `/founder-os:verify`.

---

### legal-compliance

- **Say.** "look up [legal topic]", "what do I need to know about [regulation]", or "compliance check for [jurisdiction]".
- **Outcome.** A jurisdiction-aware legal reference answer grounded in the sources loaded via `/founder-os:legal-setup`. Read-only unless you explicitly add a source.
- **Reads.** `core/identity.md` (jurisdiction field), `skills/legal-compliance/references/<jurisdiction>/sources.yml`, loaded source files.
- **Writes.** Nothing during reference lookup. Source additions write `sources.yml` and optional domain stubs (via `/founder-os:legal-add-source`).
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. Jurisdiction set via `/founder-os:legal-setup`.
- **When to run.** Before any client contract, when a regulatory deadline surfaces, or when jurisdiction-specific guidance is needed.
- **Follow-up.** `/founder-os:legal-add-source` to add primary sources. `/founder-os:legal-update` to refresh source freshness.

### linkedin-network-scan

- **Say.** "scan my linkedin network", "who in my network fits my ICP", "build my outreach list from my connections", or share your LinkedIn export ZIP.
- **Outcome.** A ranked outreach worklist scored against an ICP you define, written to files outside any repo. The assistant reads only a compact ranked digest, never the raw export.
- **Reads.** Your LinkedIn data-export ZIP or folder (`Connections.csv`, `messages.csv` metadata only, `Invitations.csv`) and your ICP config. Of the outputs, it reads only `network-scan.md`.
- **Writes.** `network-scan.html` / `.md` / `.csv` / `.json` and `inbound-invites.csv` into an output folder you choose (keep it outside any repo - it holds real names and URLs).
- **Voice rules.** No.
- **Prereqs.** A LinkedIn data export (Settings -> Data Privacy -> Get a copy of your data). Python (standard library only, no `pip install`). Free LinkedIn plan is enough.
- **When to run.** When you want to find who in your existing network matches a target customer, hiring, or partnership profile, before a week of manual outreach.
- **Follow-up.** Copy `icp.example.yaml`, edit it, and re-run with `--icp` to narrow the list. Open `network-scan.html` to browse; `network-scan.csv` has the full rows.

### add-voice

- **Say.** "add voice", "let me talk to my OS", "voice mode", "I want to speak to it", or "set up voice".
- **Outcome.** A working local voice loop: you speak, the OS answers out loud. The default tier (Tier 0) holds the accessibility floor - no extra API key, no paid service - using your browser's built-in speech (ears and mouth) plus the reasoning CLI you already run the OS in (brain). Fully-local (faster-whisper + Piper) and realtime (a free Google AI Studio key) are opt-in upgrades.
- **Reads.** `core/identity.md` (a small head slice, for a lean brain context), the skill's `runtime/` templates and `references/`.
- **Writes.** A gitignored `voice/` runtime on your machine (`server.py`, `index.html`, `config.json` bound to your port and reasoning command, and a local-only `runtime-log.jsonl`). On "save", appends a line to `brain/log.md`.
- **Voice rules.** No.
- **Prereqs.** A local runtime (Python; runs and serves a local page - so Claude Code or any local-runtime agent). The no-key brain needs the reasoning CLI you run the OS in on PATH; without it, ears and save-to-brain still work. Chrome or Edge for built-in speech input.
- **When to run.** When you want to talk to your OS instead of typing, or hear answers while your hands and eyes are busy. The OS is complete as text; this is an optional sensory layer.
- **Follow-up.** Read `skills/add-voice/references/tiers.md` to go fully-local or add realtime; `voice-model-disclaimer.md` for the cost-and-accuracy trade; `troubleshooting.md` if the page will not reach the server.

---

### add-mouth

- **Say.** "add a mouth", "add mouth", "read this out loud", "let it speak", or "set up text-to-speech".
- **Outcome.** The OS can read an answer aloud or render it to an audio file, from any skill, without the full conversational loop. The default is your operating system's own voice (Windows SAPI, macOS say, Linux espeak) - no key, no paid service, no install, and your text never leaves the machine. Piper is a free fully-local upgrade; ElevenLabs is the one paid mouth, never a default. It speaks what it is given; it does not generate content.
- **Reads.** `voice/mouth-config.json` (the chosen engine), `.env` only if you pick ElevenLabs (for the key), the skill's `runtime/` and `references/`.
- **Writes.** A gitignored `voice/` runtime (`say.py`, `mouth-config.json`). Renders audio files only where you ask with `--out`.
- **Voice rules.** No.
- **Prereqs.** A local runtime (Python; runs your machine's speech tools - so Claude Code or any local-runtime agent). The default needs nothing else; Piper needs the binary on PATH and a voice model; ElevenLabs needs a paid key stored via `connect`.
- **When to run.** When you want answers read back while your hands and eyes are busy, or a draft heard aloud before you send it. Optional - the OS is complete as text.
- **Follow-up.** `skills/add-mouth/references/mouth-options.md` for the exact install and the cost-and-locality trade of each engine.

---

### add-hands

- **Say.** "add hands", "let it do things", "give it hands", "let it take actions", or "set up actions".
- **Outcome.** The OS can act, behind a confirm gate. Safe, reversible, local actions run freely: open a file, folder, app, or link; save a note to your log. Irreversible actions stop for an explicit yes and show you the action first - running a command is the shipped example, OFF until you turn it on and still asking every time. Sending, posting, and computer control are named as not built; the dispatcher refuses them rather than improvising, and when they land they arrive behind the same gate.
- **Reads.** `voice/hands-config.json` (the action classes and which are enabled), the skill's `runtime/` and `references/`.
- **Writes.** A gitignored `voice/` runtime (`hands.py`, `hands-config.json`). The `note` action appends a line to `brain/log.md` (reversible). No outward writes.
- **Voice rules.** No.
- **Prereqs.** A local runtime (Python; opens local apps and files - so Claude Code or any local-runtime agent). No key, no paid service for the default hands.
- **When to run.** When you want the OS to open things and capture notes for you, and you want a gate on anything riskier. Optional.
- **Follow-up.** `skills/add-hands/references/hands-and-the-confirm-gate.md` for the three action classes, how to enable the command runner, and what is not built yet.

---

### tune

- **Say.** "tune", "tune my voice", "tune the handlers", "what should I pre-program", or "make the voice faster".
- **Outcome.** It reads your local voice telemetry and proposes the next instant handler to pre-program - the request you make often that is not yet answered instantly - so it stops going through the slow reasoning path. Propose-only: it never edits a handler or a config, and it says so plainly when there is too little data to recommend anything.
- **Reads.** The gitignored `voice/runtime-log.jsonl` (Tier 0) and `voice/live-telemetry.jsonl` (realtime) the voice skills already write.
- **Writes.** Nothing. It reads and proposes.
- **Voice rules.** No.
- **Prereqs.** A local runtime (Python) and some voice usage to read. No voice telemetry yet means nothing to tune - it says so and points at `add-voice`.
- **When to run.** After using the voice loop for a while, when you want it fitted to how you actually talk. Optional.
- **Follow-up.** If a proposed handler is worth adding, that is a separate, deliberate change you confirm; `tune` only points.

---

## Role packs (front doors)

Each pack is a function a solo founder covers alone, opened by one front-door wedge skill that routes into the members. The four below join the existing `linkedin-start`; `unit-economics` is the Money pack front door. Full pack map in `skills/index.md` and per-pack manifests at `skills/<pack>-pack.md`.

### pipeline-start

- **Say.** "turn this name into a deal", "track this prospect", or "help me with my pipeline".
- **Outcome.** A name becomes a tracked deal: the OS captures the person as a record and routes you to the next move (capture, research, reach out, prep the call, or propose). The Pipeline pack front door.
- **Reads.** `core/identity.md`, `companies/prospects/<slug>.md` if present, `brain/log.md`.
- **Writes.** Read-only itself; the move it routes to (e.g. `prospect-init`) writes the record. Drafts and tracks, never sends.
- **Voice rules.** No. It routes; the writer it routes to owns the voice.
- **Prereqs.** A name and ideally a company. None other - a cold install can use it.
- **When to run.** Any open-ended "I have a name, now what" business-development ask.
- **Follow-up.** Routes to `prospect-init`, `business-context-loader`, `email-drafter`, `meeting-prep`, `proposal-writer`, `list-pruner`, `reconnect-prompt`. No dedicated slash command.

### content-start

- **Say.** "turn this idea into content", "one idea into a week of content", or "help me with content".
- **Outcome.** One idea becomes the format you need: a single post, the same idea across channels, a sequenced campaign, or a reply. The OS checks your voice first. The Content pack front door.
- **Reads.** `core/voice-profile.yml`, `brands/<slug>/voice.yml` if a brand, `brain/.snapshot.md`.
- **Writes.** Read-only itself; the writer it routes to produces the draft. Drafts in your voice, never publishes.
- **Voice rules.** Routes through the voice-coupled writers, which apply `your-voice` internally.
- **Prereqs.** A voice profile makes output yours; without it, drafts fall back to anti-AI defaults and the skill says so.
- **When to run.** Any open-ended "I have something to say, help me post it" ask.
- **Follow-up.** Routes to `linkedin-post`, `content-repurposer`, `campaign-from-theme`, `review-responder`, `voice-interview`, `brand-voice-interview`. No dedicated slash command.

### delivery-start

- **Say.** "get me ready to deliver this", "I have client work due", or "ready this for the client".
- **Outcome.** Client work gets prepped, produced, and checked: the OS routes you to the session brief, the update, the SOP, the branded document, or the ship gate, and always offers the second-pair-of-eyes check before anything ships. The Delivery pack front door.
- **Reads.** `context/clients.md`, `companies/`, `core/brand-profile.yml` for branded output.
- **Writes.** Read-only itself; the step it routes to produces or checks. Readies and checks, never sends to the client.
- **Voice rules.** Routes through voice-coupled writers (`client-update`, `sop-writer`) where they apply.
- **Prereqs.** Client history and a brand profile sharpen the output; neither blocks a delivery.
- **When to run.** Any open-ended "I owe a client something" ask.
- **Follow-up.** Routes to `meeting-prep`, `client-update`, `sop-writer`, `your-deliverable-template`, `ship-deliverable` (which composes `blind-spot-review` + `pre-send-check`). No dedicated slash command.

### decisions-start

- **Say.** "help me decide", "cut my list to one", or "I'm stuck".
- **Outcome.** The block clears: the OS reads your own state to see which kind of stuck you are in (a choice, a list, a shiny idea, a fog) and routes you to the move that clears it. The Decisions pack front door.
- **Reads.** `context/priorities.md`, `context/decisions.md`, `brain/flags.md`, `cadence/weekly-commitments.md`.
- **Writes.** Read-only itself; some moves it routes to write back (a parked decision, a re-cut list, a rolled sprint), and it reports what changed.
- **Voice rules.** No. Reasoning only; the call stays yours, with the counter-case attached.
- **Prereqs.** None. The decision skills get sharper as your state files fill.
- **When to run.** Any open-ended "I'm stuck" ask that is a block on a choice or a list, not a specific task.
- **Follow-up.** Routes to `decision-framework`, `forcing-questions`, `priority-triage`, `queue`, `strategic-read`, `strategic-analysis`, `weekly-review`. No dedicated slash command.

---

## Notes for skill authors

- Skills live under `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`, optional `allowed-tools`, `mcp_requirements`).
- Voice-coupled skills must read `core/voice-profile.yml` and degrade with a one-line warning if it contains template defaults.
- Output-producing skills should consume `brain/.snapshot.md` if present (see `skills/brain-snapshot/SKILL.md` for the pattern).
- New skills go into `skills/index.md` first (the single source for the registry and counts), then get mirrored here. CLAUDE.md and the README only carry pointers, so they need no per-skill row.
- Voice rules and anti-AI baseline live in `your-voice/SKILL.md`. Any new writer skill calls it internally.
