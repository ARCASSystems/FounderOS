# raw/ - Source Documents

This folder holds the raw, immutable source documents your OS has ingested. Podcasts, articles, books, conversations, threads, transcripts, anything you fed in.

## Convention

- **Immutable.** Once a source lands here, the LLM never edits it. All derived content (summaries, entity pages, decision references) lives in the wiki layer with a link back here.
- **One file per source.** Filename pattern: `YYYY-MM-DD-<short-slug>.md`.
- **Provenance via frontmatter.** Every file starts with the block below.

## Frontmatter spec

```yaml
---
source_type: podcast | book | article | conversation | thread | document | gist | transcript | other
source_url: <if applicable, otherwise omit>
source_title: <required>
source_author: <if known, otherwise omit>
ingested_at: YYYY-MM-DD
ingested_by: <skill name, e.g. ingest>
wiki_pages:
  - <relative path of wiki file this source seeded or updated>
  - <another path>
---
```

## How sources land here

The `/founder-os:ingest` skill is the standard entry point. It writes the raw source to this folder, then proposes wiki updates that you approve before they land.

Manual paste also works - drop a file here with the frontmatter above and it counts as an ingested source for `/founder-os:lint` purposes.

## What this folder is NOT

- **Not the wiki.** Don't read raw files for context during normal operation. The wiki layer (context/, brain/, cadence/) is the working memory. Raw is the archive.
- **Not auto-cleaned.** Raw stays forever unless you explicitly delete a file.
- **Not for thoughts.** Use `brain/log.md` for unsourced observations and `knowledge-capture` skill for "I read something, here are my takeaways" without source preservation.
