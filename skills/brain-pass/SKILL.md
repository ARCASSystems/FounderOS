---
name: brain-pass
description: >
  Semantic retrieval over the brain layer. Use when a question needs synthesis across log, knowledge, decisions, flags, patterns, and needs-input - not a raw text match. Run via `/founder-os:brain-pass "<question>"`. Other skills invoke this when they need brain context with reasoning, not text dumps. The model running this skill IS the retrieval engine: read the right files, reason across them, return a structured answer with citations. No embeddings, no API call, no paid tier required.
allowed-tools: ["Read", "Grep", "Glob"]
mcp_requirements: []
---

# Brain Pass

The brain pass is where the model's reasoning meets the user's stored memory. The user asks a question. You pick the relevant files, scan them, and return a synthesised answer with entry-ID citations - not a list of matches.

## When to use

- A question spans multiple brain files.
- A keyword query (`scripts/query.py`) returns too many matches to reason across.
- A skill needs prior context with citations, not raw text dumps.
- The user asks "what did I decide about X" or "what have I been avoiding" or "what do I know about Y".

## When NOT to use

- A specific entry ID is already known. Use `python scripts/query.py --mode full --ids <id>` instead.
- A simple keyword match is enough. Use `python scripts/query.py "<keyword>"` instead.
- The question is purely about the current state ("what is on today"). Use `/today` or `brain/.snapshot.md` instead.

## Instructions

You are doing a brain pass.

1. **Pick the relevant files.** The brain layer has structured channels:

   | File | What it holds |
   |---|---|
   | `brain/log.md` | What happened, who was met, what was said. Newest at top. |
   | `brain/decisions-parked.md` | Decisions waiting on a trigger condition. |
   | `context/decisions.md` | Active and resolved business decisions. |
   | `brain/knowledge/*.md` | Distilled lessons from books, calls, articles, experiments. |
   | `brain/flags.md` | Open friction or stall flags with severity. |
   | `brain/patterns.md` | Recurring observations the OS has noticed. |
   | `brain/needs-input.md` | Open questions waiting on the user. |
   | `cadence/weekly-commitments.md` | This week's must-do, should-do, waiting-on. |
   | `cadence/quarterly-sprints.md` | The 90-day arc and sprint targets. |

   Do not read every file. Pick the two-to-four most likely to contain the answer.

2. **Scan with intent.** Use `Read` for short files. Use `Grep` to locate concept matches in long files (`brain/log.md` in particular). Stop reading once you have enough to answer. Do not exhaustively load.

3. **Synthesise.** The output is your reasoning across the matches, not a paste of the matches. Cite stable entry IDs (`log-YYYY-MM-DD-NNN`, `flag-YYYY-MM-DD-NNN`, etc.) when they exist so the user can open the source.

4. **Output format.** This is the contract. Other skills depend on it.

   ```
   ## Brain pass: <question>

   **Answer.** <2 to 4 lines synthesising what the brain says about the question.>

   **Evidence.**
   - <entry-id>: <one-line summary> (path/to/file)
   - <entry-id>: <one-line summary> (path/to/file)
   - <entry-id>: <one-line summary> (path/to/file)

   **Confidence.** <high | medium | low> - <why>

   **Gaps.** <What the brain does not know that would change the answer.>
   ```

5. **If the brain has no relevant content, say so.** Output the block with `Answer.` set to "No prior brain content found on this question." and skip Evidence. Do not fabricate.

## Composition with other skills

When called from inside another skill (the calling skill provides the question), return only the structured block. The calling skill incorporates the answer into its own output.

## Privacy

Summarise. Do not paste raw entry bodies that contain personal or client-sensitive content. Cite the ID. Let the user open the source if they want detail.

## Why this works inside Claude Code (or any model surface)

The model running this skill IS the retrieval engine. The skill instructs it to read the right files, reason, and synthesise. There is no API call, no vector index, no paid tier. The free-tier accessibility floor is preserved. On Claude Code, Codex, or any other model surface that can read local files, this skill produces the same shape of output - performance varies, but the contract stays the same.

## What this is NOT

- Not embeddings. Vector search is parked until and unless this skill is proven slow or shallow.
- Not a daemon. The pass runs only when invoked.
- Not a substitute for `query.py` for known-ID lookups.
- Not auto-fired on every skill invocation. A skill consumes brain-pass only when its instructions explicitly call for it.

## Rules

- No em dashes or en dashes. Simple hyphens with spaces.
- No banned words (delve, robust, seamless, leverage, comprehensive, holistic, transformative, streamline, optimize, utilize, facilitate, unlock, navigate figurative, ecosystem figurative, landscape figurative, unpack, deep-dive).
- Read-only on the brain. Never edit a brain file as a side effect of a pass.
