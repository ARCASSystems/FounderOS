---
name: session-handoff
description: >
  Package this session for a fresh chat. Trigger on "summarize this for a new session", "hand this off", "session summary", "transfer this context", "continue this in a new chat", "build a handoff", "wrap this up for next time", "create a prompt for a fresh session", "context transfer", "prepare for handoff", "we've gone deep, let's start fresh", "package this up", or any reference to transferring conversation context to a new session or a different user's Claude. Also fires when Claude detects the conversation is very long and the user mentions starting fresh, continuing later, or sharing context with someone else. Do NOT trigger for simple conversation summaries, meeting prep, or document creation tasks.
mcp_requirements: [optional: notion]
---

# Session Handoff

The goal: the receiving session picks up without re-explaining anything, regardless of whether it has installed skills, memory, or prior context.

---

## Step 1: Identify the Handoff Type

Ask if not obvious from context. The three types require different packaging:

### Type A: Same-User Continuation
The same user continuing in a fresh session within the same project. The receiving session has access to all installed skills and project memory.

**What to include:** Everything. Full context, internal strategy, file locations, skill references.
**What to strip:** Nothing. This is an internal transfer.

### Type B: Cross-User Handoff
Context being passed to a different person's Claude session. The receiving session likely has NO installed skills, NO project memory, and NO prior context.

**What to include:** Confirmed decisions, deliverable specs, guiding principles (rewritten as standalone directives), file locations they can access, and clear next actions.
**What to strip:** Internal strategy, pricing rationale, protection caps, advisor involvement, competitive positioning, anything marked as internal-only during the session. Also strip skill references - the receiving session doesn't have them.
**What to add:** Self-contained context that installed skills would normally provide. If the session used research or calculations, inline the relevant findings and numbers. The handoff must carry the knowledge that skills would otherwise supply.

### Type C: Fresh-Session Prompt
A self-contained prompt the user can paste into any Claude session and get useful work immediately.

**What to include:** Everything needed as a single prompt - context, specs, decisions, constraints, deliverable requirements.
**What to strip:** Same as Type B, plus any conversational framing. Write as instructions, not as a summary.
**Format:** Wrap the entire handoff in a prompt structure the receiving Claude can act on immediately.

---

## Step 2: Scan the Conversation

Walk through the full conversation history and extract:

1. **What was built or decided** - Not what was discussed. What was confirmed, produced, or locked in.
2. **What's still open** - Decisions pending, options still being weighed, things deferred.
3. **Strategic reasoning** - The WHY behind key decisions. Not "we discussed using profit share" but "profit share was chosen because it incentivizes margin discipline, not just volume."
4. **Assumptions made** - Anything the session built on that hasn't been verified. These are landmines for the next session if unlabeled.
5. **Files touched** - Every file created, referenced, modified, or planned. Current status of each.
6. **Skills used** - Which installed skills were active. For Type B/C handoffs, this tells you what knowledge needs to be inlined.

---

## Step 3: Build the Handoff Document

### Document Structure

```markdown
# Session Handoff: [Project/Topic Name]
Date: [Date]
Handoff type: [A: Same-user / B: Cross-user / C: Fresh prompt]
From: [Who ran this session]
To: [Who receives it - "fresh session", specific person, or "any Claude"]

---

## What Was Done
[2-3 sentences. What the session accomplished. Facts only.]

## Confirmed Decisions
[Every decision explicitly locked. State as facts, not discussion summaries.]

- [Decision 1]: [What was decided and why]
- [Decision 2]: [What was decided and why]

## Open Items
[Decisions still pending. Who needs to make them. What the options are.]

- [Open item 1]: [Options under consideration. Who decides.]
- [Open item 2]: [What's blocking resolution.]

## Guiding Principles
[Strategic reasoning, tone requirements, psychological framing, constraints that should carry forward. Written as directives.]

- [Principle]: [Why it matters]

## Files and Locations
[Every file. Current version status. Where it lives.]

| File | Location | Status |
|------|----------|--------|
| [filename] | [path or URL] | [draft / final / needs review] |

## Next Actions
[Specific tasks, in order. Not vague goals - concrete next steps.]

1. [Action]: [Exactly what to do, including file names, section numbers, specific changes]
2. [Action]: [Same level of specificity]

## Assumptions
[Anything the session built on that hasn't been verified. Label each with confidence level.]

- [Assumption]: [Confidence: high/medium/low] - [What would change if wrong]
```

### Type A Addition: Internal Context
For same-user handoffs, add after Assumptions:

```markdown
## Internal Context
[Information that matters for decision-making. Red flags, internal economics, protection caps, advisor involvement, competitive intelligence. This section exists ONLY in Type A handoffs.]
```

### Type B Addition: Inlined Knowledge
For cross-user handoffs, add after Guiding Principles:

```markdown
## Background Context
[Self-contained context the receiving session needs. Research findings, financial models, industry data, anything that installed skills would normally provide. Written as standalone facts - just state it.]
```

### Type C: Full Prompt Wrapper
For fresh-session prompts, wrap the entire document:

```markdown
# Instructions for Claude

You are continuing work on [project]. Here is the full context you need.

## Context
[Background Context section from Type B, expanded]

## What Has Been Decided
[Confirmed Decisions section]

## What You Need to Do
[Next Actions section, rewritten as direct instructions]

## Constraints
[Guiding Principles rewritten as rules]

## Open Questions
[Open Items section]

## Files
[Files section]
```

---

## Writing Rules

These are non-negotiable:

1. **Directives, not transcripts.** The receiving session has no context for "you". Write "The commission structure uses accelerating tiers" not "You said you wanted accelerating tiers."

2. **Confirmed vs. unconfirmed separation.** The single most common handoff failure is the next session treating a suggestion as a decision. If it wasn't explicitly confirmed, it goes in Open Items.

3. **Include the WHY.** "Profit share tiers use accelerating jumps because higher margins require greater discipline and the compensation should reflect increasing difficulty" - not just "tiers are 6%, 9%, 14%, 20%, 25%."

4. **Flag assumptions explicitly.** If the next session builds on an assumption without knowing it's an assumption, errors compound.

5. **Strip meta-commentary.** No "we discussed", "you mentioned", "as noted earlier", "in our conversation." State facts.

6. **For cross-user handoffs, note knowledge gaps.** If the receiving person doesn't know something the sending session assumed, flag it. "Note: [Person] has not been told about [X]. This should be shared before proceeding with [Y]."

7. **Under 2000 words.** If longer, the new session will truncate or lose focus. Cut nice-to-know and keep need-to-know.

8. **No branding in Type B/C.** The handoff is a working document, not a deliverable. No logos, no brand voice, no marketing language.

---

## Output

Save the handoff as a markdown file:
`SESSION_HANDOFF_[project-name]_[YYYY-MM-DD].md`

For Type C (fresh-session prompt), also provide the prompt as copyable text in the conversation so the user can paste it directly.

---

## Quality Check

Before presenting the handoff, verify:

- [ ] Every confirmed decision has its reasoning attached
- [ ] Every open item identifies who decides
- [ ] Every assumption is labeled with confidence
- [ ] Every file has a location and status
- [ ] Next actions are specific enough that someone unfamiliar could execute them
- [ ] For Type B/C: no internal strategy, pricing rationale, or project-specific references leaked
- [ ] For Type B/C: all skill-dependent knowledge has been inlined
- [ ] Total length is under 2000 words
- [ ] No meta-commentary or conversation-style language remains
