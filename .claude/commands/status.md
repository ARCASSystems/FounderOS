---
description: Founder OS readiness check. Returns a weighted score across Core, Voice and Brand, Cadence, Business Context, and Brain Layer. Surfaces the next 3 high-impact moves. Read-only.
allowed-tools: ["Read", "Glob", "Grep"]
---

# Founder OS status

Read-only readiness check. Reads the OS state and returns a single fenced score block.

## Procedure

1. Read the readiness skill at `skills/readiness-check/SKILL.md` and execute it end to end.

2. The skill owns the scoring logic, file reads, and output rendering. This command is a thin trigger.

3. If the skill file is missing, reply: `Readiness skill not found at skills/readiness-check/SKILL.md. This install is incomplete. Re-install the plugin.` and stop.

## Rules

- Read-only. Do not write to any file.
- Output is a single fenced block. No commentary before, after, or around it.
- If the install is empty (no `core/identity.md`), reply: `Founder OS not set up here. Run /founder-os:setup first.` and stop.
- No em dashes or en dashes. Hyphens only.
