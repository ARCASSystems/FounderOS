---
description: Distil unprocessed rants into the brain layer. Writes a 5-line digest. Updates patterns, flags, parked decisions, needs-input, and client signals as warranted.
---

# Dream

Process all unprocessed rants in `brain/rants/`. Distil what surfaced. Write a tight 5-line digest. Hard cap on output. The user will not read more than 5 lines.

## Procedure

1. Walk `brain/rants/`. For each file, parse entries by frontmatter. Collect every entry where `processed: false`.

2. For each unprocessed entry, classify what it contains:
   - **Pattern** - recurring theme, observation, framework. Append to `brain/patterns.md`.
   - **Flag** - stall, frustration, role feedback, friction. Append to `brain/flags.md` with `Status: **OPEN.**` and Severity Week 1 unless escalation is obvious.
   - **Parked decision** - idea waiting for a trigger. Append to `brain/decisions-parked.md` with a Trigger to revisit line.
   - **Need / blocker** - something the user must do or decide. Add or update a row in `brain/needs-input.md` (Specific + Impact columns).
   - **Client signal** - mention of a named person or company that warrants tracking. Update `context/clients.md`.
   - **Log only** - context, no action needed. Skip; the rant file itself is the record.

3. After distillation, mark each processed entry `processed: true` in its rants file.

4. Append a digest entry to the top of `brain/log.md`. Format exactly:

   ```markdown
   ### <YYYY-MM-DD> #dream

   **DREAMT:** <date range>, <N> rants processed
   - <one signal in one line, max 90 chars>
   - <one signal in one line, max 90 chars>
   - <one signal in one line, max 90 chars>
   **Action:** <single recommendation, one line, max 90 chars>
   ```

5. Output to chat: print only the 5 digest lines exactly as written to log.md. Nothing else. No preamble. No closing summary.

## Rules

- Hard cap on chat output: 5 lines after the heading line. If 7 patterns surfaced, pick the 3 most load-bearing. The rest are still written into `brain/patterns.md`.
- One Action only. Not a list of three.
- If zero rants are unprocessed, output exactly: `Nothing to dream. <N> rants total, all processed.`
- Do not ask the user questions inside `/dream`. If something is genuinely ambiguous, route it to `brain/needs-input.md` instead.
- Mark processed flag flips as a single edit per file, not per entry.
- Voice rules apply to all writeback (no em dashes, no banned words). The raw rant text in the rants file is exempt - it stays verbatim.
