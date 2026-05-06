---
description: Read-only audit of the Founder OS wiki integrity. Flags broken cross-references, orphan pages, stale time-sensitive content, provenance gaps, and possible contradictions. Never auto-fixes.
allowed-tools: ["Read", "Glob", "Grep"]
---

# Founder OS lint

Read-only wiki audit. Surfaces issues, never fixes them.

## Procedure

1. Read the lint skill at `skills/lint/SKILL.md` and execute it end to end.

2. The skill owns the scan logic, file reads, and output rendering. This command is a thin trigger.

3. If the skill file is missing, reply: `Lint skill not found at skills/lint/SKILL.md. This install is incomplete. Re-install the plugin or update via /founder-os:update.` and stop.

## Rules

- Read-only. Never modify any file.
- Output is a single fenced report block. No commentary before, after, or around it.
- If the install is empty (no `core/identity.md`), reply: `Founder OS not set up here. Run /founder-os:setup first.` and stop.
- No em dashes or en dashes. Hyphens only.
