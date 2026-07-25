---
name: os-evolve
description: Turn an audit, a pile of flags, or a vague sense that the OS is drifting into one dated plan with numbered execute prompts. Say "evolve the OS", "what should the OS fix about itself", "plan the next OS cycle", or run /founder-os:os-evolve. Scores the previous cycle first, then writes gaps with evidence, paste-ready prompts, and reconcile lines into a single plan file. It plans only - it never executes its own prompts, never edits rules, never touches your data files.
why: "Improvements to the OS itself get discovered in one session and forgotten by the next, so the same gap is rediscovered monthly and nothing compounds. This turns that loose motion into one dated file with evidence, numbered prompts, and a reconcile line per prompt, so an improvement either lands or is visibly still open."
enhance: "Run it after an audit, after two or three flags pile up, or when you notice the OS failing the same way twice. Roughly fortnightly is enough - it is a cycle, not a habit."
allowed-tools: ["Read", "Grep", "Glob", "Write"]
---

# OS evolve - the improvement cycle, written down

Runs on: local-writes - it writes one plan file into `plans/`. On a read-only surface I compose the plan and you save it yourself.

The motion this replaces: you notice three things wrong with your OS, fix one, and forget the other two until they resurface a month later. Every cycle starts from zero and nothing accumulates.

This skill does the loop properly. It plans. A later session (or you) executes. Reconciliation lands back in the same file, so a fix that never shipped stays visible instead of quietly disappearing.

## Step 1 - inputs (read by section, context discipline applies)

1. **The source:** `$ARGUMENTS` if you named a file, otherwise the newest audit or plan in `plans/`. Grep its headings first and read sections, not the whole file.
2. `brain/flags.md` - open flags. Each one is evidence of a gap.
3. `system/quarantine.md` - anything sitting ACTIVE is a failure that already happened.
4. **The previous cycle's plan.** Any prompt in it with no reconcile line is unfinished work, and it becomes gap number one of this cycle. This is the single most useful input and the one most easily skipped.
5. Where they exist: needs-work verdicts on any digital employee, and the kill notes on queue items you dropped. What you keep correcting names what keeps failing.

## Step 2 - score the last cycle first

One table before any new gap gets written. Each prompt from last time: shipped, partial, or dead, with the evidence or the reason.

An honest "dead, because we decided not to" is a valid outcome. Silence is not. A cycle that cannot say what happened to the last one is not a cycle, it is a fresh start wearing a plan's clothes.

## Step 3 - write ONE dated plan file (`plans/os-evolve-<date>.md`), and nothing else

Sections, in this order:

1. **Last cycle scored** - the table from step 2.
2. **Gap list** - numbered. Every gap cites its evidence: a flag, a quarantine entry, a line in the audit, an unreconciled prompt. **No gap without evidence.** A hunch goes in the kill column, not the list. This is the rule that keeps the plan from becoming a wish list.
3. **Execute prompts** - one per gap or cluster of gaps, numbered, paste-ready, and self-contained. Each names: the files to read, the gates that apply, the session rules (check the current state first, no attribution in saved versions, tests where code moves), and what evidence would prove it landed. Be directive. Name which one matters most and in what order. Never hand back a menu to choose from.
4. **Reconcile stubs** - one unchecked box per prompt: `[ ] P<n> - <what shipped> - <what observably moved>`. The executing session fills these in **in this same file**.
5. **Kill column** - what this cycle explicitly does not do, each with a one-line why. Naming what you are not doing is what makes the plan finishable.

## Step 4 - report

The path to the plan file, the gap count, the prompt count, the kill count, and the one prompt to run first. Nothing else. The plan is the output, not the summary.

## Rules

- **This skill never executes its own prompts.** The planner and the executor are different sessions on purpose: a session that plans and executes in one breath skips its own gates and marks its own homework.
- It never edits `CLAUDE.md`, anything in `rules/`, or any file in your User Layer. Those ride their own approved diffs.
- On demand only. This is not a routine and should never be scheduled.
- A new capability that a gap suggests goes through `forcing-questions` before it may enter a future cycle. The improvement cycle is not a door for new projects.
- Writing rules apply. No em dashes. No banned words.
