# Knowledge Index

`brain/knowledge/` stores durable notes from books, podcasts, articles, calls, experiments, and founder observations. These files are first-class wiki pages. `wiki-build` reads their `[[wikilinks]]`; proposal and strategy skills can read their frontmatter and top heading.

## File Convention

Each knowledge file uses this shape:

```yaml
---
topic: <slug>
captured: <YYYY-MM-DD>
sources: [source title or URL]
tags: [book, podcast, article, conversation, experiment]
---

# <Topic>

## Takeaways

- <point>

## How this applies to my work

- <application>
```

## Index

| Topic | Captured | Tags | Source |
|---|---|---|---|
| Example | 2026-01-01 | example | Replace this row after your first capture |

## Rules

- Keep raw transcripts and full source copies in `raw/` when provenance matters.
- Use `brain/knowledge/` for distilled, reusable notes.
- Do not hard-parse note bodies. Skills read frontmatter, headings, and user-approved excerpts.
