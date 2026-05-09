---
name: menu
description: >
  Show what FounderOS can do right now. Say "show me what you can do", "what can FounderOS do", "what should I try next", or "what's relevant right now" (or run /founder-os:menu). Returns 5 to 7 capability suggestions tailored to current state. Reads `brain/.snapshot.md`, open flags, this week's must-do, the last 7 days of `brain/log.md`, and the presence of `core/voice-profile.yml` and `core/brand-profile.yml`. Free-tier accessible - no LLM call inside the algorithm.
allowed-tools: ["Read", "Glob", "Grep"]
mcp_requirements: []
---

# Menu

Discovery entry for FounderOS. Returns a small, ranked list of capabilities the founder is most likely to want right now, scored against current state. Natural-language phrasing is primary, slash commands appear parenthetically.

This skill must:

- Run end-to-end without writing to any file.
- Read state files only. No LLM call. No web call.
- Return at least 5 rows on every install, including a brand-new one.
- Finish in under 2 seconds on a populated install.

## Algorithm

The model running this skill IS the menu engine. Read the state, score capabilities, return top 5 to 7. No external service.

### Step 1 - Read current state

Read these files if they exist. Skip silently if missing.

- `brain/.snapshot.md` - the runtime context payload (do NOT regenerate it; just read it).
- `brain/flags.md` - count entries with `Status: OPEN`.
- `cadence/weekly-commitments.md` - extract the `## Week of` date and the `Must Do` items.
- `brain/log.md` - read last 7 days of entries (group by `## YYYY-MM-DD` headers).
- `core/voice-profile.yml` - check existence and whether body is template defaults (`{{HANDLEBARS}}` markers present).
- `core/brand-profile.yml` - same check.
- `context/priorities.md` - look for items rolled forward (lines tagged `Week 2+`, `Week 3+`, or similar).
- `drafts/` directory - count files modified in the last 24 hours (if directory exists).

Do not synthesize. Just collect facts.

### Step 2 - Score capabilities

Each capability has a `surface_when` rule. Score 1 if the rule fires, 0 otherwise.

- `voice-interview` - surface when `core/voice-profile.yml` is missing OR contains template defaults.
- `brand-interview` - surface when `core/brand-profile.yml` is missing OR contains template defaults.
- `priority-triage` - surface when `context/priorities.md` has 3 or more items rolled forward (lines containing `Week 2+`, `Week 3+`, or `Week 4+`), OR when `brain/log.md` last 7 days mentions overwhelm, stuck, too many.
- `weekly-review` - surface when current date is more than 6 days past the `## Week of` date in `cadence/weekly-commitments.md`, OR when no weekly commitments file exists.
- `forcing-questions` - surface when log mentions a new initiative, scope expansion, or "should I start" in the last 7 days.
- `pre-send-check` - surface when `drafts/` has files modified in the last 24 hours.
- `capture-meeting` - surface when next 24h calendar event is less than 1 hour away (only if calendar MCP is connected; otherwise skip silently).
- `audit` - surface when last `audit` invocation in `brain/log.md` is more than 14 days old, OR never run.

Capability rows that did not fire still get scored 0 and remain available as fallback when fewer than 5 rows fired.

### Step 3 - Pick top 5 to 7

Sort by score (1 first, 0 second). Tie-break by surface order in Step 2. Take the first 5 to 7.

### Step 4 - Render rows

Each row has three parts:

- Natural-language phrasing first.
- Slash command in parentheses second.
- One-sentence why-now after a hyphen.

Pattern:

```
- Say "set up my voice profile" (or run <prefix>voice-interview) - your voice profile is empty and writing skills will fall back to anti-AI defaults until it's filled.
```

Use the same `<prefix>` substitution model the wizard uses (see `skills/founder-os-setup/SKILL.md` Phase 6.2). On Path A, `<prefix>` is `/founder-os:`. On Path B, `<prefix>` is `/`. Always-bare commands (`/today`, `/next`, `/pre-meeting`, `/capture-meeting`) stay bare on both paths.

### Step 5 - Close

End the output with this line, verbatim:

> These are tailored to your current state. Say any of the natural-language phrases above. Or ask Claude anything in plain English - most of FounderOS routes by what you say, not what you type.

## Zero-state safety

On a brand-new install with no `brain/.snapshot.md`, no `brain/log.md` entries, and no `context/priorities.md`, return the Day-1 starter set in this exact order. Never return an empty list. Never return "no capabilities to suggest."

Day-1 starter set:

1. `voice-interview` - "Say 'set up my voice profile' (or run <prefix>voice-interview) - day one move. Without it, writing skills fall back to anti-AI defaults."
2. `brand-interview` - "Say 'set up my brand profile' (or run <prefix>brand-interview) - day one move. Without it, branded deliverables render plain."
3. `priority-triage` - "Say 'what should I focus on next' (or run <prefix>priority-triage) - cuts a long open list down to one thing."
4. `today` - "Say 'what's on for today?' (or run /today) - one-screen view of today's anchor, open flags, and next event."
5. `ingest` - "Say 'ingest this' on any URL or file (or run <prefix>ingest) - files a source into raw/ with provenance preserved."

## Sample output

Rendered output for a partially populated install with voice profile missing, weekly commitments stale, and 4 items rolled forward:

```
Here are 5 things FounderOS can do right now, picked for your current state:

- Say "set up my voice profile" (or run /founder-os:voice-interview) - your voice profile is empty so writing skills are falling back to anti-AI defaults.
- Say "run my weekly review" (or run /founder-os:weekly-review) - your weekly commitments file is 9 days old, the sprint needs rolling.
- Say "what should I focus on next" (or run /founder-os:priority-triage) - 4 priorities rolled forward, list needs cutting.
- Say "audit the OS" (or run /founder-os:audit) - last audit was 18 days ago, worth a fresh pass.
- Say "what's on for today?" (or run /today) - one-screen view of today's anchor and next event.

These are tailored to your current state. Say any of the natural-language phrases above. Or ask Claude anything in plain English - most of FounderOS routes by what you say, not what you type.
```

## Constraints

- No LLM call inside the algorithm. The menu reads files, scores against rules, returns the top N.
- No write operations. This skill never modifies any file.
- Free-tier accessibility floor preserved. Works without a paid AI subscription.
- Anti-AI rules apply to any prose generated. No banned phrases, no em dashes, no en dashes.
- Trigger phrases listed in `skills/founder-os-setup/SKILL.md` Phase 6.2 must appear verbatim where relevant ("set up my voice profile", "set up my brand profile", "what should I focus on next", "what's on for today?", "audit the OS").
