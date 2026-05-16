---
name: queue
description: >
  Manage the work queue. Say "what's on my plate", "what's moving", "show me the queue",
  "add to queue: <thing>", "start <description>", "done with <description>", or "park
  <description>" (or run /founder-os:queue). Reads cadence/queue.md. The ACTIVE section
  is capped at 3 items - the skill enforces this gate before starting new work.
allowed-tools: ["Read", "Edit", "Write", "Glob"]
mcp_requirements: []
---

# Queue

The queue lives at `cadence/queue.md`. Three lifecycle states: ACTIVE, BACKLOG, DONE.

## What it reads

`cadence/queue.md` - the queue file. Three sections: ACTIVE (max 3), BACKLOG (no cap),
DONE (last 7 days). If the file does not exist, create it from
`templates/cadence/queue.md` before proceeding.

## Five operations

### read

Return the current queue state in a compact view:

- ACTIVE section in full (all entries, with their next-action and source fields)
- Last 5 BACKLOG entries (newest first)
- Last 5 DONE entries

Maximum 25 lines of output. If all sections are empty, output:

```
Queue is empty. Say "add to queue: <thing>" to capture the first item.
```

### add

Append a new entry to the BACKLOG section with today's date:

```
[YYYY-MM-DD] <user's description> | next action: TBD | source: inbound
```

Confirm with one line: `Added to backlog: <short description>.`

If the user supplies a tag, next action, or source inline, use them. Otherwise use
`TBD` for next action and `inbound` for source.

### start

Move a BACKLOG entry to ACTIVE.

**Hard precondition: if ACTIVE already has 3 entries, the skill does NOT add a fourth.**

When the gate fires:

1. Return the three ACTIVE entries verbatim.
2. Ask: "ACTIVE is at capacity (3/3). Which of these gets paused (back to BACKLOG) or
   killed (removed entirely) before this one starts?"
3. Wait for the user to name one.
4. Apply the named transition (park or kill).
5. Then move the new item from BACKLOG to ACTIVE.

Update the entry's date to today when it enters ACTIVE.

### done

Move an ACTIVE entry to the DONE section with today's date prepended:

```
[YYYY-MM-DD] <original description> | closed
```

Confirm with one line: `Done: <short description>.`

### park

Move an ACTIVE entry back to BACKLOG. Update the entry's date to today.

Confirm with one line: `Parked: <short description>. Back in BACKLOG.`

## The 3-item rule is a feature, not a limit

ACTIVE matches actual human capacity for parallel work. The gate forces a decision that would otherwise drift.

## Where the queue surfaces elsewhere

- **SessionStart brief** - ACTIVE section only, printed first after the date header.
  If ACTIVE is empty, the brief prints: `Active: 0/3 (queue empty - say "add to queue:
  <thing>" to start)`.
- **`/founder-os:status`** - Queue bucket in the weighted readiness score (5% weight).
  Full credit if ACTIVE > 0 and DONE in last 7 days > 0. Half credit if only one.
  Zero if both empty.
- **`/founder-os:weekly-review`** - DONE rolloff and stuck-item review. Items in DONE
  older than 7 days are moved to `brain/log.md`. Items in ACTIVE older than 14 days
  surface for a keep/park decision.

## Rules

- Read-only unless explicitly called with add, start, done, or park.
- If `cadence/queue.md` is missing, create it from `templates/cadence/queue.md` first.
- If the user's request matches multiple operations (e.g. "add and start this now"),
  execute add first, then start (which will trigger the 3-item gate if needed).
