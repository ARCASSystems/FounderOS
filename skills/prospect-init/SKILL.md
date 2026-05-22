---
name: prospect-init
description: >
  Create a new prospect record for a company you sell to or watch. Trigger on "add a prospect", "track <company> as a prospect", "start tracking <company>", "new prospect <company>", or run `/founder-os:prospect-init <slug>`. Creates `companies/prospects/<slug>.md` from `templates/prospect-context.template.md` after asking 3 to 5 questions. Different from `business-context-loader`, which is for companies you run.
why: "Captures the minimum prospect intel in one short flow so the next time you write a proposal or run strategic analysis, the context exists at a predictable path instead of scattered across your notes."
enhance: "Fill the operator business-context for your own company first - ICP and anti-ICP fields in your business-context-loader output make this flow sharper because it can flag the prospect against your fit signals."
allowed-tools: ["Read", "Write", "Edit", "Glob", "Bash"]
mcp_requirements: []
---

# Prospect Init

Captures a lightweight prospect record at `companies/prospects/<slug>.md`. Companion to `business-context-loader` (which handles companies you run, not prospects).

This skill must:
- Run on a fresh install (creates `companies/prospects/` lazily on first use).
- Never overwrite an existing prospect file silently.
- Ask 3 to 5 questions, no more. Rambly answers are fine; extract intent.
- Write the file in one pass after the user confirms the captured fields.
- Append a single line to `brain/log.md` capturing what was added.

## Pre-flight

1. If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
2. If `templates/prospect-context.template.md` does not exist, stop with: `Prospect template missing. Re-install or run /founder-os:update.`
3. If `companies/prospects/` does not exist, create it (empty directory is fine until the first file lands).

## Step 1 - Resolve the slug

Detect what the user passed:

- **Argument present** (e.g. `/founder-os:prospect-init widgetco` or "track widgetco as a prospect"): use `<slug>` directly. Sanitise: lowercase, replace spaces with hyphens, strip punctuation.
- **No argument**: ask `What is the company called?` and derive the slug from the answer.

Check `companies/prospects/<slug>.md` does not already exist. If it does, surface:

> `<slug>` already has a prospect file. Open it, or pick a different slug?

## Step 2 - Ask the minimum questions

Ask 3 to 5 questions, one at a time. Wait for each answer. Use the user's words back to them.

1. **What do they do, in one sentence?** (drives company name + sector + a usable note)
2. **Why are you tracking them?** (one paragraph, the trigger that made them worth a file)
3. **What's the current relationship?** (cold / warm / engaged - the user can answer in their own language; map it on the back end)
4. **Do they match your ICP?** (yes / partially / no - and if you have an operator business-context with an Anti-ICP list, flag a hit explicitly)
5. **Where did this come from?** (the source of intel - a meeting, a deck, a referral, public sources)

If the user volunteers more (headcount, geography, website), capture it. If they don't, leave the field blank in the template - prospect files do not require every field to be useful.

## Step 3 - Confirm

Show a 5-line summary of what you captured:

```
PROSPECT: <Company name>
SECTOR: <sector or "unknown">
STAGE: <cold | warm | engaged>
WHY TRACKING: <one line>
FIT: <yes | partially | no, with anti-ICP flag if it fires>
```

Ask: `Write this to companies/prospects/<slug>.md?`

If the user says no, stop. Do not write a partial file.

## Step 4 - Write the file

Copy `templates/prospect-context.template.md` to `companies/prospects/<slug>.md`.

Fill the fields you captured. Leave the rest blank (no `[FILL]` markers). Set **Last touched** to today's date.

Add a first **Notes** entry: `YYYY-MM-DD - prospect file created via prospect-init.`

## Step 5 - Brain log

Append a single line to `brain/log.md`:

```
## YYYY-MM-DD prospect-init | <slug> | <one-line summary of why tracking>
```

Tag the entry with `#prospect-init` so it surfaces in later audits.

## Step 6 - Output

Five-line confirmation:

```
PROSPECT FILED: <Company name>
PATH: companies/prospects/<slug>.md
STAGE: <cold | warm | engaged>
NEXT: Update the file as you learn more, or run strategic-analysis to map them against your market.
LOG: brain/log.md updated.
```

## Edge cases

- **User asks to track a company that is actually their own.** Ask: `Sounds like this is a company you run, not a prospect. Want to use business-context-loader instead?`
- **User provides a slug that matches an operator file** (`companies/<slug>-business.md` exists). Ask: `There is already an operator company at companies/<slug>-business.md. Is this the same company, or a different one with the same name?` Do not silently create the prospect file.
- **User wants to upgrade a prospect to operator.** Out of scope for this skill. Tell them: `When a prospect becomes a company you run, copy the relevant content from companies/prospects/<slug>.md into a new companies/<slug>-business.md via business-context-loader.`
- **Template missing fields the user wants to fill.** The prospect template is intentionally lightweight. If a user needs more structure, point them at the operator template; do not extend this template on the fly.

## What this skill does NOT do

- Does not enrich the prospect from external sources. Capture is manual.
- Does not chase the prospect. It records, the user acts.
- Does not produce a proposal, outreach draft, or analysis. Use `proposal-writer`, `email-drafter`, or `strategic-analysis` for those - they will read this file when they need company-specific context.

## Voice rules

Plain language. The user is not a strategist. Mirror their words back. Do not translate "we're chasing this big retailer" into "ICP firmographic axis is retail enterprise."

## Brain context (default)

Before producing output, read `brain/.snapshot.md` if it exists. The open-flags block can surface whether this prospect collides with a parked decision or open commitment. If the snapshot script is missing (older install), proceed without it.

<!-- private-tag: not applicable: prospect-init writes prospect facts captured from user speech into a structured file; the file lives in the public companies/prospects/ surface, not private brain state -->
