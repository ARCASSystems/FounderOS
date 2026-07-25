---
why: "Long sessions lose work to a full context window - the build gets re-derived, a decision made at hour one is forgotten at hour four, and tokens go to reads that a cheap file already answered. This names where tokens go, what must never be spent on an LLM, and the running log that makes compaction survivable."
---

# Context discipline - tokens, determinism, and not losing a build to a full window

How a session spends its context so long builds finish and nothing gets re-derived. Read this before any multi-hour or multi-step build.

## Deterministic first (where tokens go, and where they must not)

- **Anything with one right answer gets code, not a prompt.** Counts, math, file writes, renders, registries, status changes. An LLM sitting in a deterministic seat costs money, varies between runs, and fails quietly. If you can write the rule down, write it as a script instead.
- **Anything needing judgment gets the model, plus a named verify step.** Drafts, reviews, a call between two options, deciding who someone is. The verify step is what makes a judgment output safe to act on.
- **Reads are slices, not whole files.** Grep before you read. Read the section, not the document. `brain/.snapshot.md` exists so a skill can warm up without reading the whole brain layer. The cheapest token is the one a small file already spent.
- **Match the model to the blast radius.** A cheap model for work that is cheap to get wrong. Your best model for architecture, money, anything irreversible, or anything ambiguous.
- **Do not spend tokens on a redo.** If doing it again by hand takes under five minutes, do it by hand.

## The running build log (the rule that saves the work)

Any session on a build that spans hours or several steps keeps a running log at `brain/handoffs/<date>-<build>-log.md`, updated **at each milestone**, never only at the end:

- what shipped (files, and the version marker if you save versions), what is mid-flight, what is next
- every decision you gave, close enough to your words to act on
- every non-obvious finding - a gotcha, a fact checked and confirmed, a dead end - so it is never worked out twice

**The 30% rule.** When roughly 30% of the context window is left, stop building for one minute: bring the log current, save it, then carry on. If the session compacts or you start a fresh one, work resumes from the log with nothing lost. The log is disposable once the build ships - fold the keepers into `brain/log.md` and delete the rest.

The matching rule: **never work out again what this session already established.** If a fact was checked this session, it is in the log. Read the log, not the source.

## Session-cost hygiene

- Long reference files get read by section. Grep the headings first - a heading map costs twenty lines and saves a five-hundred-line read.
- Independent reads go in one batch. Dependent ones go one at a time.
- Where your surface supports subagents, fan out the reading and keep the conclusion, not the file dumps.
- A session that is getting long and still has work left writes a handoff instead of pushing through on a nearly full window. See `skills/session-handoff`.

## Why this is a rule and not a preference

A full context window does not announce itself. It shows up as the OS repeating a question you already answered, re-reading a file it already read, or quietly dropping the constraint you gave it at the start. Every item above exists to keep the second half of a long session as sharp as the first.
