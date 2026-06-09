---
name: tune
description: >
  Tune your voice handlers to how you actually talk. Trigger on "tune", "tune my voice",
  "tune the handlers", "what should I pre-program", or "make the voice faster". It reads the
  local voice runtime telemetry the add-voice skills already write (which routes you use, how
  slow each was, and - on the realtime tier - what you tend to ask), and PROPOSES the next
  fast handler to pre-program so a request you make often is answered instantly instead of
  going through the slow reasoning path. It is propose-only: it never edits a handler or
  changes a config. You decide what to add. Free-tier and fully local - it reads gitignored
  files on your machine and synthesises in-session, with no external call and no key.
why: "A voice OS gets faster the more it is shaped to one person's habits. The private design tuned handlers to how the operator actually spoke; this is the public, propose-only port. Reading the telemetry the voice skills already log and surfacing the one handler worth pre-programming next turns a generic voice loop into one fitted to this user, without ever editing behind their back."
summary: "Reads your voice telemetry and proposes the next fast handler. Propose-only."
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# Tune

Runs on: local-exec - it runs a local Python script that reads the gitignored voice telemetry. On a read-only or cloud surface, explain what it would surface but do NOT claim it ran or invent telemetry - there is none until the user runs the voice loop locally.

This is the tuning half of the voice scaffold. The `add-voice` skills log every turn locally (which route, how slow, and on the realtime tier what you said). Over time that telemetry shows what you ask for often. `tune` reads it and proposes the next **fast handler** to pre-program - an instant answer for a request you keep making - so the voice loop gets fitted to how you actually operate.

It changes nothing. It reads and proposes. You decide what to add.

## What a fast handler is

The voice loop has two speeds. Most turns go through the reasoning brain (a second or two). A few common requests - "what's on today", "what changed", "save this" - are wired as instant handlers that answer without waiting on the brain. `tune` finds the request you make often that is NOT yet an instant handler and proposes wiring one, so it stops being slow.

## The accessibility floor

`tune` is pure local file reading plus in-session synthesis. No key, no paid service, no external call. It works on the free floor.

## Pre-flight

- It needs telemetry to read. If you have not run the voice loop yet, there is nothing to tune; say so plainly and point at `add-voice`. Do not invent usage.
- The telemetry lives in the gitignored `voice/` folder (`runtime-log.jsonl` from Tier 0, `live-telemetry.jsonl` from the realtime tier). `tune` reads whatever is present.

## The flow

### 1. Run the read

```
python skills/tune/tune.py
```

It reads `voice/runtime-log.jsonl` and `voice/live-telemetry.jsonl` if present, aggregates your turns (route frequency, latency, and - realtime only - the words you tend to use), and prints a short report: how much it read, which turns were slow, and the recurring requests that are not yet instant handlers.

Pass `--days <n>` to look only at recent turns, or `--top <n>` to change how many candidates it lists.

### 2. Read the proposal back to the user

The report ends with a propose-only list: the one or two handlers worth pre-programming next, each with why (you ask it often, it was slow). Read these back as suggestions. Do NOT wire anything. If the user wants one, that is a separate, deliberate edit they confirm - `tune` only points.

## What it does and does not do

- **Does:** read the local voice telemetry, aggregate your real usage, surface slow turns, and propose the next fast handler to pre-program, with the reason. Free, local, no key.
- **Does not:** edit a handler, change a config, send telemetry anywhere, or invent usage when there is none. It is read-and-propose, never act.

## The guardrails this skill is built against

1. **Silent self-editing.** `tune` proposes; it never wires a handler on its own. Tuning the OS to you stays your decision, with a human gate, exactly like the recursive skill-update prompt elsewhere in the OS.
2. **Inventing a pattern from thin data.** If there are too few turns to say anything honest, it says so rather than manufacturing a recommendation.
3. **Leaking what you said.** The telemetry is local and gitignored; `tune` reads it in place and never writes it anywhere tracked or external.

## Runtime honesty

This skill needs a local runtime to read the telemetry files. On a web-only agent, do not claim it ran or report numbers. Explain what it would surface and say it has to run in Claude Code (or any local-runtime agent pointed at the folder).

No em dashes or en dashes in anything you write here. Hyphens only.
