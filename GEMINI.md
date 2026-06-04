# FounderOS - Gemini CLI Context

Context loader for Gemini CLI and other non-Claude agents operating in this repo.

This file is a thin bridge, not a separate rulebook. The canonical instruction file is `CLAUDE.md` - the full cross-agent reference (repo map, roles, slash commands, substrate, hooks, what-not-to-do) lives there. `AGENTS.md` is a peer bridge that carries the same cross-agent deltas for Codex-style agents. Read `CLAUDE.md` at session start.

---

## Read first

1. `CLAUDE.md` - the source of truth for how this OS behaves, and the full cross-agent reference (repo map, roles, skills, commands, hooks, substrate).
2. `AGENTS.md` - a peer bridge listing the same cross-agent deltas (slash commands not executable, skills as procedural reference, do not claim hooks ran).
3. `README.md` - the product picture and setup path.

Do not duplicate or override those files here. If anything in this file ever disagrees with `CLAUDE.md`, `CLAUDE.md` wins.

---

## Gemini-specific operating notes

- The slash commands in `.claude/commands/` are Claude Code specific. You cannot run them. Treat them as documented procedures, not executable actions.
- If you cannot run slash commands, hooks, or MCP tools, treat this repo as a system layer only. Do NOT claim that setup, hooks, file writes, MCP authentication, or scheduled routines have run. Say plainly what you can and cannot do in this environment.
- Skills in `skills/<name>/SKILL.md` are readable as procedural reference. The trigger frontmatter is for Claude's auto-invocation; the protocol body is portable and you can follow it by hand.
- Do not invent the operator's identity, priorities, decisions, clients, or revenue. If the six context files named in `CLAUDE.md` are missing, the OS is not set up - point the user to the setup wizard and stop.
- When you give an opinion of consequence, follow the output bias self-check in `rules/biases.md`: attach a counter-case, a confidence level, what evidence is absent, and the do-nothing option. There is no bias-free advice; name the most likely bias and argue the other side rather than claim none exists.

---

## Writing and commits

- No em dashes, no en dashes. Simple hyphens with spaces.
- No banned words (delve, robust, seamless, leverage as a verb, comprehensive, governance, diagnostics, and the rest listed in `rules/writing-style.md`).
- Commit messages follow `rules/commit-naming.md`: plain-language subject, no version-only subjects, no AI attribution trailers.

---

## Built by

[ARCAS Systems](https://arcassystems.com).
