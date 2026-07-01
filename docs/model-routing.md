# Model routing

Founder OS is model-agnostic. It runs on whatever Claude model your Claude Code session is set to, and it is not pinned to any one of them - newer models are always fine. You never have to touch this. This page is for when you want to match the model to the task.

## Switch models in Claude Code

Type `/model` in Claude Code and pick from the list. The choice applies to the current session. There is nothing to configure in the OS itself.

## Which Claude for which job

Match the model to the cost of being wrong, not to how hard the task feels.

| Model | Reach for it when | Examples in the OS |
|-------|-------------------|--------------------|
| **Opus** (top tier) | Being wrong is expensive: strategy, positioning, a proposal that lands a client, a decision you cannot easily walk back, or an ambiguous ask where the path is not obvious. | `strategic-analysis`, `decision-framework`, `proposal-writer`, `founder-scope-challenge`, the setup wizard |
| **Sonnet** (balanced) | Most day-to-day work. Well-scoped and higher-volume: drafting a post, a client update, a follow-up email, triaging the week. Near-Opus quality, faster and lighter. | `linkedin-post`, `client-update`, `email-drafter`, `content-repurposer`, `weekly-review` |
| **Haiku** (fast) | Cheap, mechanical, speed-first work with a clear answer: a quick classification, a short summary, a one-line lookup. | quick captures, short brain-log entries, simple reformatting |

Default rule of thumb: **stay on Sonnet for daily driving, switch up to Opus when the buck stops with you on the output, drop to Haiku for throwaway mechanical steps.** When unsure, go one tier up - a bad proposal costs far more than the extra tokens.

Anthropic also ships a most-capable tier above Opus for the hardest long-horizon, multi-hour agentic work. You will rarely need it for founder-OS tasks; reach for it only when Opus visibly struggles on something genuinely hard.

## Effort and speed (optional)

On the current Opus and Sonnet models, Claude Code exposes two dials worth knowing:

- **Effort** - how hard the model works before answering. Higher effort helps on coding, multi-step agentic work, and anything where correctness matters more than speed. For most OS writing and thinking tasks the default is fine.
- **Fast mode** (`/fast`, Opus) - same model, faster output, for when you want Opus judgment without the wait. It does not downgrade to a smaller model.

Neither is required. The OS works the same with them off.

## The free-tier floor still holds

None of this changes the promise that the OS runs on one Claude plan with no extra key. Model choice is a preference, not a paywall. Every skill works on whatever model you have; picking a bigger one just buys more headroom on the hard tasks.

## Where a second provider fits (voice only)

The one place the OS uses a non-Claude model is the **optional realtime voice tier**. Talking to the OS out loud in real time (Tier 1 of `add-voice`) uses a Google Gemini Flash model for the live speech front, wired with a **free** Google AI Studio key you paste in during `connect`. This is the mouth and ears for realtime voice, not the brain - your reasoning still runs on Claude. The default voice tier needs no key at all (your browser's built-in speech), and text mode never touches Gemini. See `skills/add-voice/references/tiers.md`.

## Other agents (Codex, Gemini CLI, Cursor)

The OS is plain markdown, so other agents can read it. `AGENTS.md` (Codex, Cursor, Windsurf) and `GEMINI.md` (Gemini CLI) are thin bridges that point those agents at `CLAUDE.md`. They can read your OS, reason over it, and draft - but the setup wizard, slash commands, and hooks are Claude Code features and will not run there. Treat non-Claude agents as a reading-and-drafting layer, not a replacement for running the OS in Claude Code.
