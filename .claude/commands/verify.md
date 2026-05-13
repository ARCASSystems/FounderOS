---
description: Check that Founder OS is healthy. Say "verify the OS" or "health check" (or run /founder-os:verify). Returns a structured report across 8 substrate checks. Read-only. Never auto-fixes.
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

# Founder OS verify

Read-only health check. Returns a structured report across 8 substrate checks.

## Procedure

1. Read the verify skill at `skills/verify/SKILL.md` and execute it end to end.

2. The skill owns all eight checks, the output format, and the summary footer. This
   command is a thin trigger.

3. If the skill file is missing, reply: `Verify skill not found at skills/verify/SKILL.md.
   Re-install or update via /founder-os:update.` and stop.

## Rules

- Read-only. Do not write to any file.
- This command never auto-fixes anything. It only reports.
- No em dashes or en dashes. Hyphens only.
