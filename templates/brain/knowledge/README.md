# Knowledge Index

`brain/knowledge/` stores durable notes from books, podcasts, articles, calls, experiments, and founder observations. These files are first-class wiki pages. `wiki-build` reads their `[[wikilinks]]`; proposal and strategy skills can read their frontmatter and top heading.

## File Convention

Each knowledge file uses this shape. Every new file gets a stable ID per `rules/entry-conventions.md` (channel: `know`).

```yaml
---
id: know-YYYY-MM-DD-NNN
topic: <slug>
captured: <YYYY-MM-DD>
sources: [source title or URL]
tags: [book, podcast, article, conversation, experiment]
seats: <seat id, or none>   # optional - see Routing below
---

# <Topic>

## Takeaways

- <point>

## How this applies to my work

- <application>
```

## Routing a note to a seat (optional)

`seats:` is the one optional field, and it decides which digital employees see this note in their read-list. `python scripts/agents_sync.py apply` folds a POINTER - id, topic, path - into every seat you name. Never the body: the seat opens this file itself when it runs, which is the do-not-hard-parse rule below, unchanged.

| Value | Meaning |
|---|---|
| absent | never reviewed. The morning loop may ask about it once, when a slot is free |
| `seats: next-move-caller` | routed to that seat. Comma-separate for more than one |
| `seats: none` | reviewed and deliberately routed to nobody - the tombstone |

Write `seats: none` when you decline. It is what records the decision, so the same note is never raised at you again. Nothing tags a note on its own: `knowledge-capture` proposes at most one seat when it writes a note, the morning loop raises at most one untagged note per run, and only your yes writes the field. A tag naming a seat that is no longer on the chart is reported by `agents_sync check` as a dangling tag and left alone, in case the seat comes back.

## Index

| ID | Topic | Captured | Tags | Source |
|---|---|---|---|---|
| know-YYYY-MM-DD-NNN | Example | 2026-01-01 | example | Replace this row after your first capture |

## Rules

- Keep raw transcripts and full source copies in `raw/` when provenance matters.
- Use `brain/knowledge/` for distilled, reusable notes.
- Do not hard-parse note bodies. Skills read frontmatter, headings, and user-approved excerpts.
