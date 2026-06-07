# FounderOS - Agent Instructions

A thin bridge for Codex, Cursor, Windsurf, Gemini, and other non-Claude agents operating in this repo.

The canonical instruction file is `CLAUDE.md`. It is the source of truth for how this OS behaves: what the repo is, the repo map, the six role modes (four active, two reference-until-invoked), the full skill and command lists, the brain substrate, the hooks, the wiki conventions, and what not to do. Read it in full. This file only carries the deltas a non-Claude agent needs on top of it. If anything here ever disagrees with `CLAUDE.md`, `CLAUDE.md` wins.

---

## Read first

1. `CLAUDE.md` - the source of truth for behaviour, structure, roles, skills, commands, hooks, and substrate.
2. `README.md` - the product picture and the setup path.

The skill registry is `skills/index.md` (70 skills, 35 commands); the long-form per-skill reference is `docs/skills.md`. Read those for the lists rather than expecting them duplicated here.

---

## Cross-agent deltas (what differs from a Claude Code session)

- **Slash commands are Claude Code specific.** The 34 commands in `.claude/commands/` cannot be run by a non-Claude agent. Treat them as documented procedures, not executable actions.
- **Skills are procedural reference.** Each `skills/<name>/SKILL.md` has trigger frontmatter for Claude's auto-invocation (ignore that) and a protocol body that is portable. Follow the body by hand.
- **You cannot run hooks, MCP tools, slash commands, or local writes unless your environment actually supports them.** Do not claim that setup, hooks, file writes, MCP authentication, or scheduled routines have run. Say plainly what you can and cannot do in this environment.
- **Runtime honesty and the per-skill `Runs on:` contract:** every skill declares its runtime class (`reasoning`, `local-writes`, or `local-exec`) on a `Runs on:` line in its `SKILL.md`. The full contract and the honest-degradation rule live in `CLAUDE.md`. Read it there. If your environment can write to the folder you may run a `local-writes` skill; if it cannot run a script you read the produced artifacts for a `local-exec` skill and say so. If anything here disagrees, `CLAUDE.md` wins.
- **Opinions of consequence:** Claude has `/founder-os:devil` to run the output bias self-check. You do not. Follow `rules/biases.md` by hand - attach the strongest counter-case, a confidence level (high / medium / low), what evidence is absent, and the do-nothing option. Name the most likely bias and argue the other side; do not claim bias-free advice.
- **Do not modify the operator's data files** (`core/`, `context/`, `cadence/`, `brain/`) without explicit instruction. Claude has approval-gates and hooks guarding this; you do not, so the burden is on you to ask first.
- **Empty state:** if the six context files named in `CLAUDE.md` are missing, the OS is not set up. Do not invent identity, priorities, decisions, clients, or revenue. Point the user to the setup wizard and stop.

---

## Writing and commits

- No em dashes, no en dashes. Simple hyphens with spaces around them. No banned words (the list is in `rules/writing-style.md`).
- Commit messages follow `rules/commit-naming.md`: a plain-language subject stating the user-visible change, no version-only subjects, no AI attribution trailers.

---

## Built by

[ARCAS Systems](https://arcassystems.com).
