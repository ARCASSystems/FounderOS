# Founder OS Commands Reference

The full reference for every slash command. The README's command table tells you the **outcome** in one line and the natural-language phrase that triggers each one. This file tells you everything else: arguments, what runs, what changes on disk, what appears in chat, and what to run next.

FounderOS routes on natural language. Each command below leads with the natural-language phrase the founder would actually say in chat. The slash command appears alongside as a power-user shortcut. If you forget what's available, say "show me what you can do" (or run `/founder-os:menu`) and the OS returns 5 to 7 capability suggestions tailored to your current state.

Each command has seven labels.

- **Or say.** The natural-language phrase the founder would say in chat to trigger the same skill.
- **Outcome.** What appears in chat after the command finishes.
- **Args.** Required and optional arguments.
- **Writes.** Files created or updated. `Read-only` if nothing.
- **Prereqs.** What must already exist for the command to work.
- **When to run.** The signal or trigger that makes this the right next move.
- **Follow-up.** What to run after.

Path B users (manual git clone) drop the `/founder-os:` prefix. So `/founder-os:setup` becomes `/setup`. The plain bare commands (`/today`, `/next`, `/pre-meeting`, `/capture-meeting`) work the same on both paths.

If a command is not behaving as documented, say "audit the OS" (or run `/founder-os:audit`) to confirm the OS surface is intact, then [open an issue](https://github.com/ARCASSystems/FounderOS/issues).

---

## Setup and identity

### `/founder-os:setup`

- **Or say.** "set up Founder OS"
- **Outcome.** A guided interview of about 15 to 20 prompts across six phases ends with your full operating layer on disk. Final summary lists every file written.
- **Args.** None.
- **Writes.** `core/identity.md`, `context/priorities.md`, `context/decisions.md`, `context/clients.md`, `context/companies.md`, `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, `brain/log.md`, `brain/flags.md`, plus the auto-memory `MEMORY.md` index.
- **Prereqs.** Founder OS plugin or repo present. Nothing else.
- **When to run.** First session, or when you want to re-do setup with fresh answers.
- **Follow-up.** `/founder-os:voice-interview`, then `/founder-os:brand-interview`. Together these complete Day 1.

### `/founder-os:voice-interview`

- **Or say.** "set up my voice profile"
- **Outcome.** A short interview (about 3 writing samples plus 6 shaping questions, ~10 minutes) plus a voice profile written to disk. The interview captures rhythm, openings, closings, contractions, idiosyncrasies, and reading level.
- **Args.** None.
- **Writes.** `core/voice-profile.yml`.
- **Prereqs.** `/founder-os:setup` complete (so `core/` exists).
- **When to run.** Right after setup, or when your voice has shifted and the writing skills no longer sound like you.
- **Follow-up.** `/founder-os:brand-interview`. Then test with `/linkedin-post` on a small idea and confirm the output sounds like you.

### `/founder-os:brand-interview`

- **Or say.** "set up my brand profile"
- **Outcome.** A brand profile and an assets folder. Captures colors, fonts, logo paths, footer text, page size and margins.
- **Args.** None.
- **Writes.** `core/brand-profile.yml`, `core/brand-assets/` folder structure.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** Once Day 1 is otherwise stable. Skip if you do not produce branded deliverables yet.
- **Follow-up.** Drop your logo files into `core/brand-assets/` per the paths the interview captured. Test with `your-deliverable-template`.

---

## Discovery

### `/founder-os:menu`

- **Or say.** "show me what you can do" / "what's available"
- **Outcome.** A tailored list of 5 to 7 capabilities scored against your current state. Each row has the natural-language phrasing first, the slash command shortcut parenthetical, and a one-sentence why-now. The single entry point if you forget what's available. Output ends with: "These are tailored to your current state. Say any of the natural-language phrases above. Or ask Claude anything in plain English - most of FounderOS routes by what you say, not what you type."
- **Args.** None.
- **Writes.** Read-only.
- **Prereqs.** Founder OS plugin or repo present. Works on a brand-new install (returns the Day-1 starter set: voice-interview, brand-interview, priority-triage, today, ingest).
- **When to run.** Any time you forget what's available, or when current state changes (new flag, stale cadence, new initiative) and you want to know what to do next.
- **Follow-up.** Say any of the natural-language phrases the menu surfaces, or run the slash command shortcut alongside.

---

## Audit and health

### `/founder-os:status`

- **Or say.** "check my OS readiness"
- **Outcome.** A weighted readiness score and the next 3 high-impact moves to run. Score breaks down by Identity, Priorities, Decisions, Cadence, Voice.
- **Args.** None.
- **Writes.** Read-only.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** Any time. Especially after a long break, before a big push, or when you cannot decide what to do.
- **Follow-up.** Run the top recommended move. If the score is below 60, run `/founder-os:audit` for the full diagnostic.

### `/founder-os:audit`

- **Or say.** "audit the OS"
- **Outcome.** One composite health report covering readiness, wiki state (broken links, orphans, stale entries), brain staleness, voice completeness, and quarantine state. Each section gets a pass or fail.
- **Args.** None.
- **Writes.** Read-only. Optionally writes a dated audit file under `audit-YYYY-MM-DD.md` (gitignored).
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** Weekly, or whenever the OS feels stale, or before a major rebuild.
- **Follow-up.** Each failed section names the skill that fixes it (`lint`, `wiki-build`, `dream`, `voice-interview`).

### `/founder-os:lint`

- **Or say.** tool invocation (run `/founder-os:lint` directly)
- **Outcome.** A list of broken `[[wikilinks]]` (ambiguous slugs now name the deterministic pick the resolver would choose, not just the candidate list), orphan files (no inbound links), entries past their `Decay after:` date, entries that LACK a `Decay after:` field where the anchor date is 30+ days old (soft signal, prefixed `decay-gap`, not a defect), `brain/log.md` past its 300-line cap (reminder, prefixed `log-cap`, not a defect), provenance gaps in `raw/`, and possible contradictions across files.
- **Args.** None.
- **Writes.** Read-only.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** Weekly, or after a heavy `/dream` session, or before `/founder-os:audit`.
- **Follow-up.** Fix the named files manually. Run `/founder-os:wiki-build` to refresh the graph.

### `/founder-os:wiki-build`

- **Or say.** tool invocation (run `/founder-os:wiki-build` directly)
- **Outcome.** A refreshed wiki graph extracted from every `[[wikilink]]` across markdown files in the OS. Reports new edges added and dead edges removed.
- **Args.** None.
- **Writes.** `brain/relations.yaml` (the auto section between markers, manual edges are preserved).
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** After adding cross-references in a session. Before `/founder-os:lint`.
- **Follow-up.** `/founder-os:lint` to verify integrity, then `/founder-os:query` to traverse.

---

## Retrieval and recall

### `/founder-os:query <question>`

- **Or say.** "find the file about [topic]" / "search my OS for [topic]"
- **Outcome.** Top 3 to 5 OS nodes that match your question, each with a stable ID, a one-line context, and the multi-hop path that reached it.
- **Args.** One free-form question (default index mode), or `--mode timeline --anchor <slug-or-id>` for a 7-day window, or `--mode full --ids <a,b,c>` for full bodies.
- **Writes.** Read-only.
- **Prereqs.** `/founder-os:setup` complete. `brain/relations.yaml` exists (run `/founder-os:wiki-build` once).
- **When to run.** When you remember a topic but not the file. When you want surrounding entries by date. When you have a known ID and need the body.
- **Follow-up.** If too many matches, use `/founder-os:brain-pass` for synthesis. If you want the body of a specific result, re-run with `--mode full --ids <id>`.

### `/founder-os:brain-pass "<question>"`

- **Or say.** "what do I know about [topic]" / "synthesise across the brain"
- **Outcome.** A synthesised answer in four sections: Answer (2 to 4 lines), Evidence (cited entry IDs), Confidence (high / medium / low with reason), Gaps (what the brain does not know that would change the answer).
- **Args.** One quoted question.
- **Writes.** Read-only.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** A question spans multiple brain files. A keyword query returns too many matches. You want reasoning, not raw text dumps.
- **Follow-up.** Open the cited IDs with `/founder-os:query --mode full --ids <ids>` if you need the source content.

---

## Cadence and review

### `/today`

- **Or say.** "what's on for today?"
- **Outcome.** A 20-line one-screen view of today: anchor, immovable commitments, deep work window, top open decisions, active flags, last 3 log entries, next calendar event.
- **Args.** None.
- **Writes.** Read-only.
- **Prereqs.** `/founder-os:setup` complete. Today's `## Today: YYYY-MM-DD` line in `cadence/daily-anchors.md` rolled forward.
- **When to run.** First thing in the morning. After a context switch.
- **Follow-up.** If the anchor is empty, set it. Run `/next` for the single recommended action.

### `/next`

- **Or say.** "what should I focus on next?"
- **Outcome.** One recommended next action across priorities, deals, and cadence. Not a list. One action with a one-line reason.
- **Args.** None.
- **Writes.** Read-only.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** Whenever you cannot decide what to do next, or after a long break.
- **Follow-up.** Run it. Or push back if the recommendation is wrong, and the model adjusts.

### `/pre-meeting <subject>`

- **Or say.** "prep me for my call with [name]"
- **Outcome.** A pass-or-fail verdict on the pre-meeting gate. Pass requires a capture artifact (notes file, doc link, or transcript path) and an ask (what you want from the meeting). Fail names what is missing.
- **Args.** Subject (person, company, or meeting topic). Use a slug.
- **Writes.** On pass, an intent entry in `brain/log.md` with `#pre-meeting` tag and a stable `log-YYYY-MM-DD-NNN` ID.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** 10 to 30 minutes before any meeting that matters.
- **Follow-up.** `meeting-prep` skill if you need a brief. After the meeting, `/capture-meeting`.

### `/capture-meeting <subject>`

- **Or say.** "capture this" / "log this"
- **Outcome.** A routed summary: meeting log entry in `brain/log.md`, updated client status in `context/clients.md` if the subject matches an existing row, and any new open commitments named.
- **Args.** Subject (matches the slug used for `/pre-meeting`).
- **Writes.** `brain/log.md`, `context/clients.md`, optional `context/decisions.md` if a decision was made.
- **Prereqs.** `/founder-os:setup` complete. A transcript or brain dump pasted in chat or available at a path.
- **When to run.** Right after the meeting, while context is fresh.
- **Follow-up.** Open the named files to verify routing. Add anything the model missed.

---

## Capture and processing

### `/founder-os:rant`

- **Or say.** "I want to rant" / "let me dump something"
- **Outcome.** A new `brain/rants/<YYYY-MM-DD>.md` file holding your raw dump verbatim. No structure asked. No editing.
- **Args.** None. Pasted or dictated content follows the command.
- **Writes.** `brain/rants/<YYYY-MM-DD>.md`. Appends if today's file exists.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** Mid-day, end-of-day, or whenever you need to think out loud without structure.
- **Follow-up.** `/founder-os:dream` later in the day or week to process unprocessed rants into structured entries.

### `/founder-os:dream`

- **Or say.** "process my rants" / "dream on the rants"
- **Outcome.** A 5-line digest in `brain/log.md` with stable-ID citations, plus new entries in `brain/patterns.md`, `brain/flags.md`, `brain/decisions-parked.md`, `brain/needs-input.md` as warranted. Each rant marked processed. If the opt-in observation log is enabled, today's tool calls are rolled into an OBSERVED section.
- **Args.** None.
- **Writes.** `brain/log.md`, `brain/patterns.md`, `brain/flags.md`, `brain/decisions-parked.md`, `brain/needs-input.md`, `context/clients.md` if a client signal surfaces. Marks rants processed in place.
- **Prereqs.** `/founder-os:setup` complete. At least one unprocessed rant in `brain/rants/`.
- **When to run.** End of day, or when `brain/rants/` has 2+ unprocessed files.
- **Follow-up.** `/today` or `/next` to act on any new flags.

---

## Ship gate

### `/founder-os:forcing-questions <initiative>`

- **Or say.** "I'm thinking of starting [X]" / "should I do this"
- **Outcome.** Six yes/no answers (vague done state, phantom user, scope creep, false urgency, sunk-cost trap, opportunity cost) plus a verdict: start, kill, postpone, or scope down.
- **Args.** Initiative name or one-line description.
- **Writes.** Read-only. Optional log entry to `brain/log.md` if you ask for one.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** Before starting any new initiative, or when scope is creeping mid-task.
- **Follow-up.** If the verdict is start, document the initiative in `context/priorities.md`. If kill or postpone, log it.

### `/founder-os:ship-deliverable <path>`

- **Or say.** "is this ready to send" / "ship-check this"
- **Outcome.** A composite pass-or-fail verdict across template fit (your-deliverable-template), anti-AI scan (your-voice rules), blind-spot evidence (legal, contract, data, timing, relationship, upside, walkaway), and pre-send checks (voice, source truth, personalization).
- **Args.** Path to the deliverable file.
- **Writes.** Read-only. The deliverable is not modified. The skill only reports.
- **Prereqs.** `/founder-os:setup` complete. Voice profile filled. Brand profile filled if the deliverable is branded.
- **When to run.** Final gate before any deliverable leaves your machine.
- **Follow-up.** Fix every issue named, then re-run. Loop until the verdict is pass.

---

## Plugin lifecycle

### `/founder-os:ingest <source>`

- **Or say.** "ingest this" / "save this source"
- **Outcome.** A new file in `raw/<source>.md` with provenance frontmatter (URL or path, captured date, source title), plus proposed wiki updates you approve before they land.
- **Args.** A URL, a file path, or pasted text with a name.
- **Writes.** `raw/<source>.md`. Optionally `brain/relations.yaml` if you approve wiki edges.
- **Prereqs.** `/founder-os:setup` complete.
- **When to run.** Whenever you read or watch something worth preserving with provenance.
- **Follow-up.** `knowledge-capture` to distil the takeaways, or `/founder-os:wiki-build` to refresh the graph.

### `/founder-os:update`

- **Or say.** "update Founder OS" / "pull the latest"
- **Outcome.** A diff of System Layer files (skills, templates, commands, hooks) between your installed version and the latest release. Asks for confirmation before applying. Subcommand `check` previews without writing. Subcommand `rollback` restores the previous System Layer.
- **Args.** Optional `check` or `rollback`.
- **Writes.** `skills/`, `templates/`, `.claude/commands/`, `.claude/hooks/`. Personal data (`core/`, `context/`, `cadence/`, `brain/`) is never touched.
- **Prereqs.** Plugin installed via Path A (marketplace) or Path B (git clone).
- **When to run.** When a new release ships and you want it. Always run `check` first.
- **Follow-up.** Open the changelog (`CHANGELOG.md`) to read what changed.

### `/founder-os:uninstall`

- **Or say.** "uninstall Founder OS"
- **Outcome.** A confirmation list of every file and folder that will be removed. Default mode preserves your personal data and only removes the System Layer. `--purge` removes everything.
- **Args.** Optional `--purge`.
- **Writes.** Default removes `skills/`, `templates/`, `.claude/`, `scripts/`. `--purge` additionally removes `core/`, `context/`, `cadence/`, `brain/`, `raw/`, `clients/`, `drafts/`, `exports/`, `reports/`, `audit-*.md`.
- **Prereqs.** Plugin installed.
- **When to run.** When you want a clean slate, or when you are switching to a different OS.
- **Follow-up.** None. Or run `/founder-os:setup` again if you kept your data and want to rebuild the System Layer.

---

## Notes for command authors

- Commands live in `.claude/commands/<name>.md` with YAML frontmatter (`description`, `argument-hint`, `allowed-tools`).
- Each command file should run a single SKILL.md end to end. Logic lives in the skill, not the command.
- The command file's job is argument parsing and routing. The skill file's job is the actual procedure.
- New commands must be added to this file under the right section, plus the README's slash commands table, plus `skills/index.md`.
