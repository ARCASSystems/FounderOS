---
name: lint
description: >
  Audit the wiki for integrity issues. Say "lint the wiki", "check wiki integrity", "find broken links", "what's stale", or "what's drifted" (or run /founder-os:lint). Five checks: broken cross-references, orphan pages, stale time-sensitive content, provenance gaps, and contradictions. Read-only - findings are advisory. Run before a weekly review.
allowed-tools: ["Read", "Glob", "Grep"]
mcp_requirements: []
---

# Lint

Read-only audit of the wiki layer. Returns a structured report. Never modifies files.

This skill must:
- Run end to end on a fresh install (clean output, no false positives).
- Run on a populated install and surface real findings with file:line references.
- Render in under 5 seconds for installs with under 1000 wiki files.
- Never write to any file.

---

## Pre-flight

If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`

## Scope

The wiki layer is the directories listed in `scripts/wiki-build.py:INCLUDE_PREFIXES`. That file is the canonical source of truth. Currently: `core/`, `context/`, `cadence/`, `brain/` (including `brain/knowledge/`), `network/`, `companies/`, `roles/`, `rules/`. Keep this prose list in sync with the script when prefixes change.

Skill files (`skills/`), templates (`templates/`), commands (`.claude/commands/`), hooks (`.claude/hooks/`), docs (`docs/`), and root metadata (`README.md`, `CLAUDE.md`, `VERSION`, etc.) are NOT scanned. Raw layer (`raw/`) is scanned only for provenance gaps (Check 4).

## Check 1 - Broken cross-references

Scan all wiki files for `[[link]]` patterns. For each:

- If the link points to an existing file, OK.
- If the link points to a missing file, flag.
- If the link uses an ambiguous slug that matches multiple files, flag with all candidates AND name the deterministic pick. Resolution order: scan directories in the order listed in `scripts/wiki-build.py:INCLUDE_PREFIXES`, then alphabetical within the first matching directory. The first match wins. Format the output as `[[slug]] -> ambiguous: <candidate list>; would resolve to <first match>`.

`[[link]]` syntax accepts: `[[file.md]]`, `[[path/to/file.md]]`, `[[page-name]]` (resolves to first match across the wiki).

## Check 2 - Orphan pages

For each wiki file, check whether any other wiki file references it (`[[]]` link, plain markdown link, or filename mention).

Pages that are intentional roots and never get linked TO are exempt:
- `core/identity.md`
- `context/priorities.md`, `context/clients.md`, `context/companies.md`, `context/decisions.md`
- `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, `cadence/quarterly-sprints.md`, `cadence/annual-targets.md`
- `brain/log.md`, `brain/flags.md`, `brain/patterns.md`, `brain/decisions-parked.md`, `brain/needs-input.md`, `brain/index.md`, `brain/relations.yaml`
- All files under `roles/` (registry + role definitions; loaded by mode, not by reference)
- All files under `rules/` (operating rules + entry conventions; loaded by mode, not by reference)
- All `README.md` files

Anything else with zero inbound references is flagged as orphan.

## Check 3 - Stale time-sensitive content

| File | Stale threshold |
|---|---|
| `cadence/daily-anchors.md` | Top `## Today:` header date is more than 3 days behind today |
| `cadence/weekly-commitments.md` | Top `## Week of` date is more than 7 days behind today |
| `cadence/quarterly-sprints.md` | If file exists, oldest unresolved item is more than 90 days old |
| `context/decisions.md` | Any decision marked `pending` with no update in 14+ days |
| `context/clients.md` | Any client row with `Last contact` (or equivalent last-touch) field 30+ days behind today |
| `brain/flags.md`, `brain/patterns.md` | Any entry whose anchor date (flag header date / `First observed:`) is 30+ days behind today AND the entry does NOT have a `Decay after:` field. Soft signal, not a defect. Parked decisions are excluded by convention (`rules/entry-conventions.md` defines them as trigger-driven, not date-driven). |
| `brain/log.md` | File exceeds 300 lines (documented cap in `templates/brain/log.md:2` and `templates/brain/index.md:33`). |

Use the dated headers and frontmatter dates first. Fall back to file mtime only if no in-content dates.

### Decay-convention adoption gap

For each entry in `brain/flags.md` (`##` headings) and `brain/patterns.md` (`###` headings):

- Determine the anchor date. For flags: the date in the heading line (`## YYYY-MM-DD - <title>`). For patterns: a `First observed:` line.
- If anchor date is 30+ days behind today AND the entry has no `Decay after:` field: flag.

Render under STALE CONTENT, prefixed `decay-gap`:

`decay-gap brain/flags.md: "<entry heading>" - <N> days old, no Decay after: field. Suggest: Decay after: <today YYYY-MM-DD>`

This is a soft suggestion, not a defect. The user may have deliberately omitted the field. Cap at the 5 oldest entries per file to avoid flooding.

`brain/decisions-parked.md` is intentionally excluded. The entry conventions in `rules/entry-conventions.md` define parked decisions as trigger-driven (no auto-decay), so a parked entry without `Decay after:` is the documented default, not a gap. The seeded template ships an example with no `Decay after:` for the same reason; flagging it would be noise on a fresh install.

### Log size cap

If `brain/log.md` exceeds 300 lines, output under STALE CONTENT:

`log-cap brain/log.md: <N> lines (cap is 300). Move oldest entries to brain/archive/log-<YYYY-MM>.md.`

The cap is a writing convention (not a hard limit). This is a reminder, not a defect.

## Check 4 - Provenance gaps

Scan `raw/`:

- Any raw file with empty `wiki_pages: []` AND ingested more than 14 days ago - flag as "ingested but unused".
- Any wiki file containing `[[raw/<filename>]]` where the raw file does not exist - flag as "broken provenance link".

If `raw/` does not exist, skip this check entirely (not all installs use ingest).

## Check 5 - Possible contradictions

Heuristic, not deterministic. Flag for human review, never auto-fix.

For each decision marked `resolved` in `context/decisions.md`, check whether `cadence/weekly-commitments.md` (current week + previous week retro) or `context/priorities.md` contains text that explicitly contradicts the resolution. Examples:
- Decision resolved: "Stop building feature X." Weekly commitments contains: "Build feature X this week."
- Decision resolved: "Hire first ops lead." Priorities contains: "Defer all hires."

This is a low-confidence signal. Output as candidates, not as defects. Phrasing: `Possible contradiction (review): <decision> vs <commitment>`.

---

## Output format

Single fenced block. Same skeleton as `/founder-os:status` for visual consistency.

```
FOUNDER OS LINT - <total findings count>
Last checked: <YYYY-MM-DD>

CROSS-REFERENCES (<N> issues)
- <file:line>: [[broken-link]] -> file does not exist
- <file:line>: [[ambiguous-slug]] -> ambiguous: <list>; would resolve to <first match>
(or: "Clean.")

ORPHAN PAGES (<N> issues)
- <file>: no inbound references
(or: "Clean.")

STALE CONTENT (<N> issues)
- cadence/daily-anchors.md: top header is YYYY-MM-DD (5 days stale)
- context/decisions.md: <decision title> pending since YYYY-MM-DD (18 days)
- decay-gap brain/flags.md: "<entry heading>" - 42 days old, no Decay after: field. Suggest: Decay after: YYYY-MM-DD
- log-cap brain/log.md: 327 lines (cap is 300). Move oldest entries to brain/archive/log-YYYY-MM.md.
(or: "Clean.")

PROVENANCE (<N> issues)
- raw/<filename>: ingested YYYY-MM-DD, wiki_pages empty (24 days unused)
- context/<file>:line: [[raw/<missing>]] -> raw file does not exist
(or: "Clean." or: "raw/ not present, skipped.")

POSSIBLE CONTRADICTIONS (<N> candidates)
- <decision> (resolved YYYY-MM-DD) vs <commitment in cadence/weekly-commitments.md>
(or: "Clean.")

NEXT 3 MOVES (advisory)
- <highest-priority finding to address>
- <second>
- <third>
```

If a section has zero findings, render a single `Clean.` line under that header.

If total findings count is zero, output:

```
FOUNDER OS LINT - 0 findings
Last checked: <YYYY-MM-DD>

Clean across all checks. Nothing to address.
```

---

## Output rules

- No em dashes or en dashes. Hyphens only.
- No banned words.
- Read-only. Never modify any file. If you find something that obviously should be fixed, name it under NEXT 3 MOVES, do not edit.
- One finding per line. No paragraphs.
- File:line references where possible. File-only references where line is not meaningful (orphans, stale headers).

## Edge cases

- **No wiki files yet.** Output: `Empty install. Nothing to lint. Run /founder-os:setup first.`
- **`raw/` does not exist.** Skip Check 4 entirely. Don't list this as an issue.
- **Network/ folder missing.** Skip silently - it's optional in many installs.
- **Companies/ folder missing.** Skip silently - some founders run a single business.
- **Very large install (>1000 wiki files).** Continue but warn at the top: `Large install (<count> files). Lint took <duration>. Consider archiving older content.`
