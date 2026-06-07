---
name: log-reply
description: >
  Capture a pasted thread (WhatsApp export, Telegram dump, email body, voice memo transcript) and structure it into the brain layer. Trigger on "log this reply", "log this thread", "I got a reply", "they responded", "here is the reply", "log this conversation", "capture this exchange", or run `/log-reply`. Extracts participants, dates, key updates, commitments, action items, and person or company mentions. Writes one structured entry to `brain/log.md` per conversation. Proposes (never auto-writes) updates to `context/clients.md` and `context/leads.md`. Different from `capture-meeting`, which is for a named meeting you ran. Different from `brain-log`, which is for free-form thoughts.
why: "Replies and threads carry the most decay-prone information in the OS. Without a fast ingest path, the commitments inside them get lost and the next session boots blind to what has changed."
enhance: "Fill context/clients.md and context/leads.md with at least the people you talk to often. The skill cross-references names against those files and proposes an add only for unknown contacts, which keeps the noise low and the signal high."
summary: "Capture a pasted thread and structure it into the brain layer."
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep"]
mcp_requirements: []
---

# Log Reply

Runs on: local-writes - creates or edits files in your OS folder; needs an agent with write access.

Routes a pasted thread into the brain layer. One log entry per conversation. Proposed updates to operating files. Approval gate before any write to `context/clients.md` or `context/leads.md`.

This skill must:
- Accept any of WhatsApp export, Telegram dump, email body, voice memo transcript. Plain pasted text is fine.
- Extract participants, dates, key updates, commitments, action items, and person or company mentions.
- Write one structured entry to `brain/log.md` per distinct conversation.
- Propose (not auto-write) updates to `context/clients.md` and `context/leads.md`. The operator confirms each proposed update before it lands.
- Fail loud when the source format is ambiguous. Ask the operator to label it. Do not guess.

## Pre-flight

1. If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
2. If `brain/log.md` does not exist, stop with: `brain/log.md missing. Re-install or run /founder-os:setup first.`
3. If `rules/approval-gates.md` does not exist, fall back to `templates/rules/approval-gates.md`. The Confirm-before gate for edits to operating files (`context/clients.md`, `context/leads.md`) still applies even if neither file is installed.

## Step 1 - Capture the paste

If the operator already pasted the thread along with the command, use that text. Otherwise ask, as a single message:

```
Paste the thread. Tell me the source: WhatsApp / Telegram / email / voice memo transcript.
```

Wait for the reply. Accept the full body.

## Step 2 - Confirm the source format

If the operator did not label the source, ask before parsing:

```
What is the source format? WhatsApp / Telegram / email / voice memo transcript.
```

Do not guess. A WhatsApp export, an email body, and a voice memo transcript all have different shapes. Misreading one as the other corrupts the extraction.

Recognised source labels:

| Label | Typical shape |
|---|---|
| WhatsApp | `[DD/MM/YYYY, HH:MM:SS] <Name>: <text>` per line (export format) |
| Telegram | `<Name>, [date]\n<text>` blocks |
| email | headers (`From:`, `To:`, `Subject:`, `Date:`) then body |
| voice memo transcript | free-form prose with no per-message headers |

## Step 3 - Detect the date

Find the conversation date in the paste:

- WhatsApp: date is in each message header.
- Telegram: date is in each block header.
- email: `Date:` header.
- voice memo transcript: usually no embedded date.

If no date is recoverable, ask:

```
When did this conversation happen? Give me a date (YYYY-MM-DD) or "today".
```

Do not invent a date.

## Step 4 - Extract structure

Per conversation, pull these fields:

- **Participants**: names from message headers or `From` / `To` lines.
- **Date(s)**: the conversation date or the date range if it spans days.
- **Key updates**: what changed since the last touchpoint (one bullet per update).
- **Commitments made**: who promised what, with deadline if stated (one bullet each).
- **Action items**: explicit next steps (one bullet each).
- **Person and company mentions**: names that appear in the text beyond the participants themselves.

If the paste contains multiple separate conversations (different threads bundled together), structure each as its own log entry with its own date and participants.

## Step 5 - Private-tag filter

Before persisting anything, scan the source text for `<private>...</private>` blocks (case-insensitive). Remove every matched block (including the tags) from the text before writing. If the entire input is wrapped in `<private>`, write nothing and report `skipped - content was tagged private.`

## Step 6 - Cross-reference person and company mentions

For each name extracted in Step 4:

1. Grep `context/clients.md` and `context/leads.md` for the name.
2. If found, note it as a known entity. The log entry will use a `#xref` wikilink to the file where the name lives.
3. If not found, flag it as a propose-add candidate for Step 8.

If `context/leads.md` does not exist on the install, treat its hits as empty and only check `context/clients.md`. The propose-add for unknown names still targets `context/leads.md` so that fresh installs get the right file created on first confirmation.

## Step 7 - Write the brain/log.md entry

The brain log entry is auto-runnable per `rules/approval-gates.md` (append to `brain/log.md` is on the Auto silent table). Write it directly.

Format (newest on top, below the file header):

```
### YYYY-MM-DD (log-reply: <source>) · #acted [S] #xref:context/clients.md

**Thread with <participants>. Source: <WhatsApp | Telegram | email | voice memo transcript>.**

- Key updates: <bullets>
- Commitments made: <bullets>
- Action items: <bullets>
- Mentions: <names captured beyond participants, or "none">

ID: log-YYYY-MM-DD-NNN
```

Use `#acted [S]` when the thread was a sales or client touch. Use `#acted [D]` when the thread was infrastructure or internal. Use `#context` when it was neither (a pure update with no action).

For the ID counter, follow the per-channel per-day rule in `templates/rules/entry-conventions.md`. Scan today's existing `log-YYYY-MM-DD-NNN` IDs in `brain/log.md`, take the highest, increment by one. Start at `001` if none exist for today.

When there are multiple separate conversations in one paste, write one heading block per conversation. Each gets its own ID.

## Step 8 - Propose updates to operating files (approval gate)

This step is where the approval gate fires. Per `rules/approval-gates.md`, edits to `context/clients.md` and `context/leads.md` are Confirm-before, not auto. The skill must propose, not auto-write.

Build the propose-list:

- For every participant in `context/clients.md`: propose a row update (last contact date, next step, response state).
- For every participant in `context/leads.md`: same.
- For every person or company mention not in either file: propose adding a row to `context/leads.md` with `Stage: Raw` per `templates/rules/entry-conventions.md`. The convention for fresh leads is `Type: Lead`, `Stage: Raw`, `Source: <label of where this lead came from, e.g. WhatsApp reply, email reply>`.

Show the operator the proposal in one block:

```
Proposed updates (approval required per rules/approval-gates.md):

context/clients.md:
- <Name>: last contact -> YYYY-MM-DD; next step -> <one line>
- <Name>: <field changes>

context/leads.md:
- ADD <Name>: Type=Lead, Stage=Raw, Source=<source label>, first contact=YYYY-MM-DD
- <existing lead>: <field changes>

Confirm each one (yes / no / edit), or reply "all yes" to accept them all.
```

Wait for confirmation. Apply only the ones the operator approves. Do not write anything else.

If the operator says no to all proposals, log that in the same brain entry as `- context updates: declined.` and stop.

## Step 9 - Output

After all writes (brain log unconditional, context updates conditional), report in under 120 words:

```
Thread captured.
- brain/log.md: <1 line summary, ID stamped>
- context/clients.md: <N rows updated, or "no change">
- context/leads.md: <N rows added or updated, or "no change">
- Mentions awaiting confirmation: <list of any deferred proposals, or "none">
Next step: <one line if a clear next step surfaced, else "none surfaced">
```

## Approval gates

The approval gates for this skill, summarised so a maintainer reading this file in isolation does not need to chase the global rules:

- Append to `brain/log.md` -> **AUTO-RUN**. Per `rules/approval-gates.md` Auto table.
- Edit `context/clients.md` -> **ASK FIRST**. Operator must confirm each proposed row update.
- Edit `context/leads.md` -> **ASK FIRST**. Operator must confirm each proposed add or update.
- Anything else (delete, send, push) -> **REFUSE**. Not in scope for this skill.

Per `rules/approval-gates.md`. The skill never silently writes to `context/clients.md` or `context/leads.md`. If neither installed nor template copy of `rules/approval-gates.md` is present, default to ask-first for any edit to an operating file.

## Edge cases

- **No clear date in the thread.** Ask the operator for the date. Do not invent one.
- **Source format unknown or not labelled.** Ask the operator to label as WhatsApp, Telegram, email, or voice memo transcript. Do not guess based on shape alone. A WhatsApp paste with the timestamps stripped looks like a voice memo transcript and parsing them the same way loses the participant attribution.
- **Multiple separate conversations in one paste.** Structure as separate log entries, each with its own date, participants, and ID. Do not merge into one entry.
- **Person mentioned not in `context/clients.md` or `context/leads.md`.** Propose adding to `context/leads.md` with `Stage: Raw` per `templates/rules/entry-conventions.md`. Operator confirms before the add lands.
- **Participant name ambiguous (only a first name in a WhatsApp export).** Cross-reference against known files. If exactly one match, use it. If multiple matches, ask the operator which one.
- **Empty paste.** Reply `No thread content found. Re-run /log-reply and paste the thread body.` and stop.
- **Whole paste wrapped in `<private>`.** Reply `skipped - content was tagged private.` and stop. No writes.

## What this skill does NOT do

- Does not subscribe to inbound messages. The skill ingests pasted content only.
- Does not send replies, draft replies, or compose anything outbound. Use `email-drafter` for that.
- Does not auto-write to `context/clients.md` or `context/leads.md`. Every change to those files passes through the operator.
- Does not enrich names from external sources (no Apollo, no LinkedIn lookup). Cross-reference is local only.

## Voice rules

Plain language. Mirror the operator's words back when summarising. No em dashes or en dashes. No banned words per `rules/writing-style.md` or its template fallback. The output of this skill is read by the operator during a session and by future skills (`brain-pass`, `weekly-review`) on later passes. Keep it scannable.

## Brain context (default)

Before producing output, read `brain/.snapshot.md` if it exists. The open-flags block can surface whether a participant in this thread already has an open commitment or parked decision. The recent decisions block can show whether the thread settles or contradicts something already decided. If the snapshot is missing (older install), proceed without it. Do not block.

## Cross-reference

- `skills/brain-log/SKILL.md` - the underlying brain capture primitive. log-reply is a wrapper that adds thread parsing and a propose-update flow on top.
- `skills/capture-meeting/SKILL.md` - the sister skill for a meeting you ran. Use that one when you have a transcript or brain dump from a meeting; use this one when you have a thread reply.
- `skills/approval-gates/SKILL.md` - the gate classifier that downstream skills call.
- `rules/approval-gates.md` (or `templates/rules/approval-gates.md`) - the gate matrix this skill cites.
- `templates/rules/entry-conventions.md` - ID stamping and Stage convention for `context/leads.md` rows.

<!-- private-tag: applies - log-reply ingests pasted speech that can contain private content (someone else's words, sensitive personal updates, financial figures). The skill applies the <private>...</private> filter in Step 5 before any persisted write. The resulting brain/log.md entry can still hold non-private body content; the private blocks are stripped, not redacted in place. Operator can wrap the entire paste in <private>...</private> to skip persistence entirely. -->
