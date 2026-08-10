---
name: morning-loop
description: The morning answer loop. Say "morning loop", "run my morning", "what needs me today", or run /founder-os:morning-loop. Asks at most four sharp questions drawn from what is actually waiting - a blocked queue item, an unanswered ask, a provisional fact, a stale commitment - then writes every answer back into the file that owns it and silences the thing that asked. Ends with one coach line naming today's single step. Once a day.
why: "Everything the OS notices piles up in files nobody re-reads, so the same question gets raised on five mornings and answered on none. This is the human half of the loop: a few answers a day, each one landing in the file that owns it so it stops being asked."
enhance: "Run it first thing, before the day starts making the decisions for you. Answering four questions takes two minutes and is what keeps every other surface honest."
allowed-tools: ["Read", "Edit", "Write", "Grep", "Glob", "Bash(python scripts/employee_verdict.py:*)", "Bash(python scripts/unconfirmed_facts.py:*)", "Bash(python scripts/agent_runs.py:*)", "Bash(python scripts/agents_sync.py:*)"]
---

# Morning loop - four questions, then get on with it

Runs on: local-writes - it writes your answers into the files that own them. On a read-only surface, ask the questions and hand back the exact edits for you to apply.

You wake up, answer a few sharp questions, and the OS compounds. That is the whole design.

**Once a day at most.** If today's run already happened (a `#morning-loop` entry dated today in `brain/log.md`), say so and stop. A second run the same day means asking questions you already answered, which is the exact failure this loop exists to remove.

## Step 0 - which stage is this install in

Read `cadence/first-30-days.md` before anything else. It carries three dated stages and it decides how much this run is allowed to do. Compare today's date against the dates written in the file. Do not compute a stage from an install date, from the age of a folder, or from how full the files look. The dates are written down so this is a comparison, not a judgment.

| Stage | Dates | This run may |
|---|---|---|
| 1 - Watching | days 1 to 7 | ask **one** question, and only about something already sitting in a file. Write the answer back. File no queue item, draft nothing, propose no priorities. |
| 2 - Proposing | days 8 to 21 | ask up to four. Propose queue items and drafts. Nothing acts without a yes. |
| 3 - Working | day 22 on | ask up to four, and act inside `rules/approval-gates.md`. |

Three rules on top of the table:

- **A missing file means stage 3.** An older install and an operator who deleted the ramp are the same case, and neither should find their OS has gone quiet for no reason they can see.
- **A file whose dates have all passed means stage 3.** The ramp ends; it does not need closing.
- **Say it once, on the day it changes.** When today is the first day of a new stage, open with one plain line naming what changed: "Day 8. From today I will start proposing queue items and drafts, and nothing acts without your yes." Never repeat it on the other days, and never explain the ramp unprompted.

If the operator wrote an override at the top of the file (an ended line, a moved date, a deleted stage), that is the answer. The file outranks this table.

## Step 1 - gather, silently (no questions yet)

Read only what is present, and skip what is not:

0. `core/working-preferences.md` - read it first and read it as a gate on this run. Its **Active** rows already tell you what not to ask and what shape the operator wants back: a row saying "never ask me about X" removes X from the candidate list entirely, and a row about answer length applies to Step 5. This is a loop whose whole purpose is to stop asking questions that already have answers, so a preference it ignores is the loop failing at its own job. Its **Proposed** rows are candidates from `/dream` and unanswered corrections, and one of them is a legitimate question for Step 2 (below).
1. `brain/needs-attention.md` - open asks the OS has raised for you. Read `brain/needs-input.md` with it if present: `/dream` parks its questions there, and the two files are one queue split by which surface wrote them.
2. `cadence/queue.md` - ACTIVE items with no movement, and anything with a named blocker.
3. `cadence/weekly-commitments.md` - this week's MUST DO items and whether any has gone quiet.
4. `cadence/daily-anchors.md` - whether the anchor is even rolled to today.
5. `brain/unconfirmed-facts.md` if it exists - names and claims waiting to be confirmed or cut.
6. `brain/flags.md` - flags past their `Decay after:` date, which are due a keep-or-kill.
7. If `roles/employees.yaml` exists, run `python scripts/employee_verdict.py render` (a derived-view refresh, nothing else) and read `brain/employees.md` - anything showing REVIEW DUE. This is the only daily surface that carries the review trigger, so skipping it means verdicts pile up unread.
8. Yesterday's coach line: the most recent `Coach:` line in `brain/log.md`. Step 4 scores it.
9. `brain/knowledge/*.md` frontmatter if the folder exists - only the `seats:` line, and only to find notes that have none. Frontmatter, never bodies.
10. Context only, never a question: `system/quarantine.md` ACTIVE count, and any tool your hands registry records as down.

## Step 2 - pick at most four questions (the cap is hard)

In stage 1 the cap is one, not four. Take the highest-priority item below and stop there. A first-week loop that asks four questions is interviewing the operator, not learning from them.

Priority order. Never two questions about the same thing.

0. **A dated deadline outranks everything.** Anything with a real date attached - a filing, a payment, a renewal, a promise you made for a specific day - beats every undated item no matter how interesting. Bookkeeping and tidying questions rank last, behind all business state. A clock that loses its slot to a tidier question is how a deadline gets missed.
1. A decision a queue item is blocked on.
2. A review due on a recurring job ("that follow-up job's last run - ok, needs work, or failed?").
3. An ask in `brain/needs-attention.md` or `brain/needs-input.md` nobody has answered.
4. A commitment that has gone quiet: keep it, kill it, or move the date.
5. A provisional fact whose confirm-or-cut unblocks something real. One at a time, never two in one batch.
6. A flag past its decay date: keep, kill, or refresh.
6b. **A proposed working preference: promote it, or drop it.** One at a time, and only when a slot is free. Show the row in their own words with the evidence line, and ask plainly: "You said this. Want me to work that way from now on?" On a yes it moves to the Active table and starts gating output today. On a no it is deleted, not parked - a rejected preference kept "for later" comes back every morning. This is the one question that changes how the OS treats them, so it is never batched with another and never asked twice about the same row.
7. **A gap between designed intent and enacted practice.** You described how something should work, and the log shows it running differently. Ask about the gap; do not pick a side and do not quietly update the file to whichever version is newer. Three lines, no more:

   ```
   Designed intent: <what you said should happen>
   Enacted practice: <what the log shows happening>
   The gap: <the question>
   ```

   The answer goes into the entity's `profile.md` (or the owning file). This is the one question that produces something no amount of accumulation gives you: the reason a stated process and a real one diverge. Nobody writes that down unless something asks. Only raise it when both sides are actually in the files - never manufacture a contradiction to have something to ask.
8. One pattern observation, only if a slot is still free.
9. **A knowledge note nobody has routed: which seat should be reading it, if any?** The lowest-priority class here and the last to take a slot - it tidies the OS rather than moving business state, so everything above outranks it. Fires only on files in `brain/knowledge/` with **no** `seats:` field at all; a note already routed, or one carrying `seats: none`, is never raised again. **One per run, maximum**, and only when a slot is still free after the real asks - the same rule as 6b. Stage 1 never asks this one: proposing is stage 2 and up. Name the note in plain words and at most one seat: "That note on what buyers actually pay for - should the one who names your next move be reading it?" If no seat obviously fits, do not ask; leave the field absent and spend the slot elsewhere.

Each question: two or three narrow options **plus your recommendation first**. Plain language, no ids and no system jargon. "Skip" is always free and costs nothing.

**If nothing qualifies, say "Nothing needs you this morning" and stop.** Never invent a question to fill the batch. A quiet morning is a real result and the loop has to be able to report one, or you will stop trusting the mornings when it does speak.

## Step 3 - write every answer back, and silence its source

An answer that does not land in a file is a conversation, not a loop. For each answer:

- **A queue decision** - update the item in `cadence/queue.md`: move it, or close it with your one-line why on the DONE line.
- **A verdict on a recurring job** - `python scripts/employee_verdict.py verdict --employee <id> --verdict <v> --why "<your line>"`
- **A provisional fact** - `python scripts/unconfirmed_facts.py confirm --id <id> --value "<value>" --note "<who or what confirmed it>"` or `cut --id <id> --note "<why>"`. On a confirm, also write the value into the file the row names. That write is the point of the whole ledger.
- **An answered ask** - mark it answered in place in the file that raised it (`brain/needs-attention.md` or `brain/needs-input.md`) with the date and your one line. Never delete it: the answered row is the record of what you decided. An ask closed in the wrong file is still open in the right one, and it comes back tomorrow.
- **A commitment call** - update `cadence/weekly-commitments.md`. A kill gets its reason on the same line.
- **A flag call** - update `brain/flags.md`: extend the decay date with a reason, or close it with one.
- **A knowledge-routing call** - edit the note's frontmatter in `brain/knowledge/<file>.md`. A yes writes `seats: <id>` and then `python scripts/agents_sync.py apply`, so the seat's read-list actually changes today instead of at some later sync. A no writes `seats: none`. Never leave it pending: the field's state IS the record that the question is closed, and it is the only thing that stops the same note being raised tomorrow.
- **A preference call** - edit `core/working-preferences.md`: move the row from Proposed to Active with today's date, or delete the row. Never leave it sitting in Proposed with a note; the row's presence IS the open question.

**Then close the thing that asked.** This is the half that gets skipped and it is the half that matters. An answer that closes a flag has to close it in `brain/flags.md`, not only in the conversation. If a cached or rendered view still shows the item, refresh it or say plainly that it is stale. An answered question that leaves its source open comes back tomorrow wearing the same clothes, and by the third morning you have learned to ignore the loop.

Close with one entry in `brain/log.md` tagged `#morning-loop`: the questions asked, the answers, and where each one landed.

### Private tag filter

Your answers are your own words, so the exclusion tag applies to every write this loop makes. Before persisting anything, scan the answer text for `<private>...</private>` blocks (case-insensitive), and remove every matched block including the tags. If a whole answer is wrapped in `<private>`, write nothing for it and report "skipped - content was tagged private." Act on it in the conversation, and do not put it in a file.

This matters more here than almost anywhere else in the OS. A morning answer is the most candid thing you will type all day, and some of it belongs in the decision but not in a permanent record.

## Step 4 - the coach line (every run, and it never costs a question slot)

Two halves, then one line.

**Score yesterday.** If yesterday's `Coach:` line named a step, score it from the files first: did its queue item close, did the outreach date move, is there a log entry for it? Then it is `done` or `slipped` on evidence, with no question spent. If the files cannot tell and a question slot was free, your answer scores it. Otherwise record `none`. Unscored is honest. Guessed is not.

**Name today's one step.** Draw it from the same files, in this order: the sharpest live MUST DO this week, else the oldest waiting queue item (a `Review commitment:` item from your monthly review lands here naturally), else one outreach touch if the last one is more than fourteen days old. One step, doable today, **your own hands** - never a build the OS should be running itself.

Write it into the closing log entry in exactly this shape, because the weekly and monthly reviews read this line:

```
Coach: yesterday=done|slipped|none | today: <the one step>
```

A run of slipped days is coaching material for the monthly review. It is never a scolding here.

## Step 5 - report (under 15 lines)

Questions asked, answered, skipped. Where each answer landed. Anything deferred and why. The last line is the coach line in plain words: "Yesterday's step: done. Today's one step: <step>." No summary prose after that.

## What this loop measures

Worth stating because it changes which questions are worth asking: the loop tracks whether things **moved**, not whether they were touched. A queue item closed is not progress. A customer replied, a decision got made, a commitment landed - that is progress. When you are choosing between two questions, the one whose answer moves something real wins over the one that tidies the OS.

## Rules

- Four questions maximum, one run per day, and skipping everything costs nothing.
- No new writers. This loop asks and files. It never sends anything, never runs a recurring job, never starts a build.
- It must survive a freeform answer. If you reply "1 yes, 2 skip, 3 the second one", read the intent. Never ask a person to answer in a tidier format.
- Writing rules apply. No em dashes.

---

## Record the run (the closing act, when this runs as a seat)

If `roles/employees.yaml` carries the `daily-assistant` row, close with one line so the run leaves a trace whether or not anyone was watching:

    python scripts/agent_runs.py record --seat daily-assistant --trigger "morning loop"         --read "brain/needs-attention.md,cadence/queue.md,brain/flags.md" --produced "brain/log.md" --outcome ok

Use `--outcome refused` (with `--could-not "<why>"`) when the run stopped because today's loop had already happened, and `--outcome failed --could-not "<why>"` when it broke - the script requires the reason for both, so a failure with no reason is never a silent no-record. A refusal is not a failure and the log distinguishes them. Skip this silently if the script or the registry is absent, and never mention it in your reply - it is bookkeeping, not output.
