---
name: strategic-read
description: >
  Produce a state-of-the-OS report from the current file layer. Say "give me a strategic read", "where am I", "what's the state of my OS", "read across my brain and tell me where I stand" (or run `/founder-os:strategic-read`). Reads identity, priorities, decisions, clients, leads, cadence, flags, and the recent log, then returns a 5-section report: Identity anchor, Active commitments and pipeline, Open decisions, Active flags, Next 3 recommended moves. Pass a section key (`/founder-os:strategic-read flags`) to produce only that section when you do not need the full report. Read-only. Free-tier accessible: file read plus in-session synthesis, no external API call, no paid model required.
why: "Produces a one-shot orientation across your operating files instead of asking you to remember which file holds which piece of state."
enhance: "Keep cadence/daily-anchors.md and cadence/weekly-commitments.md current. If those headers are stale, the report flags it and recommends a refresh before any synthesis lands."
allowed-tools: ["Read", "Glob", "Grep"]
mcp_requirements: []
---

# Strategic Read

Runs on: reasoning - reads your files and reasons; any capable agent can run this.

A user runs `/founder-os:strategic-read` (no arguments) for the full 5-section report, or `/founder-os:strategic-read <section>` for a single named section. The report is the output. Nothing is written. No file is modified.

## Section argument (optional)

When the user passes a single argument, treat it as a section selector. Valid section keys (lowercase, kebab-case) map to the section headers below:

| arg | section header |
|---|---|
| `identity` | `## 1. Identity anchor` |
| `commitments` | `## 2. Active commitments and pipeline` |
| `decisions` | `## 3. Open decisions` |
| `flags` | `## 4. Active flags` |
| `next-moves` | `## 5. Next 3 recommended moves` |

When a valid section is named, run the read list and the stale-context check as usual, then render ONLY that section inside the fenced block. Drop the other four sections. The fenced block opens with the same `STRATEGIC READ - <YYYY-MM-DD>` line as the full report so downstream skills can grep deterministically.

When the section argument does NOT match any valid key, do NOT fall back to the full report. Print a one-line note listing the valid keys and stop:

```
Unknown section: <arg>. Valid keys: identity, commitments, decisions, flags, next-moves.
```

The mapping table is the contract. If the section headers in this skill body ever change wording, update the table here so the args stay coupled to the actual headers.

## When to use

- Returning to the OS after a gap and needing one orientation pass.
- Before a planning session, to anchor on current state instead of last remembered state.
- When a question touches priorities, pipeline, decisions, and flags at once.

## When NOT to use

- A single-channel question. Use `/founder-os:today` for the day, `/founder-os:brain-pass "<question>"` for synthesis on a specific topic.
- A keyword match. Use `/founder-os:query "<keyword>"`.

## Pre-flight

1. If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
2. Read each file listed below in order. Missing files are not fatal; name the gap in the report.

## Files read (in this order)

The skill reads, in order:

1. `core/identity.md`
2. `context/priorities.md`
3. `context/decisions.md`
4. `context/clients.md`
5. `context/leads.md` (optional - some installs route lead pipeline through `context/clients.md` Prospect rows; if `context/leads.md` is absent, do not flag as missing, just use `context/clients.md` as the pipeline source)
6. `cadence/daily-anchors.md`
7. `cadence/weekly-commitments.md`
8. `brain/flags.md`
9. `brain/log.md` (last 20 entries only, newest on top)

If `brain/.snapshot.md` exists, also read it. Use it as supplementary runtime state. Proceed without it if missing.

## Stale-context check (run before synthesis)

Before producing the report:

1. Read the `## Today: YYYY-MM-DD` header in `cadence/daily-anchors.md`. If the date is past today, mark daily stale.
2. Read the `## Week of YYYY-MM-DD` header in `cadence/weekly-commitments.md`. If the date is more than 6 days past today, mark weekly stale.
3. If either is stale, prepend a single line to the report: `STALE: <which file or files>. Refresh cadence/<file>.md, then re-run /founder-os:strategic-read for a clean read.` Then continue producing the report against current file contents. The stale flag is a recommendation, not a block.

## Output (exact 5-section structure)

Render the report inside a single fenced block. Section headers stay verbatim so downstream skills can grep for them.

```
STRATEGIC READ - <YYYY-MM-DD>

## 1. Identity anchor
<One line synthesised from core/identity.md. Who the operator is right now, sells to whom, sells what. If identity fields are still template placeholders, say so and recommend /founder-os:setup.>

## 2. Active commitments and pipeline
- This month: <top 3 priorities from context/priorities.md Current Priorities section>
- This week: <Must Do items from cadence/weekly-commitments.md, plus Should Do if Must Do is empty>
- Active clients: <one line per Engaged row from context/clients.md>
- Hot or warm leads: <one line per Hot or Warm row from context/leads.md Stage column if the file exists; otherwise one line per Scoped / Meeting Scheduled / Proposal Sent row from context/clients.md>

## 3. Open decisions
- Pending: <one line per Pending decision from context/decisions.md with Since date>
- Parked: <one line per Parked decision from context/decisions.md with trigger to revisit>

## 4. Active flags
<One line per OPEN or ESCALATED flag from brain/flags.md. Include severity (Week 1 / Week 2 / Week 3+) and decay status. A flag past its `Decay after:` date is marked `(decayed - keep/kill/refresh)` per rules/entry-conventions.md.>

## 5. Next 3 recommended moves
<Three concrete moves, one line each. Synthesised across priorities + flags + cadence + decisions. Each move points at one of: closing a Week 3+ flag, advancing a Hot lead, resolving a Pending decision, shipping a Must Do, or refreshing a stale cadence file. Do not invent moves; cite the source channel in parentheses at the end of each line.>
```

## Synthesis rules

- The report is your reasoning across the matches, not a paste of the matches. Summarise. Cite stable entry IDs (`log-YYYY-MM-DD-NNN`, `flag-YYYY-MM-DD-NNN`, etc.) when they exist so the operator can open the source.
- Read-only. Never edit any file as a side effect.
- Free-tier accessible. No external API call, no paid model. The model running this skill IS the synthesis engine.

## Missing file handling (graceful degradation)

For each file in the read list that is absent:

- Do not invent content for that section.
- Render the section header anyway and name the gap on a single line: `(missing: <path>)`.
- If `core/identity.md` is the missing file, stop at the pre-flight step (per Pre-flight rule 1). All other missing files produce a degraded but valid report.

Example degraded section:

```
## 4. Active flags
(missing: brain/flags.md - run /founder-os:setup to scaffold the brain layer)
```

## Edge cases

- **Fresh install with only template files.** Identity exists but priorities, decisions, flags are template stubs with `{{PLACEHOLDER}}` markers. Report each section as `(template stub - no real entries yet)`. Do not strip the placeholders into prose; that fabricates content.
- **Empty pipeline.** No Engaged clients and no Hot or Warm leads. Section 2 still renders; the relevant sub-lines read `(none)`.
- **Empty flags.** Section 4 reads `(no open flags)`. Section 5 then leans on priorities and decisions only.
- **`brain/log.md` has fewer than 20 entries.** Read what is there. Do not pad.

## Composition with other skills

When another skill calls strategic-read for orientation, it consumes the structured 5-section block as input. The calling skill cites section numbers (e.g. "per Section 3 of the strategic read") rather than re-synthesising.

## Voice rules

- No em dashes, no en dashes. Hyphens only.
- No banned words per `templates/rules/writing-style.md`: delve, robust, seamless, leverage (verb), comprehensive, holistic, transformative, streamline, optimize, utilize, facilitate, unlock, navigate (metaphorically), ecosystem, landscape, cutting-edge, best-in-class, world-class, game-changer, innovative.
- Contractions on. Plain language. Mirror the operator's words back where possible.

## Privacy

Summarise. Do not paste raw entry bodies that contain personal or client-sensitive content. Cite the ID and the file path. The operator opens the source if they want detail.

## Brain context (default)

Before producing output, read `brain/.snapshot.md` if it exists. The open-flags and weekly-must-do blocks make the synthesis sharper. If the snapshot script is missing (older install), proceed without it.

## Rules

- Read-only on the entire repo. Never edit a file as a side effect of a strategic read.
- The 5 section headers are a contract. Other skills may grep for them. Keep them verbatim: `## 1. Identity anchor`, `## 2. Active commitments and pipeline`, `## 3. Open decisions`, `## 4. Active flags`, `## 5. Next 3 recommended moves`.
- The stale-context line, when it fires, prepends the fenced block. It does not replace it.

<!-- private-tag: not applicable: strategic-read is read-only. It produces an in-session report from existing files and writes nothing back to disk, so the private-tag exclusion contract has no write surface to govern here. -->
