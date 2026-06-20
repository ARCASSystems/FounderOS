---
name: routines
description: >
  Discover, trigger, and understand your routines in plain English. Trigger on "what are my routines", "what runs automatically", "run my morning brief", "run my weekly review", "what should I change this month", "turn on the weekly review", or "how does the heartbeat work". Founder OS checks in when you open it (the SessionStart brief) and runs any routine on demand when you ask, all local with no account. Truly unattended while-you-sleep runs are an opt-in upgrade for users who have synced their OS to a remote, and the skill never claims a routine ran where it did not.
why: "An OS that only acts when typed at feels dead. Routines make it check in. But the honest model is hybrid: local on-open and on-demand for everyone, unattended only once you sync to a remote. Pretending a laptop can run unattended cron would be the dishonest shortcut, so this skill states the mechanism for each routine plainly."
enhance: "Open the OS even occasionally and the on-open brief gives you a real heartbeat. Want one to run while you sleep? Sync your OS to a remote (the backup skill is the first step) and turn on the remote routine."
allowed-tools: ["Bash", "Read", "Skill"]
mcp_requirements: []
---

# Routines

Runs on: reasoning - reads what routines exist and routes you to the one you asked for; the routines themselves run on their own mechanisms (below).

The heartbeat layer. Founder OS does not sit unused: it checks in when you open it and runs any routine the moment you ask. This skill is how you find, trigger, and understand them in plain English.

## Pre-flight

- If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`

## The heartbeat, honestly (hybrid)

There are two levels, and the difference is the whole point:

- **Free local floor (default, no account).** Routines fire when you OPEN the OS (the SessionStart brief already does this) and ON DEMAND when you ask or run `/loop`. This is a real heartbeat for anyone who opens the OS even occasionally. It is fully local and truthful.
- **Unattended upgrade (opt-in).** If you have synced your OS to a remote (start with the `backup` skill, then a remote routine on claude.ai), genuine while-you-sleep runs operate on the synced copy. This is the next level, never required, and only works because the remote can reach the synced files.

We never promise unattended local cron, and never claim a routine ran where it did not.

## The routines

| Routine | What it does | How it runs |
|---|---|---|
| Daily brief | Flags, stale cadence, decisions, quarantine, decay, connectors not set up | On-open (the SessionStart brief, automatic) + on-demand: say "run my brief" or `/founder-os:today` |
| Weekly review | Rolls the sprint, forces a verdict on every open flag | On-demand or on-open when a week has passed: say "run my weekly review" |
| Monthly flagship | The three changes worth making now, each with a dated source | On-demand: say "what should I change" (the `what-to-change` skill). Freshness nag in the brief when a month has passed since the last run |

To run any routine now, just say its name in plain English, or use the slash command in the table. To run one repeatedly in a session, wrap it with `/loop` (for example `/loop weekly run my weekly review`).

## Turning routines on

A fresh install does NOT have unattended routines running on its own - that would be a false claim. What it has:

- The on-open daily brief, active out of the box (it fires every time you open the OS).
- Every routine runnable on demand with one plain-English ask.
- An opt-in path to unattended runs once you sync (the upgrade above).

So the honest statement is: you can turn on any routine with one ask, and you can add unattended runs once your OS is synced.

## Scheduling glossary (so the terms do not blur)

Four different things get called "scheduling". They are not the same:

- **Native `CronCreate`** - in-session only. Fires while the Claude Code REPL is idle, and a recurring job auto-expires after 7 days. Good for a short in-session cadence, not a reliable weekly or monthly cron.
- **`RemoteTrigger` (claude.ai routines)** - runs on claude.ai infrastructure. It cannot read your laptop, so it only helps once your OS is synced to a remote it can reach. This is the unattended upgrade.
- **Cowork `/schedule`** - Anthropic's desktop surface can run timed jobs, but hooks and the `/founder-os:*` namespace do not fire there. Use it for drafting and timed runs, keep Claude Code as the OS layer.
- The old external task-runner MCP is no longer a dependency. Founder OS uses the native on-open / on-demand floor and the optional remote upgrade instead, so there is nothing extra to install.

## Runtime honesty

On a web-only surface, the on-open brief and any local-script routine cannot run; say so and offer the on-demand version you can do in-session (reading files and reasoning). Never report that a routine ran on a surface that cannot run it.

## Rules

- State each routine's real mechanism. Never imply unattended local cron exists.
- Never claim a routine ran where it did not.
- No em dashes or en dashes in anything you write. Hyphens only.
