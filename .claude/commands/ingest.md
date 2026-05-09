---
description: Save a source for later. Say "ingest this" or "save this source" (or run /founder-os:ingest <url|path|text>). Files the source into raw/ with provenance, then proposes wiki updates the user approves before writing.
argument-hint: "<url | file path | pasted text>"
allowed-tools: ["Read", "Write", "Edit", "WebFetch", "Glob", "Grep", "Bash"]
---

# Founder OS ingest

Process a source into the OS with provenance preserved. Different from knowledge-capture: ingest writes the source to `raw/` and proposes wiki updates the user approves before writing.

## Procedure

1. Read the ingest skill at `skills/ingest/SKILL.md` and execute it end to end with the user-supplied argument.

2. The skill owns source detection, raw file creation, wiki update proposal, and approval flow. This command is a thin trigger.

3. If the skill file is missing, reply: `Ingest skill not found at skills/ingest/SKILL.md. This install is incomplete. Re-install the plugin or update via /founder-os:update.` and stop.

## Rules

- Only one auto-write: the source itself to `raw/`. All wiki updates require explicit user approval.
- If the install is empty (no `core/identity.md`), reply: `Founder OS not set up here. Run /founder-os:setup first.` and stop.
- No em dashes or en dashes. Hyphens only.
