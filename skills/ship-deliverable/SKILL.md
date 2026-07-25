---
name: ship-deliverable
description: Run the final ship gate before any external deliverable goes out. Say "ship this", "is this ready to ship", "final gate", or "run the ship checks" (or run /founder-os:ship-deliverable). Runs a deterministic scan first, then composes template fit, anti-AI scan, blind-spot evidence check, and pre-send-check in one report. Read-only.
why: "Composes four checks that are easy to skip individually under deadline pressure into one pass so nothing ships with an AI phrase, missing asset, or unreviewed blind spot."
enhance: "Run blind-spot-review before calling ship-deliverable - Link 3 (blind-spot evidence check) will fail if no review artifact exists, and you will have to run it separately anyway."
allowed-tools: ["Read", "Grep", "Bash"]
mcp_requirements: []
---

# Ship Deliverable

Runs on: local-exec - Link 0 runs a read-only scan script over the deliverable. On a surface that cannot run scripts, say so in one line, skip Link 0, and run Links 1 to 4 by reading. Never report Link 0 as passed when it did not run.

Composes the checks that are easy to skip under deadline pressure and reports every failure in one pass.

## Input

A path to the deliverable.

If the path is missing, reply: `Which deliverable? Re-run as /founder-os:ship-deliverable <path>.` and stop.

If the file does not exist, fail with the path and stop.

## The Links

Run every link every time. Do not stop at the first failure.

### Link 0 - Deterministic scan (run this first)

```
python scripts/deliverable_gate.py all <path>
```

Five checks a grep can settle without spending any judgment on them: structural fit, leftover placeholders, a prep date within 48 hours, AI-attribution strings and document author metadata, and evidence that a blind-spot pass actually happened. Exit 0 means nothing failed, exit 2 means something did.

Three things to hold onto when reading its output:

- **SKIP is honest, not a pass.** It names what a text scan cannot judge - a binary layout, a compressed PDF - and hands it to the reading links below. Never report a SKIP as a PASS.
- **Brand checks need `os-config.yaml`.** The font and the document author name come from your config. With no config those two checks SKIP rather than assume a default, which means the reading pass has to cover them.
- **A Link 0 FAIL is still a FAIL** even if the reading links all pass. It caught something real.

If the script is missing or your surface cannot run it, say so in one line and continue with Links 1 to 4. The reading links overlap it deliberately, so you lose speed and repeatability, not coverage.

### Link 1 - Template Fit

Read `skills/your-deliverable-template/SKILL.md` if it exists. Check whether the deliverable follows the founder's brand profile and the expected file-type structure.

If the brand or template skill is missing, record `WARN - template skill missing` and continue.

### Link 2 - Anti-AI Scan

Apply the baseline: use `rules/writing-style.md`; fall back to `templates/rules/writing-style.md` only if the local copy is missing.

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

You cannot invoke another skill from inside a skill in Claude Code. So this link runs the pre-send-check logic against the deliverable directly using the criteria defined in that skill file. If the user wants the full skill output independently, they can ask for the `pre-send-check` skill in a separate turn.

If `skills/pre-send-check/SKILL.md` does not exist, record `FAIL - pre-send-check skill file missing - cannot apply checks`.

## Output Format

```text
Ship deliverable: <path>
Run at <YYYY-MM-DD HH:MM>

Link 0 Deterministic:   PASS / FAIL / NOT RUN - <n checks, n fail, n left to reading>
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

- Read-only. Never modify the deliverable. Link 0's script writes nothing either.
- Run every link every time.
- If any link fails, verdict is `FIX THEN RETRY`.
- A human can override, but the override and failed links must be logged to `brain/log.md`.
