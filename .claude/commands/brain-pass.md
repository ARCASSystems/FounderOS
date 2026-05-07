---
description: Synthesise a focused answer across the brain layer with citations. Use when a question spans multiple brain files and a keyword query is too noisy.
argument-hint: "<question>"
allowed-tools: ["Read", "Grep", "Glob"]
---

# Founder OS brain pass

Run the brain-pass skill at `skills/brain-pass/SKILL.md` end to end.

## Procedure

1. If `$ARGUMENTS` is empty, reply `What should the brain pass over? Re-run as /founder-os:brain-pass "<question>".` and stop.
2. If `core/identity.md` does not exist, reply `Founder OS not set up here. Run /founder-os:setup first.` and stop.
3. If `skills/brain-pass/SKILL.md` is missing, reply `brain-pass skill not found at skills/brain-pass/SKILL.md. Re-install the plugin.` and stop.
4. Follow the brain-pass skill instructions exactly. The question for the pass is `$ARGUMENTS`.
5. Output the structured block defined in the skill (Answer / Evidence / Confidence / Gaps).

## When to use

- A question spans multiple brain files and you want one synthesised answer with citations.
- A keyword query (`/founder-os:query`) returned too many matches to reason across.
- You want context with reasoning, not raw text dumps.

## When NOT to use

- A specific entry ID is known. Use `/founder-os:query --mode full --ids <id>`.
- A simple keyword match is enough. Use `/founder-os:query <keyword>`.

## Examples

- `/founder-os:brain-pass "what did I decide about pricing tiers?"`
- `/founder-os:brain-pass "what blocks the launch?"`
- `/founder-os:brain-pass "what have I been avoiding for three weeks?"`

## Rules

- Read-only.
- No external dependencies.
- No em dashes or en dashes.
- No banned words.
- Cite entry IDs where they exist. Summarise, do not paste raw bodies.
