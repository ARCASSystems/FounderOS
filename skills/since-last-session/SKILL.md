---
name: since-last-session
description: >
  Report what changed in the OS since the last time this skill ran. Say "what changed since last session", "what did I miss", "catch me up since I was last here", "since last session", "what is new since yesterday" (or run `/since-last-session`). Reads a marker file at `brain/.last-session`, computes elapsed time, and reports five things: hours elapsed, brain/log.md entries added, flags decayed per the `Decay after:` convention, commitments now overdue from the cadence files, and files modified in `context/` (git diff names only). Updates the marker at the end of the run. First run with no marker prints a one-line note and seeds the marker; no delta report on the first run. Free-tier accessible: filesystem read plus a single git call, no external API.
why: "Without a session-to-session anchor, the operator boots blind to what shifted while they were away. The skill turns that gap into a five-line report by reading the file layer at task time, not by running a daemon."
enhance: "Run this skill at the start of every working session, before any planning work. The marker advances each time it runs, so the next session's report is scoped to the gap since the last run rather than since install."
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
mcp_requirements: []
---

# Since Last Session

A user runs `/founder-os:since-last-session` (no arguments). The skill reports what changed since the last marker time, then updates the marker. Read the file layer, do the math, render the report, write the marker. Nothing else.

## When to use

- Returning to the OS after a gap (hours, a day, a long weekend) and needing one delta pass.
- Before any planning work, so the report scopes to the gap since the last run.
- After a parallel session ran on another machine and you want to see what is newly on disk.

## When NOT to use

- Full state-of-the-OS orientation. Use `/founder-os:strategic-read` for the 5-section read across the brain.
- A single-topic question. Use `/founder-os:brain-pass "<question>"` or `/founder-os:query "<keyword>"`.
- A first-time install. The skill will run, but the first run prints the seed message and stops; there is no prior state to diff against.

## Marker file

- Path: `brain/.last-session`
- Format: a single line, ISO-8601 timestamp with timezone offset.
- Example: `2026-05-23T03:30:00+04:00`
- Writer: this skill itself, at the end of every successful run. A future SessionStart hook may also write the marker; the skill does not depend on it.

## Pre-flight

1. If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
2. Ensure `brain/` exists. If not, stop with: `brain/ folder missing. Re-install or run /founder-os:setup first.`

## First-run behaviour (marker missing)

If `brain/.last-session` does not exist:

1. Print verbatim: `No prior session found, creating marker now.`
2. Write the current local ISO-8601 timestamp (with timezone offset) to `brain/.last-session`. One line, no trailing newline beyond the line itself.
3. Stop. Do not produce a delta report. There is no prior state to diff against.

The marker write on first run is auto-runnable. It does not touch any operating file.

## Subsequent runs (marker present)

If `brain/.last-session` exists:

1. Read the marker timestamp. If the line does not parse as ISO-8601, stop with: `brain/.last-session is malformed. Expected one ISO-8601 line. Delete it to reseed, then re-run /founder-os:since-last-session.`
2. Compute elapsed time between the marker and the current time. Round hours to one decimal place.
3. Walk the five report sections below.
4. Render the report.
5. Overwrite `brain/.last-session` with the current ISO-8601 timestamp. This is the new anchor for the next run.

## Files read

The skill reads, in order:

1. `brain/.last-session` (the marker)
2. `brain/log.md` (to count entries added since the marker)
3. `brain/flags.md` (to find flags whose `Decay after:` window has passed since the marker)
4. `cadence/daily-anchors.md` (to find commitments past their date)
5. `cadence/weekly-commitments.md` (to find sprint items past their week)

If `brain/.snapshot.md` exists, also read it. Use it as supplementary runtime state. Proceed without it if missing.

For Section 5 the skill calls `git diff --name-only <marker-iso> -- context/` to list files in `context/` modified since the marker. The call goes through the `Bash` tool. If the install is not under git (no `.git/` directory at the repo root, or `git` returns a non-zero exit), skip Section 5 with the documented one-line note.

## Report shape (exact 5-section structure)

Render the report inside a single fenced block. Section headers stay verbatim so downstream skills can grep for them.

```
SINCE LAST SESSION - <YYYY-MM-DD HH:MM> -> <YYYY-MM-DD HH:MM>

## 1. Hours elapsed
<one line: "X.Y hours since last session" where X.Y is the rounded elapsed hours>

## 2. brain/log.md entries added
<count of new entries dated on or after the marker, one line per new entry with its ID and one-line summary; "(none)" if zero>

## 3. Flags decayed
<one line per flag in brain/flags.md whose Decay after: window has passed AND whose decay date sits between the marker and now; "(none)" if zero. Format per rules/entry-conventions.md: ID, heading, decay date>

## 4. Commitments now overdue
<one line per Must Do / Should Do row in cadence/weekly-commitments.md whose deadline sits between the marker and now and which is still marked pending; one line per Day-anchored row in cadence/daily-anchors.md whose Day is past today and which is still pending; "(none)" if zero>

## 5. Files modified in context/
<git diff --name-only output, one path per line; "(install is not under git; skipping context/ diff)" if the install is not under git; "(none)" if git ran cleanly and reported no changes>
```

After the fenced block, on its own line outside the fence, print: `Marker advanced to <new-iso-timestamp>.`

## Synthesis rules

- The report is your reasoning across the matches, not a paste of the matches. Cite stable IDs (`log-YYYY-MM-DD-NNN`, `flag-YYYY-MM-DD-NNN`) where they exist so the operator can open the source.
- Names only. Do not paste log entry bodies or flag bodies into the report. The operator opens the file for detail.
- The decay check uses the convention in `templates/rules/entry-conventions.md`: a flag with `Decay after: 14d` decays 14 days after its heading date; a flag with `Decay after: YYYY-MM-DD` decays on that absolute date. A flag without a `Decay after:` line never decays and never appears in Section 3.

## Missing file handling (graceful degradation)

For each file in the read list that is absent:

- Do not invent content for that section.
- Render the section header anyway and name the gap on a single line: `(missing: <path>)`.
- The skill does not stop on missing brain/log.md, brain/flags.md, or the cadence files. It stops only when `core/identity.md` or the `brain/` folder is missing (per Pre-flight).

Example degraded section:

```
## 3. Flags decayed
(missing: brain/flags.md - run /founder-os:setup to scaffold the brain layer)
```

## Edge cases

- **Marker timestamp in the future.** Print `brain/.last-session is ahead of the system clock. Skipping delta. Check your clock or delete the marker to reseed.` and stop. Do not overwrite the marker.
- **Marker line has trailing whitespace or extra blank lines.** Strip whitespace before parsing. Re-write a clean single-line marker on save.
- **brain/log.md has no entries newer than the marker.** Section 2 reads `(none)`. The skill still runs and still advances the marker.
- **Flag with relative decay but no anchor date.** Skip that flag from Section 3. The `rules/entry-conventions.md` scanner surfaces it via a separate `Decay anchor missing` block; this skill does not duplicate that.
- **Multiple separate conversations or threads in brain/log.md.** Count each as one entry. Do not group.
- **Install not under git.** Section 5 reads `(install is not under git; skipping context/ diff)`. The other four sections still render.
- **git command times out or errors for reasons other than no-git.** Section 5 reads `(git diff failed; skipping context/ diff)`. The skill does not stop.

## Approval gates

- Write to `brain/.last-session` -> **AUTO-RUN**. The marker is internal state owned by this skill. Per `rules/approval-gates.md` (or its template fallback), append-style writes to brain-layer files are auto-runnable.
- No other file is modified by this skill. No write to `brain/log.md`, no write to any `context/` file, no write to cadence files.

If `rules/approval-gates.md` is not present, default to the auto-run path for the marker only.

## Composition with other skills

- `/founder-os:strategic-read` is the full state-of-the-OS read. This skill is the delta version. Run since-last-session first for the gap, then strategic-read if a fuller orientation is still needed.
- `/founder-os:weekly-review` consumes the marker indirectly: a long elapsed time since last session is a signal the retro should ask whether the missing days had off-system commitments worth logging.
- `/founder-os:log-reply` writes to `brain/log.md`. Those writes show up as Section 2 entries on the next since-last-session run.

## Voice rules

- No em dashes, no en dashes. Hyphens only.
- No banned words per `templates/rules/writing-style.md`: delve, robust, seamless, leverage (verb), comprehensive, holistic, transformative, streamline, optimize, utilize, facilitate, unlock, navigate (metaphorically), ecosystem, landscape, cutting-edge, best-in-class, world-class, game-changer, innovative.
- Contractions on. Plain language. The report is read quickly at session start; keep each line scannable.

## Brain context (default)

Before producing output, read `brain/.snapshot.md` if it exists. The open-flags and weekly-must-do blocks make Section 3 and Section 4 sharper. If the snapshot script is missing (older install), proceed without it. Do not block.

## Rules

- Read-only on every file except `brain/.last-session`. The marker is the one file this skill writes.
- The five section headers are a contract. Other skills may grep for them. Keep them verbatim: `## 1. Hours elapsed`, `## 2. brain/log.md entries added`, `## 3. Flags decayed`, `## 4. Commitments now overdue`, `## 5. Files modified in context/`.
- First-run behaviour is fixed: print the documented seed line, write the marker, stop. No delta on first run.
- The skill must work without git. The Bash tool is required only for the `git diff --name-only` call in Section 5; the other four sections run on pure filesystem reads.

<!-- private-tag: not applicable: since-last-session reads file modification times, log entry IDs, flag IDs, and git diff filenames. It does not ingest user-provided speech content. The marker file holds a single ISO-8601 timestamp, not narrative content. The private-tag exclusion contract has no narrative write surface to govern here. -->
