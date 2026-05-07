---
description: Query the Founder OS graph and operating files for the 3 to 5 most relevant nodes. Read-only.
argument-hint: <question>
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
python scripts/query.py "$ARGUMENTS"
```

5. Print stdout verbatim. If the script exits non-zero, print stderr and stop.
6. If the script is missing, follow the manual procedure in the skill file.

## Rules

- Read-only.
- No external dependencies.
- No em dashes or en dashes.
- No banned words.
