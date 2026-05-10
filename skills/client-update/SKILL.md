---
name: client-update
description: >
  Write a client-facing status update or milestone report. Trigger on "update the client", "write a status update", "project update", "send a progress report", "milestone update", "weekly update for", or any variation of client-facing project communication. Also fires when the user describes project progress and needs it packaged for a client. Reads `core/voice-profile.yml` and writes in the founder's voice.
allowed-tools: ["Read", "Write", "Edit"]
mcp_requirements: []
---

# Client Update

Writes client-facing communications. Updates build trust through transparency, not polish.

## Before you write

Before producing output, read `core/voice-profile.yml`. If the file is missing OR contains template defaults (lines starting with `{{`, values like `<your tone here>`, `[CHOOSE`, `[example:`, or `[NOT SET]`), STOP and tell the user:

> Your voice profile is empty. Run `/founder-os:voice-interview` first, or this output will sound like Claude defaults rather than you. Want me to run the interview now, or proceed with defaults anyway?

If the user chooses to proceed with defaults, write the update using the universal anti-AI baseline from `your-voice` and clearly label that the voice profile was not applied. Do not pretend the update is voice-coupled.

If the founder has filled `core/brand-profile.yml`, follow the visual brand for any branded version of the update (PDF, doc, etc.). Plain-text updates do not need brand assets.

If the engagement has a context file under `context/companies/<client>.md` or similar, read it for project specifics, named milestones, and the agreed scope.

## Core Principles

**Lead with outcomes, not activities.** "Your hiring process now takes 3 days instead of 12" beats "We reviewed and optimised the hiring workflow."

**Bad news travels fast.** If something is off track, say it immediately. Don't bury it.

**Short and structured.** The client should get the picture in 30 seconds of scanning.

**Specific dates, not soft adverbs.** No "soon", no "in the coming weeks". Either commit to a date or admit you don't have one yet.

## Weekly / Regular Update

```
PROJECT UPDATE: [Engagement Name]
Client: [Company Name]
Period: [Date range]
STATUS: [On Track / Attention Needed / Behind]

COMPLETED THIS PERIOD
-> [Outcome]
-> [Outcome]

IN PROGRESS
-> [What's being worked on] - [Expected completion]

COMING NEXT
-> [What's planned]

NEEDS FROM YOU
-> [Decisions, access, feedback needed]
```

## Milestone Update

```
MILESTONE REACHED: [Name]
Date: [Date]

WHAT WE DELIVERED
[2-3 sentences on impact]

DELIVERABLES
-> [Item delivered]

WHAT THIS MEANS FOR YOU
[What changes now]

NEXT MILESTONE
[What comes next, when]
```

## Issue / Delay Communication

```
SITUATION
[What happened. Direct.]

IMPACT
[What this means for timeline or deliverables]

WHAT WE'RE DOING
[Actions to resolve]

REVISED TIMELINE
[New dates if applicable]
```

## Writing Rules

- Simple hyphens (-) not em or en dashes
- Arrows (->) for lists
- Specific dates, not "soon" or "in the coming weeks"
- No padding. If a section has nothing, skip it.
- Apply the founder's voice profile if available. If not, default to plain, direct sentences.

## Self-check before sending

1. Could the client read this in 30 seconds and know status, what's coming, and what they need to do?
2. Is bad news in the first three lines, not the last?
3. Are all dates specific, or is anything hidden behind "soon"?
4. Did you run the result against the universal anti-AI baseline (banned words, em dashes, rule of three, negation-contrast)?
5. If the engagement has a brand profile and this is going out as a PDF or doc, did you use `your-deliverable-template` to apply it?
