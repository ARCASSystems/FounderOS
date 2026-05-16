---
name: ship-deliverable
description: Run the final ship gate before any external deliverable goes out. Say "ship this", "is this ready to ship", "final gate", or "run the ship checks" (or run /founder-os:ship-deliverable). Composes template fit, anti-AI scan, blind-spot evidence check, and pre-send-check in one report. Read-only.
allowed-tools: ["Read", "Grep"]
mcp_requirements: []
---

# Ship Deliverable

Composes the checks that are easy to skip under deadline pressure and reports every failure in one pass.

## Input

A path to the deliverable.

If the path is missing, reply: `Which deliverable? Re-run as /founder-os:ship-deliverable <path>.` and stop.

If the file does not exist, fail with the path and stop.

## The Four Links

Run all four links every time. Do not stop at the first failure.

### Link 1 - Template Fit

Read `skills/your-deliverable-template/SKILL.md` if it exists. Check whether the deliverable follows the founder's brand profile and the expected file-type structure.

If the brand or template skill is missing, record `WARN - template skill missing` and continue.

### Link 2 - Anti-AI Scan

Apply the baseline from `rules/writing-style.md` or `templates/rules/writing-style.md`:

- No em dashes or en dashes.
- No rule-of-three filler.
- No meta-commentary such as "in this document".
- No hype phrases.
- No banned words listed in the writing rules.

Record line numbers for any hit.

### Link 3 - Blind-Spot Evidence

Confirm `blind-spot-review` has run on this deliverable in this session or the immediately prior session. Accept any of these signals:

- A blind-spot memo file that references the deliverable filename.
- A `brain/log.md` entry in the last 100 lines that includes the deliverable filename and `blind spot`, `second pass`, `review`, or `nine categories`.
- A review artifact in the same folder as the deliverable.

If no evidence exists, record `FAIL - run blind-spot-review first`.

### Link 4 - Pre-Send Check

Read `skills/pre-send-check/SKILL.md` and apply its checklist to this deliverable inline. The check covers voice consistency, source truth, recipient, date, token replacement, asset paths, and filing hygiene.

You cannot invoke another skill from inside a skill in Claude Code. So this link runs the pre-send-check logic against the deliverable directly using the criteria defined in that skill file. If the user wants the full skill output independently, they can run `/founder-os:pre-send-check` in a separate turn.

If `skills/pre-send-check/SKILL.md` does not exist, record `FAIL - pre-send-check skill file missing - cannot apply checks`.

## Output Format

```text
Ship deliverable: <path>
Run at <YYYY-MM-DD HH:MM>

Link 1 Template:        PASS / WARN / FAIL - <detail>
Link 2 Anti-AI:         PASS / FAIL - <detail>
Link 3 Blind-spot run:  PASS / FAIL - <detail>
Link 4 Pre-send check:  PASS / FAIL - <detail>

Verdict: READY TO SEND | FIX THEN RETRY
Failed links: <comma-separated link numbers, or N-A if all passed>
```

If ready, state that the file is ready for the intended channel and log the ship event to `brain/log.md`.

If not ready, list every fix grouped by link. Do not edit the deliverable.

## Rules

- Read-only. Never modify the deliverable.
- Run all four links every time.
- If any link fails, verdict is `FIX THEN RETRY`.
- A human can override, but the override and failed links must be logged to `brain/log.md`.
