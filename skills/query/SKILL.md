---
name: query
description: Use when the founder asks a multi-hop question across their OS, such as what blocks a priority, what connects to a client, or what history explains a decision. Traverses `brain/relations.yaml` plus core operating files.
allowed-tools: ["Read", "Bash"]
mcp_requirements: []
---

# Query

This skill retrieves the 3 to 5 most relevant OS nodes for a question by walking markdown files and `brain/relations.yaml`. It uses plain files only. No vector database, no embeddings, no external service.

## Pre-Flight

If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`

If `brain/relations.yaml` is missing, tell the user to run `/founder-os:wiki-build` first, then continue with keyword search if enough files exist.

If `scripts/query.py` exists, use it. If not, perform the procedure manually.

## Script Path

Take the user's question (the literal text they typed after `/founder-os:query`) and pass it as a single quoted argument:

```bash
python scripts/query.py "<the user's question, verbatim>"
```

Substitute the question text directly. Do not rely on shell variables like `$ARGUMENTS` - those are not exposed in the Claude Code Bash tool context. If the question contains double quotes, escape them with `\"`.

Print the script output verbatim. If the script exits non-zero, print the error and stop.

## Manual Procedure

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

## Output Format

```text
QUERY: <user question>
---
Top results:

1. <node> - <one-line context> - reached via: <path>
2. <node> - <one-line context> - reached via: <path>
3. <node> - <one-line context> - reached via: <path>

Recommend reading: <single highest-value node>
```

## Rules

- Read-only. Never write to `relations.yaml` or any brain file.
- No external dependencies.
- Do not use embeddings or a graph database in v1.6.
- If the answer needs more than 5 nodes, still show 5 and tell the user which one to read first.
- No em dashes, no en dashes, no banned words.

## Later Path

Embedding retrieval and graph databases stay parked for v1.7+ behind the triggers in `ROADMAP.md`.
