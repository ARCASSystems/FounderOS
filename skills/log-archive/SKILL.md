---
name: log-archive
description: >
  Age the running brain log so a long-lived install stays lean. Say "archive my log", "my log is getting long", "trim the brain log", or "the log is over the cap". Moves the oldest entries out of brain/log.md into monthly archives at brain/archive/log-YYYY-MM.md and leaves a one-line pointer behind, so the file every skill reads stays small while history is preserved. Deterministic script, no LLM call, free-tier safe. Run it when the SessionStart brief or a long session shows the log past its 300-line cap.
why: "brain/log.md is read by output skills and the SessionStart brief; once it carries months of history every read pays for all of it. Aging old entries into monthly archives keeps the hot file small and the install responsive over time, while the pointer keeps history one hop away."
enhance: "Run after a heavy logging stretch or when the brief flags the log over cap. The script is idempotent - once the log is under the cap it does nothing - and never splits an entry, so running it twice is safe."
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# Log Archive

Runs on: local-exec - runs a local script against your files. A local-runtime agent runs it (Claude Code is the reference). A cloud or read-only surface reads the produced archive and pointer instead and says so.

Keeps `brain/log.md` lean. When the log grows past its cap (default 300 lines), the oldest entries move to `brain/archive/log-YYYY-MM.md`, grouped by month, and the log keeps only the most recent entries plus a one-line pointer to the archive. The pointer is the cache summary: it says history exists and where, without carrying the detail.

This is the running-log half of the context discipline in the Session Protocol: a small desk, the rest of the history in the filing cabinet, retrieved only when needed.

---

## Pre-flight

If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`

If `scripts/log-archive.py` does not exist, stop with: `Log-archive script not found. Run /founder-os:setup or /founder-os:update to install it.`

## Procedure

1. To preview without writing, run `python scripts/log-archive.py --dry-run` and report the result.
2. To archive, run `python scripts/log-archive.py`. Use `--cap N` only if the operator asks for a different line cap.
3. Report the script's stdout verbatim.
4. If the script exits non-zero, report stderr verbatim and stop. Do not hand-edit the log to "fix" it - the script is the safe path; hand-editing a long log is how entries get lost.

## What it guarantees

- Never splits an entry. An entry moves whole or stays whole.
- Never archives an entry it cannot date. Undated entries stay in `brain/log.md`.
- Idempotent. Once the log is under the cap, a re-run writes nothing.
- Conserves entries. Every entry is either still in the log or in an archive file, never dropped.

## Output format

Single fenced block, the script's own report:

```
LOG ARCHIVE - YYYY-MM-DD
Cap 300 lines. Log was N lines, M entries.
Archived K entries to: brain/archive/log-YYYY-MM.md (K)
Log now 300 lines, P entries. Pointer updated.
```

When the log is already under the cap, report the "Nothing to archive." line instead.

## Voice

- No commentary outside the output block.

<!-- private-tag: not applicable: moves dated log entries between files (structured records, not user-provided speech); no private data introduced -->
