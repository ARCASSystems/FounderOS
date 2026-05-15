---
name: readiness-check
description: >
  Score the OS install across five buckets and name the next 3 moves. Trigger on "check my OS readiness", "how am I doing", "what's my OS state", "readiness check", "how's the system", or "where are the gaps" (or run /founder-os:status). For a full composite health report across all five checks, use /founder-os:audit instead. Returns a 0-100% score across Core, Voice and Brand, Cadence, Business Context, and Brain Layer. Read-only.
allowed-tools: ["Read", "Glob", "Grep"]
mcp_requirements: []
---

> **Command:** `/founder-os:status` (plugin install) or `/status` (git clone install). This folder is named `readiness-check` to describe what it does; the command is `status` because it's the natural founder-facing name.

# Readiness Check

Read-only audit of the Founder OS install. Returns a weighted score and the next 3 moves.

This skill must:
- Run end-to-end on a fresh install (mostly empty result, no crashes).
- Run on a partial install (mid-completion) and produce a useful score.
- Run on a fully populated install and show 80%+ readiness.
- Render in under 3 seconds.
- Never write to any file.

## How to score

Six buckets, each scored 0-100. Overall is the weighted average.

| Bucket | Weight | What it reads |
|---|---|---|
| Core | 25% | `core/identity.md`, `context/priorities.md` |
| Voice and Brand | 25% | `core/voice-profile.yml`, `core/brand-profile.yml` |
| Cadence | 20% | `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, `cadence/quarterly-sprints.md` |
| Business Context | 15% | `context/companies.md`, `context/companies/<name>.md` for each declared business |
| Brain Layer | 10% | `brain/log.md`, `brain/flags.md`, `brain/patterns.md` |
| Queue | 5% | `cadence/queue.md` |

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

### Brain Layer (10%)

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

### Queue (5%)

Read `cadence/queue.md`:

- File missing -> 0 (`not set up`)
- ACTIVE > 0 AND DONE entries present in last 7 days -> 100 (`active`)
- ACTIVE > 0 but no DONE in last 7 days -> 50 (`in progress`)
- ACTIVE = 0 but BACKLOG has items -> 50 (`backlog only`)
- All sections empty or file missing -> 0 (`empty`)

DONE entries are lines in the `## DONE` section with a date within the last 7 days.

## Backlog (from setup wizard)

If `founder-os-setup` left deferred items, they live in `core/setup-backlog.md` under the `## Setup Backlog` heading. Read that file and surface up to 3 items in the BACKLOG section of the output. If the file is missing or empty, write `none recorded` and skip.

## Next 3 Moves logic

The next 3 moves are the highest-impact gaps. Pick in this order:

1. If voice-profile is missing or template defaults: `Run /founder-os:voice-interview - activates <N> deliverable skills`.
2. If brand-profile is missing or template defaults: `Run /founder-os:brand-interview - activates branded deliverables`.
3. If identity.md is missing: `Run /founder-os:setup - the OS has no idea who you are yet`.
4. If priorities.md is missing or stale: `Update context/priorities.md - this week's focus is unclear`.
5. If daily-anchors is stale by 4+ days: `Roll cadence/daily-anchors.md and run a weekly-review` (chain).
6. If weekly-commitments is stale by 7+ days: `Say "run my weekly review" - weekly-review is a skill, not a slash command`.
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

QUEUE (<NN>%)
- active: <count>/3
- done last 7 days: <count>

BACKLOG (from setup wizard)
- <item 1>
- <item 2>
- <item 3>
| none recorded

NEXT 3 MOVES
- <highest-impact gap>
- <second>
- <third>
```

Replace `<NN>` with actual percentages. Replace `<count>` with actual integers. Replace `<...>` placeholders with the file's real status label.

If a section has no content (e.g. no businesses declared), keep the section header and write one line: `none declared.` Don't omit sections.

## Rules

- Read-only. Do NOT write to any file.
- Do NOT invoke other skills.
- If total score is under 20, replace the NEXT 3 MOVES section content with the Day-1 starter sequence below, and replace the top line of the fenced block with `STATUS: Day 1 - your OS is fresh. Score will climb as you complete setup.` Keep every other section header in place (mark each `none recorded` or its actual value).

  Day-1 NEXT 3 MOVES content:
  - Run /founder-os:identity-interview to capture who you are
  - Run /founder-os:voice-interview to capture how you write
  - Set 1-3 priorities in `context/priorities.md`

- Output ONLY the fenced block. No prose around it.
- If `core/identity.md` is missing, reply with exactly this block and stop:

  ```
  Founder OS not set up here. Day 1 - start with these three steps:
  1. Run /founder-os:setup to walk the interactive wizard
  2. Then /founder-os:identity-interview to capture who you are
  3. Then /founder-os:voice-interview to capture how you write

  Run /founder-os:status after each step to see your score build.
  ```
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

<!-- private-tag: not applicable: readiness-check is read-only; context/ reference describes files being read, not written -->
