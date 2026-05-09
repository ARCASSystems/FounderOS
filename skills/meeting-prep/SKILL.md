---
name: meeting-prep
description: >
  Prep for a meeting or debrief one after. Trigger on "prep me for my call with [name]", "prep for a meeting", "prepare for a call", "get me ready for", "meeting notes", "debrief this meeting", "summarize the call", "what should I ask in", or any reference to preparing for or processing meetings, calls, interviews, or conversations. Also fires when the user mentions an upcoming meeting and needs context, talking points, or questions.
mcp_requirements: [optional: gcal, optional: gmail]
---

# Meeting Prep and Debrief

You help the founder prepare for and process meetings. Two modes: prep (before) and debrief (after).

## Before You Write

Read three files so the brief is specific, not generic.

1. **`stack.json`** at the Founder OS root. Look at `calendar` (gcal vs outlook), `meeting_notes` (granola vs otter vs notion), and `email_platform`. Reference the user's actual MCP, not a hardcoded one. If `calendar: outlook_calendar`, do not call out a Gmail integration.
2. **`context/clients.md`** for any prior interaction history with this person or company. Pull the last touch, current status, and any open commitments.
3. **`core/identity.md`** for the founder's relationship framing - first name, business name, role.

If `stack.json` is null for a field, do not invent. Note "no calendar integration configured" and proceed.

## Brain context (default)

Before producing output, read `brain/.snapshot.md` if it exists.

If the snapshot is missing, run:

    python scripts/brain-snapshot.py --write

Then read it. If the snapshot script is also missing (older install), proceed using only the profile files. Do not block.

The snapshot tells you what flags are open, what the user is working on this week, and what the latest staleness state is. Apply this context to your output where it is relevant. Do not surface every snapshot field in every output - use judgment. For meeting prep, open flags often surface unresolved threads with the same person, and recent decisions tell you what is locked in already so the brief does not re-open settled questions.

## Brain pass (auto)

Before writing the meeting brief, invoke the `brain-pass` skill (`skills/brain-pass/SKILL.md`) with this question, substituting `<subject>` for the meeting subject (the person, company, or topic):

> What do we know about `<subject>`? Past interactions, open commitments, unresolved threads, sensitivities.

Read the structured Answer / Evidence / Confidence / Gaps block the pass returns. Use it to shape the brief:

- Past commitments become explicit talking points or "watch for" items.
- Unresolved tension becomes a sensitivity flag in PREP ITEMS.
- A first-interaction answer routes to the New Prospect Detection block below.
- Cite the entry IDs from Evidence in the brief so the founder can open the source if needed.

If `skills/brain-pass/SKILL.md` is missing (older install), fall back to `python scripts/query.py --mode timeline --anchor <subject-slug>` and then `python scripts/query.py "<subject>"` if no anchor matches. Do not block.

## New Prospect Detection

If the meeting is with a new prospect (someone the founder hasn't worked with before):
1. **Check what context exists.** If the founder has already done research on this company, use that as the foundation for the meeting brief.
2. **If no context exists,** offer to research the company before building the brief: "Want me to look up [company] before building the meeting brief? It'll give us context, likely pain points, and questions to bring."
3. **If the founder wants to skip research,** proceed with meeting-prep using whatever context is available, but note what's missing.

## Pre-Meeting Brief

When the founder says they have a meeting coming up, build a brief. Ask for what you don't know, but don't over-ask if context is already clear.

### What You Need (ask if not provided)

1. **Who** - Name, role, company, relationship history
2. **What** - Type of meeting (sales, client check-in, partner, investor, team)
3. **Goal** - What does the founder want to walk away with?
4. **Context** - Any background, previous conversations, current situation

### Brief Structure

```
MEETING BRIEF
---
Who: [Name, Role, Company]
When: [Date/Time if known]
Goal: [One sentence - what success looks like]
---

CONTEXT
[2-3 sentences of relevant background.]

THEIR LIKELY PRIORITIES
[What does the other person care about? Top 2-3 priorities or pain points.]

QUESTIONS TO ASK
[3-5 strategic questions specific to this meeting's goal.]

WATCH FOR
[1-2 things to pay attention to. Signals, red flags, opportunities.]

PREP ITEMS
[Anything the founder should review, bring, or have ready.]
```

### Question Strategy

Questions should follow this priority:
1. **Discovery questions** - What don't you know yet that matters?
2. **Validation questions** - What assumptions need testing?
3. **Decision questions** - What do you need answered to move forward?
4. **Relationship questions** - What builds trust and shows you've done your homework?

Good questions are specific. Not "How's business?" but "You mentioned last time you were hiring for ops - did you fill that role?"

## Post-Meeting Debrief

When the founder describes what happened in a meeting, capture it structured.

### Debrief Structure

```
MEETING DEBRIEF
---
With: [Name, Company]
Date: [Date]
---

KEY TAKEAWAYS
[What did you learn? What surprised you?]

DECISIONS MADE
[Any commitments, agreements, or choices locked in.]

ACTION ITEMS
-> [Founder]: [task] by [date]
-> [Other person]: [task] by [date]

FOLLOW-UP
[What happens next? When is the next touchpoint?]

NEXT STEP
[What skill or task comes next - proposal, playbook, follow-up email?]

NOTES
[Anything else worth remembering.]
```

## Formatting Rules

- Use simple hyphens (-) not em dashes or en dashes
- Arrows (->) for action items
- Keep it scannable - this is a reference document, not prose
- Bold only for section headers and critical items
- No filler. Just what happened and what's next.

## If Context Is Thin

If the founder gives you minimal info (just a name and "I have a call"), do a quick web search if tools are available. Look for their LinkedIn, company info, and any mutual context. Build the brief from what you find. Flag anything you're not sure about.
