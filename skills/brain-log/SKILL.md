---
name: brain-log
description: >
  Manages the brain system - logging thoughts, flagging patterns, parking decisions. Use this skill when the user says "log this", "capture this", "flag this", "park this decision", "note this", "remember this", "save this thought", "brain dump", "I had an idea", "something to track", or any variation of capturing a thought, observation, or decision for later. Also trigger when the user shares an observation that should be recorded but doesn't need immediate action.
---

# Brain Log - Thinking in Motion

You manage the founder's brain system. Three modes for incoming thoughts, plus flags and parked decisions.

## Routing

When the founder gives you something to capture, determine which mode:

### Mode A: Log and Move On
The thought is worth recording but doesn't connect to anything specific right now.
- Append to `brain/log.md` with timestamp
- Tag: `#context`
- No follow-up

### Mode B: Log and Cross-Reference
The thought connects to an existing file or topic.
- Append to `brain/log.md` with timestamp
- Tag: `#xref:[target-file]`
- Insert a dated note into the referenced file
- Examples: "This changes my priorities" -> xref to priorities.md. "This affects the deal with X" -> xref to clients.md

### Mode C: Log and Act
The thought requires immediate action.
- Append to `brain/log.md` with timestamp
- Tag: `#acted`
- Take the action (update a file, create a task, move a priority)
- Note what was done in the log entry

**Default:** Infer the mode from context. The founder can override: "just log it" (Mode A), "tie this to priorities" (Mode B), "act on this now" (Mode C).

## Flags

When the founder says "flag this" or you detect friction/stalls:

Write to `brain/flags.md` with:
```
### [date] - [STALL/FRICTION/PERFORMANCE] - [short title]
- What: [what's happening]
- Why it matters: [impact if unaddressed]
- Pattern: [if this connects to a recurring issue]
- Action: [what should change]
- Cross-ref: [related files]
```

Two types of flags:
1. **Role performance flags** - feedback on how a specific operating mode is performing
2. **Friction/stall flags** - items stuck, avoided, or compounding

## Parked Decisions

When the founder says "park this" or you identify a decision that's not ready to be made:

Write to `brain/decisions-parked.md` with:
```
### [Decision Title]
- Status: Parked
- Date parked: [date]
- Context: [why this came up and why it's not ready]
- Trigger to revisit: [specific condition that means it's time to decide]
- Options: [if known]
- Cross-reference: [related files]
```

Every parked decision MUST have a trigger condition. "Revisit later" is not a trigger. "After first paying client" or "after running the system for 2 weeks" are triggers.

## Brain Dump Mode

When the founder says "brain dump" or starts sharing a stream of thoughts:

1. Listen to the full dump without interrupting
2. Categorize each thought: log (A), cross-reference (B), act (C), flag, or park
3. Present the categorization: "Here's how I'd route these - [list]. Any changes?"
4. Process all items after confirmation

## Archive Protocol

Before appending to `brain/log.md`, check its line count. If it's approaching 300 lines:

1. Summarize the oldest entries into key takeaways
2. Extract emerging patterns to `brain/patterns.md`
3. Move raw text to `brain/archive/YYYY-MM.md`
4. Clear the archived entries from log.md

This is mandatory. Don't skip it.

## Log Entry Format

```
### YYYY-MM-DD HH:MM - #tag
[Content of the thought/observation/update]
```

Newest entries on top. Keep entries concise - capture the insight, not the full conversation.

## Rules

- Capture the insight, not the conversation. "Realized pricing needs to account for delivery time" not "We were talking about pricing and I mentioned that..."
- One log entry per thought. Don't bundle unrelated items.
- Cross-references must point to real files. Check the file exists before referencing it.
- Parked decisions without trigger conditions are just avoidance. Push for a trigger.
- When you detect a pattern across multiple log entries, proactively suggest adding it to `brain/patterns.md`.
