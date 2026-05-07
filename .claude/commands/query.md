---
description: Query the Founder OS graph and operating files. Three modes (index, timeline, full) for progressive disclosure. Read-only.
argument-hint: <question> | --mode timeline --anchor <slug> | --mode full --ids <id1,id2>
allowed-tools: ["Read", "Bash"]
---

# Founder OS query

Run the query skill at `skills/query/SKILL.md` end to end.

## Procedure

1. If `$ARGUMENTS` is empty, reply `What should I query? Re-run as /founder-os:query <question>.` and stop.
2. If `core/identity.md` does not exist, reply `Founder OS not set up here. Run /founder-os:setup first.` and stop.
3. If `skills/query/SKILL.md` is missing, reply `Query skill not found at skills/query/SKILL.md. Re-install the plugin.` and stop.
4. If `scripts/query.py` exists, run:

```bash
python scripts/query.py $ARGUMENTS
```

When `$ARGUMENTS` is a plain question (no `--mode` flag), pass it as a single quoted argument so the question is preserved as one string. When `$ARGUMENTS` already contains flags, pass it through as-is.

5. Print stdout verbatim. If the script exits non-zero, print stderr and stop.
6. If the script is missing, follow the manual procedure in the skill file.

## Forms

- `/founder-os:query <question>` - default `index` mode. Returns ~10 candidate nodes with IDs.
- `/founder-os:query --mode timeline --anchor <slug-or-id>` - returns entries within 7 days either side of the anchor, ordered chronologically.
- `/founder-os:query --mode full --ids <id1,id2,...>` - returns full bodies for the listed IDs.

Examples:

- `/founder-os:query outreach stalled`
- `/founder-os:query --mode timeline --anchor brain/flags.md`
- `/founder-os:query --mode timeline --anchor log-2026-05-07-001`
- `/founder-os:query --mode full --ids log-2026-05-07-001,log-2026-05-07-002`

## Progressive Flow

Recommended for any non-trivial question:

1. Start with `index` to see candidate nodes.
2. Pick one and run `timeline` anchored on it for surrounding context.
3. Pull specific IDs with `full` to read bodies end to end.

## Rules

- Read-only.
- No external dependencies.
- No em dashes or en dashes.
- No banned words.
