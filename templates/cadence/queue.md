---
file: cadence/queue.md
purpose: The work in motion right now. Three lifecycle states. ACTIVE is capped at 3.
populated_by: [setup wizard (creates from template), queue skill (state transitions), weekly-review (rolloff)]
load_on_demand: false  # SessionStart brief reads ACTIVE section
---

# Queue

> What is moving. Read at every session start. ACTIVE is hard-capped at 3 items.

## Conventions

Every entry has the shape:

`[YYYY-MM-DD] [TAG] short description | next action | source`

- `YYYY-MM-DD` = date the item entered this state
- `[TAG]` = optional, e.g. `[client:acme]`, `[content]`, `[ops]`
- `next action` = the single next concrete step
- `source` = where the item came from (`rant`, `meeting`, `weekly-review`, `inbound`)

## ACTIVE (max 3)

Items currently in motion. The cap is non-negotiable. If a fourth thing wants to start, one of these moves to BACKLOG or gets killed.

(none yet)

## BACKLOG

Captured but not started. No cap. Newest at the top.

(none yet)

## DONE (last 7 days)

Closed in the rolling 7-day window. Older items roll into `brain/log.md` automatically by the weekly-review skill.

(none yet)
