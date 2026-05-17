---
name: today
description: >
  Show today's one-screen brief: anchor task, open flags, last 3 log entries, and next event. Say "what's on for today?" or "what's my day look like" (or run /today).
why: "Gives you a one-screen brief of what matters today without loading every context file - anchor, flags, recent log, and next calendar event in under 20 lines."
enhance: "Keep cadence/daily-anchors.md rolled to today and log at least one entry to brain/log.md during the day - a stale anchor and empty log make the brief generic rather than specific."
mcp_requirements: []
---

# Today

The user is asking for the today brief. Run the `/today` command. In Cowork mode, where slash commands do not fire, print the equivalent output by reading `cadence/daily-anchors.md`, `context/decisions.md`, `brain/flags.md`, and `brain/log.md` using the same structure as `.claude/commands/today.md`.

Keep it read-only. No commentary outside the brief.
