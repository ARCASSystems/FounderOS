---
name: observation-rollup
description: >
  Roll up weekly observation logs. Say "roll up observations" or "compress old logs" (or run /founder-os:observation-rollup). Compresses JSONL observation files older than 10 days into weekly markdown summaries and deletes the source files. Idempotent - safe to run anytime.
mcp_requirements: []
---

# Observation Rollup

Compress old observation logs into weekly summaries. Runs `scripts/observation-rollup.py` and reports the result.

## When to use

Run this skill when the SessionStart brief surfaces a nudge about unrolled JSONL files older than 10 days. Also safe to run anytime - idempotent runs produce no changes on already-rolled weeks.

Triggered by: "roll up observations", "compress old logs", "compact observations", `/founder-os:observation-rollup`.

## Procedure

1. Verify `scripts/observation-rollup.py` exists at the repo root.
2. Run: `python scripts/observation-rollup.py`
3. Report the output: what rolled, what was skipped, any errors.
4. If rollups were written, note the count of summary files now in `brain/observations/_rollups/`.

## What the script does

- Walks `brain/observations/*.jsonl`. Filenames must be `YYYY-MM-DD.jsonl`.
- Groups files by ISO week (`YYYY-Wnn`).
- For each week with >= 7 days of data AND today >= 3 days past the week-end:
  - Aggregates: total observations, tool counts, top 5 tools, skill invocations, unique session IDs.
  - Writes `brain/observations/_rollups/YYYY-Wnn.md`.
  - Deletes source JSONL files only after the rollup is verified written.
- Weeks with < 7 days of data or that ended < 3 days ago are skipped.
- Weeks already rolled are skipped (idempotent).

## Requirements

- Python stdlib only. No pip installs, no API keys, no external services.
- `FOUNDER_OS_OBSERVATIONS=1` must have been set to produce any JSONL files.
- If `brain/observations/` is empty, the script exits cleanly with no changes.
