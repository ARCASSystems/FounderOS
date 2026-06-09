# Decisions Pack

A logical pack, not a folder. Claude Code discovers skills as top-level directories under `skills/`, so the pack is held together by convention and by the links in this manifest rather than by nesting. The members do not share a name prefix; this manifest reads them as one connected unit.

This is the chief-of-staff function for a founder who runs alone. It covers the path from stuck to clear: a decision weighed, a list cut to one, a new idea gated, or the whole picture read back to you.

## The front door

[decisions-start](decisions-start/SKILL.md) is the entry. Say "help me decide", "cut my list to one", or "I'm stuck". It reads your own files to see which kind of stuck you are in, gives one honest disclaimer, and routes you to the move that clears it. You do not name the skill; you name the block, and it aims the right tool at it.

## What the pack is

You are blocked: on a choice, on a list, on a shiny idea, or on a fog where you have lost the thread. The pack reads your own state and gives you the thinking partner a solo founder does not have. It structures the decision and gives you the counter-case; it never makes the call for you. Everything runs locally and free, as reasoning over files you already hold. Nothing is sent.

## The outcomes and the skills behind them

| Outcome | Skill | Status |
| --- | --- | --- |
| Front door (which kind of stuck) | [decisions-start](decisions-start/SKILL.md) | Ready |
| Weigh a real choice | [decision-framework](decision-framework/SKILL.md) | Ready |
| Gate a new initiative before it starts | [forcing-questions](forcing-questions/SKILL.md) | Ready |
| Cut an overloaded list to one thing | [priority-triage](priority-triage/SKILL.md) | Ready |
| See what is actually on your plate | [queue](queue/SKILL.md) | Ready |
| Read the state of the whole OS | [strategic-read](strategic-read/SKILL.md) | Ready |
| Size a market or a competitor | [strategic-analysis](strategic-analysis/SKILL.md) | Ready |
| Run the weekly retro and reset | [weekly-review](weekly-review/SKILL.md) | Ready |

## The shared discipline

The pack's shared discipline is bias honesty. When the OS leans toward an option it says so, attaches the counter-case and a confidence level, names what evidence is missing, and flags when it is agreeing mainly because it is your plan. It never claims a bias-free answer, because none exists. This is what keeps the decisions yours and honest rather than rubber-stamped.

## Honest about the limits

The OS reads what you have written down and structures the call; it cannot see what is only in your head, it does not know your risk appetite or what you can live with, and it will not make an irreversible decision for you. It clears the block; the decision is yours. Its strength is structured thinking over your real state, with the counter-case always attached.

## Dependencies between members

- The decision skills read `context/priorities.md`, `brain/flags.md`, `context/decisions.md`, and `cadence/weekly-commitments.md`; the more honest those are, the sharper the call. The front door reads them first to name the block.
- `forcing-questions` and `weekly-review` write back (a parked decision, a re-cut priority list, a rolled sprint); the front door reports what changed.
- `strategic-read` is read-only and is the safe first move when the block is a general fog rather than a named choice.
