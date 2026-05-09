---
name: wiki-build
description: >
  Rebuild the wiki graph from extracted [[wikilinks]]. Say "rebuild the wiki graph", "refresh relations", "build the wiki graph", or "extract wikilinks" (or run /founder-os:wiki-build). Walks all markdown, extracts Obsidian-style [[wikilinks]], and refreshes the auto-generated section in `brain/relations.yaml`. Companion to lint - lint checks the wiki, wiki-build keeps the graph fresh. Run after a session that added cross-references between files.
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# Wiki Build

Refreshes the auto-extracted half of `brain/relations.yaml`. The hand-curated `relations:` section is preserved.

This skill must:
- Run end to end on a fresh install (clean output, no false positives).
- Refuse with a clear error if `brain/relations.yaml` is missing or has corrupt sentinel markers.
- Be idempotent. Running twice in a row produces no diff.
- Never write to any file other than `brain/relations.yaml`.
- Never modify the hand-curated `relations:` section.

---

## Pre-flight

If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`

If `scripts/wiki-build.py` does not exist, stop with: `Wiki-build script not found. Run /founder-os:setup or /founder-os:update to install it.`

## Scope

Scans these directories for `[[wikilinks]]`:

- `core/`
- `context/`
- `cadence/`
- `brain/`
- `network/`
- `companies/`
- `roles/`
- `rules/`

Excluded: plugin-internal (`.claude/`, `skills/`, `templates/`, `docs/`), source archive (`raw/`), brain archive (`brain/archive/`), transient brain (`brain/transcripts/`, `brain/rants/`), `.git/`, `node_modules/`.

Wikilinks inside fenced code blocks (` ``` `) and inline backtick spans (`` ` ``) are ignored. This means documentation that describes the wikilink syntax does not pollute the graph.

## Wikilink syntax

| Form | Meaning |
|---|---|
| `[[target]]` | Bare slug. Resolved at query time, not at build time. |
| `[[target.md]]` | Explicit file path (basename or repo-relative). |
| `[[target.md#anchor]]` | File with heading anchor. |
| `[[target\|display text]]` | Alias form. Display text is discarded for the graph. |

## Procedure

1. Run `python scripts/wiki-build.py`.
2. Report the script's stdout line verbatim (example: `Wrote 12 wiki links from 4 source files into brain/relations.yaml`).
3. If the script exits non-zero, report stderr verbatim and stop. Do not attempt automatic recovery.

## Output format

Single fenced block:

```
WIKI BUILD - YYYY-MM-DD

Wrote N wiki links from M source files into brain/relations.yaml

Hand-curated relations: P entries (preserved)
```

If the script errored, replace the success line with the error verbatim.

## Companion to lint

Wiki-build keeps the graph fresh. Lint audits the graph. Run wiki-build before lint when the wiki layer has changed materially since the last build. Lint will surface stale graph as orphans or broken cross-references.

## Voice

- No em dashes or en dashes. Hyphens only.
- No commentary outside the output block.
- No banned words (delve, robust, seamless, leverage as verb, comprehensive, holistic, transformative, streamline, optimize, utilize, facilitate, unlock, navigate, ecosystem, landscape).
