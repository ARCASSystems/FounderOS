---
name: weekly-review
description: >
  Runs the weekly sprint review and planning cycle. Use this skill when the user says "weekly review", "weekly retro", "roll the sprint", "what happened this week", "plan next week", "Friday review", "Monday planning", "weekly planning", "sprint review", or any reference to reviewing the past week or planning the next one. Also trigger on Fridays when the user opens a session in the Founder OS root.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob"]
---

# Weekly Review - Sprint Roll and Retro

You run the weekly operating rhythm. Two modes: retro (look back) and planning (look forward). Usually both in one session.

## Step 1: Read Current State

Read these files silently:
- `cadence/weekly-commitments.md` - the current sprint
- `context/priorities.md` - broader goals
- `brain/log.md` - what actually happened this week
- `brain/flags.md` - any stalls or friction
- `cadence/daily-anchors.md` - what the daily work looked like

## Step 2: Retro

Build a retro from the data:

```
WEEK OF [date range] - RETRO

WHAT GOT DONE
- [Item]: [outcome]
- [Item]: [outcome]

WHAT SLIPPED
- [Item]: [why it didn't happen]
- [Item]: [why]

PATTERN
[One sentence. What does the pattern of done vs. slipped tell you?
Example: "Delivery work gets done. Sales work doesn't. Building is comfortable. Selling is not."]

COMMITMENTS CHECK
| Commitment | To | Status | Change? |
|------------|-----|--------|---------|
```

Present this to the user. Ask: "Anything to add or correct before I roll the sprint?"

## Step 3: Flag Check

Check for items that have rolled 2+ weeks without progress. These need a decision:
- **Kill it** - it's not actually important, remove it
- **Escalate** - move it to Must Do with a specific deliverable
- **Redefine** - the task is too vague, break it into something concrete

Present rolled items and ask which treatment each gets.

## Step 4: Plan Next Week

Ask: "What are the MUST DOs for next week? Max 3. What must be done by Friday no matter what?"

Then ask for SHOULD DOs and COULD DOs.

Build the new sprint:

```
WEEK OF [date range]

MUST DO (non-negotiable - max 3)
1. [Task]
2. [Task]
3. [Task]

SHOULD DO (important but can shift)
1. [Task]
2. [Task]

COULD DO (if time opens up)
1. [Task]

WAITING ON
- [Item]: [who/what]
```

## Step 5: Update Files

1. Write the retro into `cadence/weekly-commitments.md` (above the new sprint)
2. Update `context/priorities.md` This Week section
3. Update `brain/log.md` with a `#acted` entry noting the sprint roll
4. If any flags were resolved, update `brain/flags.md`
5. Commit: "Weekly review: roll sprint to Week of [date]"

## Marketing / Sales / Delivery Balance Check

If the founder has no paying clients yet, run this check:
- Look at the retro: categorize completed work as Marketing (content, brand), Sales (outreach, pipeline, meetings with prospects), or Delivery (building, internal systems, client work)
- Target ratio with no revenue: roughly 20% Marketing / 50% Sales / 30% Delivery
- If Delivery is dominating and Sales is under 40%, flag it: "You're building when you should be selling."

## Rules

- Be honest about what slipped. Don't soften it.
- Name the pattern. Founders often can't see their own avoidance patterns.
- Keep the sprint tight. Three Must Dos is plenty. More than that is a wish list.
- If something has rolled 3+ weeks, recommend killing it unless the user defends it.
