---
name: today
description: >
  Show the today brief. Say "what's on for today?" (or run /today). Thin skill wrapper for the daily one-screen view.
mcp_requirements: []
---

# Today

The user is asking for the today brief. Run the `/today` command. In Cowork mode, where slash commands do not fire, print the equivalent output by reading `cadence/daily-anchors.md`, `context/decisions.md`, `brain/flags.md`, and `brain/log.md` using the same structure as `.claude/commands/today.md`.

Keep it read-only. No commentary outside the brief.
