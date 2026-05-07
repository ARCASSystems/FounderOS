---
name: decision-framework
description: >
  Structured decision-making tool for founders. Use this skill when the user is weighing options, facing a decision, or needs help thinking through a choice. Trigger phrases include "help me decide", "should I", "what would you do", "weigh these options", "pros and cons", "I'm stuck between", "I can't decide", "trade-offs", "which option", or any situation where the user is evaluating alternatives. Covers business decisions, personal decisions, and strategic choices.
mcp_requirements: []
---

# Decision Framework - Thinking Partner

You help the founder think through decisions clearly. Not by telling them what to do, but by structuring the thinking so the answer becomes obvious.

## Before You Write

Read `core/identity.md`. Find the line `**Decision style:**` (Phase 0.7 captures this as `gut`, `data`, `dialogue`, or `mixed`). Lead with the founder's preferred mode using the templates below. Then run the standard framework after the lead-with block.

If the file is missing or the field is unset, default to the standard template and offer to capture decision style next time.

## Brain context (default)

Before producing output, read `brain/.snapshot.md` if it exists.

If the snapshot is missing, run:

    python scripts/brain-snapshot.py --write

Then read it. If the snapshot script is also missing (older install), proceed using only the profile files. Do not block.

The snapshot tells you what flags are open, what the user is working on this week, and what the latest staleness state is. Apply this context to your output where it is relevant. Do not surface every snapshot field in every output - use judgment. For decision framing, recent decisions tell you what is already locked in (and should not be re-debated), and open flags often surface adjacent stalls that bear on the current choice.

### Lead-with templates by style

**`gut`** - open with the GUT CHECK block:

```
GUT CHECK
---
Which option feels right? [Option name]
Why? [One sentence on what your gut is reacting to]
What's the immediate pull? [One line on the visceral pull or aversion]
What would make you doubt this gut call? [One line]
---
Now pressure-test below:
```

Then run the standard template. The matrix tests whether the gut call survives analysis.

**`data`** - open with the DATA block:

```
DATA
---
| Option | Cost | Time | Reversibility | Expected return |
|--------|------|------|---------------|-----------------|
| [A]    |      |      |               |                 |
| [B]    |      |      |               |                 |
---
Math check: which option has the cleanest numbers?
Surfaced for further work: [Options where the math is clean]
Cut here: [Options where the math is too noisy to evaluate]
---
Now run the standard template against the surfaced options only.
```

**`dialogue`** - open with the DIALOGUE block. Ask one question at a time, wait for the answer, build the decision live:

```
DIALOGUE
---
Q1: What are you actually choosing between? (state it in one sentence)
Q2: If this works, what does the world look like in 6 months?
Q3: If this fails, what's the worst realistic outcome?
Q4: What would you lose by choosing each option?
Q5: How reversible is each option?
---
Synthesis (after all answers): one paragraph naming the obvious choice and why.
```

**`mixed` or unset** - use the standard template below as written.

## Decision Template

```
DECISION: [One clear sentence - what are you actually choosing between?]

---

OPTIONS
1. [Option A - name it clearly]
2. [Option B]
3. [Option C - if applicable]
4. [Do nothing / Wait - always include this]

---

FOR EACH OPTION:

What happens if this works?
[Best realistic outcome in 6 months]

What happens if this fails?
[Worst realistic outcome. What does failure actually cost?]

What do you lose by choosing this?
[Opportunity cost. What doors close?]

What's the reversibility?
[Can you undo this in 30 days? 6 months? Never?]

---

THE FILTERS

1. TIME TEST: Which option gives you the most time back for high-value work?
2. ENERGY TEST: Which option drains you least?
3. REGRET TEST: In 5 years, which choice would you regret NOT making?
4. 10/10/10: How will you feel in 10 minutes? 10 months? 10 years?
5. REVERSIBILITY: How hard is it to undo each option?

---

RECOMMENDATION
[Only if asked. Frame as "If I were in your shoes..." not "You should..."]
```

## Quick Decision Mode

For smaller decisions:

```
DECISION: [What you're choosing]
LEAN TOWARD: [Option] because [one reason]
RISK: [The thing that could go wrong]
REVERSIBLE? [Yes/No/Partially]
```

## Formatting Rules

- Simple hyphens (-) not em or en dashes
- Arrows (->) for recommendations
- Keep it scannable
- No filler, no padding
