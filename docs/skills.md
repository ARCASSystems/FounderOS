# Founder OS Skills Reference

The full reference for every skill. The README's three skill tables tell you the **outcome** in one line. This file tells you everything else: how to invoke each skill in plain English, what it reads, what it writes, whether it inherits your voice, what must exist before it works, and what to run after.

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
- **Outcome.** A weighted readiness score across Identity, Priorities, Decisions, Cadence, Voice. Plus the next 3 high-impact moves.
- **Reads.** `core/identity.md`, `core/voice-profile.yml`, `context/priorities.md`, `context/decisions.md`, `cadence/`, `brain/flags.md`.
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
- **Reads.** `companies/<slug>.md` (or your equivalent), `context/clients.md`.
- **Writes.** Read-only.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete. At least one company file under `companies/`.
- **When to run.** When switching focus to a different company or project. Start of a working block scoped to one entity.
- **Follow-up.** Skill named in the "next move". No dedicated slash command.

### ingest

- **Say.** "ingest this", "process this source", or "save this transcript".
- **Outcome.** A new file in `raw/<source>.md` with provenance frontmatter (URL or path, captured date, source title), plus proposed wiki updates you approve before they land.
- **Reads.** Source URL, file, or pasted text.
- **Writes.** `raw/<source>.md` always. After your approval: `context/entities/`, `context/decisions.md`, `brain/patterns.md`, `cadence/`, or company files (whichever the proposal targets), plus a one-line trace in `brain/log.md`.
- **Voice rules.** No.
- **Prereqs.** `founder-os-setup` complete.
- **When to run.** Whenever you read or watch something worth preserving with provenance.
- **Follow-up.** `knowledge-capture` to distil. `wiki-build` to refresh the graph. Slash command: `/founder-os:ingest`.

---

## Notes for skill authors

- Skills live under `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`, optional `allowed-tools`, `mcp_requirements`).
- Voice-coupled skills must read `core/voice-profile.yml` and degrade with a one-line warning if it contains template defaults.
- Output-producing skills should consume `brain/.snapshot.md` if present (see `skills/brain-snapshot/SKILL.md` for the pattern).
- New skills must be added to this file, plus the README's three skill tables, plus `skills/index.md`.
- Voice rules and anti-AI baseline live in `your-voice/SKILL.md`. Any new writer skill calls it internally.
