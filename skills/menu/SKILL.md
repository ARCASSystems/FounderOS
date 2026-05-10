---
name: menu
description: >
  Show what FounderOS can do right now. Say "show me what you can do", "what can FounderOS do", "what should I try next", or "what's relevant right now" (or run /founder-os:menu). Returns 5 to 7 capability suggestions tailored to current state. Reads `brain/.snapshot.md`, open flags, this week's must-do, the last 7 days of `brain/log.md`, and the presence of `core/voice-profile.yml` and `core/brand-profile.yml`. Free-tier accessible - no LLM call inside the algorithm.
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# Menu

Discovery entry for FounderOS. Returns a small, ranked list of capabilities the founder is most likely to want right now, scored against current state. Natural-language phrasing is primary, slash commands appear parenthetically only for capabilities that have a real command file.

## How this skill runs

The menu engine is `scripts/menu.py`. The skill invokes the script and prints its output verbatim. The model does not score capabilities, does not invent rows, and does not paraphrase the engine's output.

```
python scripts/menu.py
```

The script:

- Reads state files only (`brain/.snapshot.md`, `brain/flags.md`, `cadence/weekly-commitments.md`, `brain/log.md`, `core/voice-profile.yml`, `core/brand-profile.yml`, `context/priorities.md`, `drafts/`).
- Scores capabilities against deterministic rules.
- Returns the top 5 to 7 by score, with a Day-1 starter set as zero-state fallback.
- Renders rows natural-language-first, with slash commands only for capabilities that have a real `.claude/commands/<name>.md` file. Skill-only capabilities (`weekly-review`, `priority-triage`, `pre-send-check`) render natural-language only and never invent a slash form.
- Closes with the verbatim line specified in `scripts/menu.py`.
- Stdlib only. No LLM call. No network call. Free-tier accessible.

## What the skill does

1. Locate the FounderOS install root (the working directory, or the repo root if the user is inside a sub-folder).
2. Run `python scripts/menu.py --root <root>` and capture stdout.
3. Print stdout verbatim. Do not summarize, do not paraphrase, do not add commentary.
4. If the script exits non-zero, surface the error to the user and stop.

## What the skill does not do

- Does not score capabilities itself. The script is authoritative.
- Does not invent slash commands. If the script omits a slash form, the model omits it too.
- Does not write to any file.
- Does not call an LLM. The scoring is deterministic, file-based, free-tier accessible.

## Constraints

- Output must end with the closing line from `scripts/menu.py` verbatim.
- Trigger phrases the operator already uses ("set up my voice profile", "set up my brand profile", "what should I focus on next", "what's on for today?", "audit the OS") appear in the script's rendered rows when the corresponding capability surfaces. The script handles this; the skill does not.
- If `scripts/menu.py` is missing on this install, surface that to the user and stop. Do not fall back to a model-side menu (that would re-introduce the v1.20.0 defect this skill was rewritten to fix).

## Tests

Behavioural tests live at `tests/test_menu.py`. They run the script against fixture roots (zero-state, populated, missing snapshot) and assert on stdout. The skill itself is verified by `SkillFileSurface` in the same test file: the SKILL.md must reference `scripts/menu.py` and must not delegate scoring to the model.
