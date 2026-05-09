---
description: Show what's on for today. Say "what's on for today?" (or run /today). 20-line view: anchor, open decisions, active flags, last 3 log entries, next calendar event.
---

# Today

One-screen view of what matters today. No scrolling. No prose. Read-only.

## Procedure (in order)

1. Read `cadence/daily-anchors.md`. Extract the `## Today:` section: anchor line + top 3 tasks.

2. Read `context/decisions.md`. Extract the top 3 Pending decisions by deadline proximity.

3. Read `brain/flags.md`. Extract active flags. Top 3.

4. Read `brain/log.md`. Extract the first line of the last 3 entries (newest on top).

5. If a calendar MCP is available (Google Calendar, Outlook), fetch the next scheduled event within the next 24 hours. Otherwise skip that line.

6. Render the output as a single fenced block, exactly this structure. No commentary before, after, or around it.

   ```
   TODAY - <YYYY-MM-DD>
   Anchor: <anchor line from daily-anchors>

   OPEN DECISIONS (top 3 by deadline)
   - <title> - <deadline>
   - <title> - <deadline>
   - <title> - <deadline>

   ACTIVE FLAGS
   - <flag name>
   - <flag name>
   - <flag name>

   LAST 3 SESSIONS
   - <first line of session entry 1>
   - <first line of session entry 2>
   - <first line of session entry 3>

   NEXT: <calendar event title at HH:MM> | <"no scheduled event next 24h">
   ```

7. If a section has nothing, write the header and one line: `none open.` Do not skip the section.

## Rules

- Read-only. Do not write to any file.
- Do not invoke other skills.
- No commentary outside the fenced block.
- If the daily anchor is stale (current date past `## Today:`), prepend a top line: `STALE: anchor date is <X>. Roll cadence/daily-anchors.md first.`
- Keep total under 20 lines.
- No em dashes or en dashes. Hyphens only.
- This command works only inside a Founder OS install. If the `cadence/` folder is missing, reply: `Founder OS not installed here. Run /founder-os:setup first.`
