# Memory Index

This file is read by Claude Code at the start of every session. It is the cross-session continuity layer. Entries here are the small, durable things Claude should know about how you work and what is true right now.

The Founder OS files in `core/`, `context/`, and `cadence/` hold operating state. This file holds *behavioral memory* - corrections you have made, patterns Claude should not repeat, project facts that change between sessions but stay relevant for weeks.

Four sections. Load order: guards first, project context only when task touches it, review-due on explicit prompt only, never load expired.

---

## Behavioral Guards (permanent - load every session)

Things you have told Claude to start or stop doing. These do not decay. They live until the underlying behavior changes.

Format: one line per guard. Link to a detail file if the guard needs more context.

Examples (delete and replace once your first real guards land):

- *Lead with the answer, not the warm-up.* When I ask "what should I do", give one recommendation, not a menu. I value time over options.
- *Don't draft on my behalf without asking.* When I describe a tricky email or message, flag the issue and offer to draft. Don't write the message until I say go.
- *Numbers before recommendations.* If a decision touches money or time, run the math first. Don't skip to advice.

---

## Active Project Context (load if task touches the project)

Project-specific facts that are true right now. May change between sessions. Tagged with what a task must touch for the entry to be relevant.

Examples (delete and replace once you have real project context):

- *About: Client X. Scope locked at 6 weeks ending 2026-06-15. Final deliverable is a written diagnostic, not a deck. Load if: any Client X work.*
- *About: Q3 launch. Marketing handles content, ops handles platform integration. I write none of the copy. Load if: Q3 launch work.*

---

## Review Due / Dormant (do not auto-load - surface only on explicit review prompt)

Entries past their stated decay date but not yet triaged. They may still hold; they may have been silently overtaken. Surface when you run a memory review or when a current task contradicts what one of them says. After review, move to Active or to Expired.

*None yet. Entries whose decay date has passed move here for triage before final disposition.*

---

## Expired / Superseded (reference only - do not load)

*None yet. Entries that are confirmed stale or superseded move here. Kept as a record, not loaded into sessions.*
