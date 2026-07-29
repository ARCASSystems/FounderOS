---
why: "A new OS that starts filing cards and drafting work on day one is guessing, because it has read nothing about you yet. This file makes the ramp explicit: what the OS is allowed to do this week, next week, and after that, on a schedule you can read and change."
---

# The first 30 days

Started: {{TODAY}}

This is the ramp. It says how much your OS is allowed to do for you, and when that
changes. It is here because the alternative is worse in both directions: an OS that
starts proposing work on day one is proposing from four lines it read during setup,
and an OS that never graduates stays a notepad.

Autonomy is earned on a written schedule, not on a feeling. This is the schedule.
It is a plain file. Edit the dates, skip a stage, or end the whole thing early.

---

## Stage 1 - Watching (days 1 to 7)

Dates: {{TODAY}} to {{TODAY_PLUS_6}}

**What the OS does:** reads, files what you tell it, and asks you one question a day.
That is all. The question comes from something real it noticed, not from a checklist.

**What it does not do:** file queue items on its own, draft work you did not ask for,
or tell you what your priorities should be. It has known you for a week. It has not
earned an opinion about your business yet.

**Your part:** answer the one question, and use the OS for whatever you were going to
do anyway. Ask it things. Log what happened. Every answer is context it did not have.

**Why a whole week of this:** the first proposals an OS makes are the ones that decide
whether you trust it, and a proposal built on four lines of setup answers is a coin
flip. A week of your actual work is the cheapest way to make the first real proposal
land instead of embarrass itself.

## Stage 2 - Proposing (days 8 to 21)

Dates: {{TODAY_PLUS_7}} to {{TODAY_PLUS_20}}

**What the OS does:** everything from stage 1, plus it starts proposing. Queue items
for things it noticed going quiet. Drafts when you ask for one. A named next move when
you ask what to do. The morning loop goes up to its full four questions.

**What it does not do:** anything without a yes. Every proposal is a thing you approve,
edit, or kill. Nothing it produces reaches anyone outside this folder.

**Your part:** say no often. A killed card with one line of why is worth more to the OS
than an approved one, because it teaches the shape of what you do not want. If you find
yourself approving everything, the OS is proposing too safely and you should say so.

## Stage 3 - Working (day 22 onward)

From: {{TODAY_PLUS_21}}

**What the OS does:** acts inside the gates you already have. Approving a queue item is
the decision, so the work follows without a second confirmation. The gates in
`rules/approval-gates.md` still hold, and the ones that matter do not move: nothing
leaves your machine without you, nothing is sent, nothing is published.

**What it does not do:** graduate any further on its own. There is no stage 4 that
arrives by itself. Widening what the OS may do without asking is a decision you make
once per verb, deliberately, and it is written down in `rules/approval-gates.md` when
you make it.

**Your part:** this is the point where the review loop starts paying. Once a month, look
at the roles in `roles/employees.yaml` and grade them. A role that keeps getting things
wrong gets its definition changed, not another correction from you.

---

## How this file gets used

The morning loop reads this file and checks today's date against the dates above. It
tells you which stage you are in when the stage changes, and it holds itself to that
stage's limits in between. Nothing runs on a timer, and nothing changes behind your
back: there is no scheduler here, only a date you can read.

If this file is missing, the OS behaves as though it is in stage 3. That is deliberate.
An install with no ramp file is either an older install or someone who deleted this on
purpose, and neither of them should suddenly find their OS has gone quiet.

## Changing it

Change any date. Delete a stage. Write "ended {{TODAY}}, going straight to stage 3" at
the top and the OS will read that and stop holding itself back. The ramp exists to serve
a founder who has not decided how much they trust this yet. If that is not you, say so
and it is over.

One thing worth not changing: the stage 3 line about nothing leaving your machine. That
is not part of the ramp. That is the floor, and it holds on day 400 the same as day 1.
