---
name: query
description: Search across the OS with a multi-hop query. Say "what blocks <priority>", "what connects to <client>", "what history explains <decision>", or "search the OS for <topic>" (or run /founder-os:query). Traverses `brain/relations.yaml` plus core operating files. Three modes (index, timeline, full) for progressive disclosure.
allowed-tools: ["Read", "Bash"]
mcp_requirements: []
---

# Query

This skill retrieves OS nodes for a question by walking markdown files and `brain/relations.yaml`. It uses plain files only. No vector database, no embeddings, no external service.

## Pre-Flight

If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`

If `brain/relations.yaml` is missing, tell the user to run `/founder-os:wiki-build` first, then continue with keyword search if enough files exist.

If `scripts/query.py` exists, use it. If not, perform the procedure manually.

## Three Modes

The script has three modes for progressive disclosure. Start with `index`, drill in with `timeline`, pull specific bodies with `full`.

### 1. index (default)

Returns ~10 candidate nodes with ID, path, first heading, decay flag if present, and a 1-line context. Target ~50 tokens per hit. Hard cap 10 hits. Use this on the first call when you do not yet know which entries you need.

```bash
python scripts/query.py "<the user's question, verbatim>"
```

Or explicit:

```bash
python scripts/query.py --mode index "<question>"
```

### 2. timeline

Given an anchor (file slug or brain ID), returns entries within 7 days either side, ordered chronologically. Target ~150 tokens per hit. Hard cap 20 hits. Use after `index` when you want to see what was happening around a specific node.

```bash
python scripts/query.py --mode timeline --anchor brain/flags.md
python scripts/query.py --mode timeline --anchor log-2026-05-07-001
```

If the anchor is a brain ID, the date is read from the ID itself. If the anchor is a file slug, the date is read from frontmatter (`updated:` or `date:`). If neither is present, file mtime is used as a fallback.

Definition: an "entry" in timeline mode is one markdown file (per-file granularity, dated by frontmatter or mtime). Per-heading granularity is parked for a later version.

### 3. full

Given a comma-separated list of IDs, returns the full body of each entry. No cap, the user explicitly asked for these. Use after `timeline` (or directly from `index`) when you want the actual content of a specific entry.

```bash
python scripts/query.py --mode full --ids log-2026-05-07-001,log-2026-05-07-002
```

For each ID the script searches every markdown file in scope and matches the ID either as a frontmatter `id:` line or as a trailing parenthetical on a heading line `(<id>)`. The body returned is the heading line plus all lines up to the next heading at the same depth or shallower. If no match is found, the output is `id <X>: not found` and the script continues with the next ID.

## Operating against a non-default root

The script accepts `--root <path>` to point at another Founder OS-style folder, such as a vendored archive or a fixture corpus. Use it when the current shell is outside the folder you want to query.

```bash
python scripts/query.py --root /path/to/archive "outreach stalled"
```

## Progressive Flow

Recommended pattern for any non-trivial question:

1. Call `index` mode with the question. Skim the 10 hits.
2. Pick one slug or ID that looks most relevant.
3. Call `timeline` mode anchored on that slug to see surrounding context.
4. Call `full` mode with the specific IDs you want to read end to end.

This keeps token cost low until the user commits to a deeper read.

## Manual Procedure (if script is missing)

1. Read `brain/relations.yaml`.
2. Read the boot files:
   - `CLAUDE.md`
   - `core/identity.md`
   - `context/priorities.md`
   - `context/decisions.md`
   - `rules/operating-rules.md`
3. Read `brain/patterns.md` and `brain/flags.md` if they exist.
4. Identify candidate nodes by keyword match against the user's question.
5. Walk curated and auto-generated edges up to 3 hops from each candidate.
6. Rank by keyword match, edge count, and recency.
7. Return the top 3 to 5 nodes with the path that connects each result to the question.

## Output Formats

### index mode

```text
QUERY: <user question>
---
Top results:

1. <node> (id: <id>) [DECAY soon (YYYY-MM-DD)] - <one-line context> - reached via: <path>
2. <node> - <one-line context> - reached via: <path>
...

Recommend reading: <single highest-value node>
```

### timeline mode

```text
TIMELINE: <anchor> (YYYY-MM-DD) +/- 7 days
---

YYYY-MM-DD - <node> (id: <id>)
  <first heading>
  <body lines, capped>
```

### full mode

```text
FULL: id1, id2
---

=== id1 (path) ===
<body block>
```

## Rules

- Read-only. Never write to `relations.yaml` or any brain file.
- No external dependencies. Pure Python stdlib.
- No embeddings or graph database in v1.7.
- `index` mode output stays under ~500 tokens total even with a corpus of 1000 markdown files (10-hit cap, 200-char context).
