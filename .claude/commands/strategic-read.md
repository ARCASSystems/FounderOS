---
description: Produce a state-of-the-OS report from the current file layer. Say "give me a strategic read", "where am I", or run /founder-os:strategic-read. Returns 5 sections: Identity anchor, Active commitments and pipeline, Open decisions, Active flags, Next 3 recommended moves. Read-only.
allowed-tools: ["Read", "Glob", "Grep"]
---

# Founder OS strategic read

Run the strategic-read skill at `skills/strategic-read/SKILL.md` end to end. No arguments.

## Procedure

1. If `core/identity.md` does not exist, reply `Founder OS not set up here. Run /founder-os:setup first.` and stop.
2. If `skills/strategic-read/SKILL.md` is missing, reply `strategic-read skill not found at skills/strategic-read/SKILL.md. Re-install the plugin.` and stop.
3. Follow the strategic-read skill instructions exactly. Read each file in the documented order, run the stale-context check, then render the 5-section report.
4. Output the structured block defined in the skill. Nothing before, nothing after.

## When to use

- Returning to the OS after a gap and needing one orientation pass.
- Before a planning session, to anchor on current state instead of last remembered state.
- When a question touches priorities, pipeline, decisions, and flags at once.

## When NOT to use

- A single-channel question. Use `/today` for the day or `/founder-os:brain-pass "<question>"` for synthesis on a specific topic.
- A keyword match. Use `/founder-os:query "<keyword>"`.

## Examples

- `/founder-os:strategic-read`
- "give me a strategic read"
- "where am I across the OS"

## Rules

- Read-only. This is a read of your current files; nothing is auto-modified.
- No external dependencies. No paid API.
- No em dashes or en dashes.
- No banned words.
- Cite stable entry IDs where they exist. Summarise, do not paste raw bodies.
- If the daily anchor or weekly commitments header is stale, the report prepends a STALE line and recommends refreshing before re-running.
