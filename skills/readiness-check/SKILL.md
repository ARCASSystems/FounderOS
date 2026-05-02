---
name: readiness-check
description: >
  Reads the current state of the Founder OS install and returns a weighted readiness score (0-100%) across five buckets: Core, Voice and Brand, Cadence, Business Context, Brain Layer. Surfaces the next 3 high-leverage moves the founder can make. Read-only - never writes to user files. Triggered by the `/founder-os:status` slash command. Use this when the founder asks "how am I doing", "what's my OS state", "readiness check", "how's the system", "what should I focus on next", or "where are the gaps".
allowed-tools: ["Read", "Glob", "Grep"]
mcp_requirements: []
---

# Readiness Check

Read-only audit of the Founder OS install. Returns a weighted score and the next 3 moves.

This skill must:
- Run end-to-end on a fresh install (mostly empty result, no crashes).
- Run on a partial install (mid-completion) and produce a useful score.
- Run on a fully populated install and show 80%+ readiness.
- Render in under 3 seconds.
- Never write to any file.

## How to score

Five buckets, each scored 0-100. Overall is the weighted average.

| Bucket | Weight | What it reads |
|---|---|---|
| Core | 25% | `core/identity.md`, `context/priorities.md` |
| Voice and Brand | 25% | `core/voice-profile.yml`, `core/brand-profile.yml` |
| Cadence | 20% | `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, `cadence/quarterly-sprints.md` |
| Business Context | 15% | `context/companies.md`, `context/companies/<name>.md` for each declared business |
| Brain Layer | 15% | `brain/log.md`, `brain/flags.md`, `brain/patterns.md` |

### Core (25%)

Read `core/identity.md` and `context/priorities.md`. For each:
- File missing -> 0.
- File exists but contains template placeholders (`{{HANDLEBARS}}`, `[BRACKETED]`, `[CHOOSE:` markers) on more than 30% of lines -> 20 (template defaults, not run).
- File exists but has no real content past the headers (under 200 characters of body) -> 30 for that file.
- File exists, content present, no template placeholders -> 100 for that file.
- File exists, content present, but file modified more than 14 days ago (per filesystem mtime) -> mark as `stale` and score 60.

Bucket score = average of the two file scores.

Status labels for output:
- `populated` if score >= 90
- `partial` if score 30-89
- `empty` if score 0-29
- Append ` (stale)` if file is more than 14 days old

### Voice and Brand (25%)

Read `core/voice-profile.yml` and `core/brand-profile.yml`. For each:
- File missing -> 0.
- File exists but contains template placeholders (`[CHOOSE: ...]`, `[YOUR ...]`, `[#XXXXXX]`, `{{HANDLEBARS}}`) on any required field -> 20 (template defaults, not run).
- File exists, no placeholders on required fields, has real content -> 100.

Bucket score = average of the two file scores.

Also count the number of voice-coupled skills that can run with the current voice profile:
- If voice profile is populated: count `linkedin-post`, `client-update`, `proposal-writer`, `email-drafter`, `content-repurposer`, `sop-writer` as unlocked. Plus `your-voice` itself.
- If voice profile contains placeholders or is missing: 0 unlocked.

Status labels for output:
- `populated` if score 100
- `template defaults` if score 20
- `not run` if score 0
- For brand-profile only: `partial` if some fields are filled but not all

### Cadence (20%)

Three files. Each scored 0-100:

`cadence/daily-anchors.md`:
- Read the file. Look for `## Today: <YYYY-MM-DD>` header.
- If header date == today -> 100 (`current`)
- If header date is 1-3 days old -> 60 (`stale - <X> days`)
- If header date is 4+ days old -> 20 (`stale - <X> days`)
- File missing or no `## Today:` header -> 0 (`empty`)

`cadence/weekly-commitments.md`:
- Look for `## Week of <YYYY-MM-DD>` header.
- If within 6 days of today -> 100 (`current`)
- If 7-13 days old -> 50 (`stale`)
- If 14+ days old -> 10 (`stale`)
- File missing or no `## Week of` header -> 0 (`empty`)

`cadence/quarterly-sprints.md`:
- File missing or empty -> 0 (`empty`)
- File has any content past template placeholders -> 100 (`populated`)
- Template-defaults only -> 20

Bucket score = average of the three file scores.

### Business Context (15%)

Read `context/companies.md`. Count the number of declared businesses (top-level `## ` headers naming businesses, or rows in a table - whichever pattern the file uses).

For each declared business, check whether `context/companies/<sanitised-name>.md` exists and has content.

- Score per business: 0 if context file missing, 50 if file exists but contains `[FILL]` placeholders, 100 if file is populated.
- Bucket score = average across all declared businesses.
- If `context/companies.md` itself is missing or has no declared businesses, score 0 and label `no businesses declared`.

### Brain Layer (15%)

Three files:

`brain/log.md`:
- Count entries in the last 14 days. Look for date-stamped entry markers (e.g. `## YYYY-MM-DD` or `### YYYY-MM-DD HH:MM`).
- 0 entries -> 0
- 1-2 entries -> 40
- 3-9 entries -> 80
- 10+ entries -> 100

`brain/flags.md`:
- Count any entries (open or resolved).
- 0 -> 0
- 1+ -> 100

`brain/patterns.md`:
- Count any entries past the template placeholders.
- 0 -> 0
- 1+ -> 100

Bucket score = average of the three file scores.

## Backlog (from setup wizard)

If `founder-os-setup` left a `BACKLOG` block in any of the cadence or brain files (typically `cadence/quarterly-sprints.md` or a `core/setup-backlog.md`), surface up to 3 items in the BACKLOG section of the output. If no backlog exists, write `none recorded` and skip.

## Next 3 Moves logic

The next 3 moves are the highest-leverage gaps. Pick in this order:

1. If voice-profile is missing or template defaults: `Run /founder-os:voice-interview - unlocks <N> deliverable skills`.
2. If brand-profile is missing or template defaults: `Run /founder-os:brand-interview - unlocks branded deliverables`.
3. If identity.md is missing: `Run /founder-os:setup - the OS has no idea who you are yet`.
4. If priorities.md is missing or stale: `Update context/priorities.md - this week's focus is unclear`.
5. If daily-anchors is stale by 4+ days: `Roll cadence/daily-anchors.md and run a weekly-review` (chain).
6. If weekly-commitments is stale by 7+ days: `Run /founder-os:weekly-review`.
7. If brain/log.md has 0 entries in last 7 days: `Open brain-log skill and capture this week's signals`.
8. If a declared business has no `context/companies/<name>.md`: `Run business-context-loader for <name>`.
9. If quarterly-sprints is empty: `Set this quarter's focus in cadence/quarterly-sprints.md`.
10. If brain/flags.md is empty AND priorities have rolled 2+ weeks: `Open Chief of Staff lens, surface stalls`.

Pick the top 3 by impact (voice and identity first, then cadence, then brain). If fewer than 3 gaps, return what exists. Never invent moves.

## Output template

Render this as a single fenced block. No commentary outside the block.

```
FOUNDER OS READINESS - <NN>%
Last checked: <YYYY-MM-DD>

CORE (<NN>%)
- identity.md           <populated | partial | empty | stale>
- priorities.md         <populated | partial | empty | stale>

VOICE AND BRAND (<NN>%)
- voice-profile.yml     <populated | template defaults | not run>
- brand-profile.yml     <populated | template defaults | not run>
- voice-coupled skills unlocked: <N>

CADENCE (<NN>%)
- daily-anchors.md      <current | stale - X days | empty>
- weekly-commitments.md <current | stale | empty>
- quarterly-sprints.md  <populated | template defaults | empty>

BUSINESS CONTEXT (<NN>%)
- declared businesses: <N>
- context files filled: <M of N>

BRAIN LAYER (<NN>%)
- log.md entries last 14d: <count>
- open flags: <count>
- patterns logged: <count>

BACKLOG (from setup wizard)
- <item 1>
- <item 2>
- <item 3>
| none recorded

NEXT 3 MOVES
- <highest-leverage gap>
- <second>
- <third>
```

Replace `<NN>` with actual percentages. Replace `<count>` with actual integers. Replace `<...>` placeholders with the file's real status label.

If a section has no content (e.g. no businesses declared), keep the section header and write one line: `none declared.` Don't omit sections.

## Rules

- Read-only. Do NOT write to any file.
- Do NOT invoke other skills.
- Output ONLY the fenced block. No prose around it.
- If `core/identity.md` is missing, reply: `Founder OS not set up here. Run /founder-os:setup first.` and stop.
- Total output should fit on one screen at standard terminal width (under 50 lines).
- No em dashes or en dashes. Hyphens only.
- Render time target: under 3 seconds.

## Failure handling

If a file read fails (permissions, encoding, etc.), score that file as 0 and append a `READ ERRORS` section at the bottom of the output naming the file. Do not crash. Do not fabricate scores.

If `cadence/daily-anchors.md` exists but the date format is unrecognised, treat it as stale and score 30.

If `context/companies.md` exists but the format is unrecognisable as either headers or a table, count zero declared businesses and label `format unrecognised`.

## Self-check before delivering output

1. Total score is between 0 and 100.
2. Every section header is present even if its content is empty.
3. The NEXT 3 MOVES section has at most 3 items, all derived from real gaps.
4. No em dashes or en dashes in the output.
5. Output is a single fenced block. No prose before or after.
6. The output fits in under 50 lines.
