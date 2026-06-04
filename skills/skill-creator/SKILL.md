---
name: skill-creator
description: >
  Create new skills, modify and improve existing skills, and measure skill performance. Use when the user wants to create a skill from scratch, edit or improve an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or tune a skill's description for better triggering accuracy. Triggers on "create a skill", "make a skill for", "turn this into a skill", "improve this skill", "why isn't my skill triggering", "test this skill", or "tune the description".
why: "A skill that never triggers, or triggers on the wrong prompts, is dead weight - this makes the description, the only thing the model sees before loading a skill, something you test rather than guess at."
enhance: "Run the description length check at every edit, not just at creation - a tuning pass that scores well on triggering can quietly push the description past the install ceiling and the skill silently stops loading."
summary: "Create, improve, and measure skills - and tune why they trigger."
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
mcp_requirements: []
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run a copy of the model that has access to the skill on them
- Help the user evaluate the results both qualitatively and quantitatively
- Rewrite the skill based on the user's evaluation of the results (and any glaring flaws the quantitative benchmarks surface)
- Repeat until you are satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress. They might say "I want to make a skill for X" - then you help narrow down what they mean, write a draft, write the test cases, run them, and iterate. Or they might already have a draft - then you go straight to the eval and iterate part of the loop.

Be flexible. If the user says "I do not need a bunch of evaluations, just vibe with me", do that instead.

After the skill is done, you can also run a description-tuning pass to improve how reliably the skill triggers.

This file is the router. The full procedure for each heavy step lives in a `references/` file. **Load the reference for the step you are on, when you reach it - not all at once.**

| Step | Load |
|------|------|
| Write the SKILL.md (frontmatter, anatomy, progressive disclosure, writing patterns, writing style) | `references/writing-guide.md` |
| Test cases + running and evaluating runs (the eval loop, steps 1-5) | `references/evals.md` |
| Improving the skill from feedback + the iteration loop | `references/improving.md` |
| Description tuning for triggering accuracy | `references/description-tuning.md` |

## Description length - HARD CHECK (mandatory)

Some skill loaders silently fail to install a skill whose `description:` value runs over roughly **1,024 characters**. The failure surfaces no error - the skill installs, never triggers, and the user only notices weeks later when a use case that should have invoked it goes unhandled. Loud failure is preferable to silent install.

**Run this check at every point a description is written or modified:**

1. Initial draft (when first writing the SKILL.md frontmatter)
2. After applying a tuned `best_description` from the description-tuning step
3. Any later edit to the `description:` field

**Procedure:**

- Count the characters of the `description:` value (the string after the key, including a folded `>` block's joined text).
- If **over 1024**: STOP. Do not write or install. Report the actual length and the overflow. Propose a trimmed version that preserves the trigger phrases.
- If **over 900 and at or under 1024**: WARN. The description is in the danger zone. Likely fine but at risk if a future edit adds words. Suggest a trim.
- If **at or under 900**: PASS. Proceed.

This check is non-negotiable.

## Communicating with the user

This skill gets used by people across a wide range of familiarity with technical jargon. Pay attention to context cues to understand how to phrase your communication.

- "evaluation" and "benchmark" are borderline but usually fine
- for "JSON" and "assertion" wait for clear cues that the user knows those terms before using them without explaining

It is fine to briefly explain a term if you are in doubt. A short definition costs one line.

---

## Creating a skill

### Capture intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (for example, they say "turn this into a skill"). If so, extract answers from the conversation history first - the tools used, the sequence of steps, corrections the user made, input and output formats observed. Have the user fill the gaps and confirm before moving on.

1. What should this skill enable the model to do?
2. When should this skill trigger? (which user phrases and contexts)
3. What is the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, design) often do not. Suggest the right default based on the skill type, but let the user decide.

### Interview and research

Ask about edge cases, input and output formats, example files, success criteria, and dependencies. Wait to write test prompts until this is ironed out.

Check available tools and MCPs. If any are useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents where available, otherwise inline. Come prepared so you reduce the burden on the user.

### Write the SKILL.md

Now read `references/writing-guide.md` for the full SKILL.md authoring guide: the frontmatter components, the anatomy of a skill, progressive disclosure, the principle of no surprise, the writing patterns, and the writing style.

### Test and evaluate

When the draft is ready, read `references/evals.md` for the full procedure: writing test cases to `evals/evals.json`, spawning with-skill and baseline runs, drafting assertions, capturing timing, grading, aggregating into a benchmark, and reading the feedback.

---

## Improving the skill

After the runs and the user's review, read `references/improving.md` for how to think about improvements (generalize, keep lean, explain the why, bundle repeated work) and the iteration loop.

---

## Description tuning

After creating or improving a skill, offer to tune the description for better triggering accuracy. Read `references/description-tuning.md` for the full tuning loop: generating trigger eval queries, reviewing with the user, running the tuning loop, how triggering works, applying the winner, and the mandatory length check.

---

## Updating an existing skill

The user might be asking you to update an existing skill, not create a new one. In that case:

- **Preserve the original name.** Keep the skill's directory name and `name` frontmatter field unchanged.
- **Copy to a writeable location before editing** if the installed path is read-only. Edit the copy, then move it back.
- **Re-run the length check** on the modified description before considering it done.

---

## Output rules

- No em dashes or en dashes. Hyphens only, with spaces around them.
- No banned words (delve, robust, seamless, leverage, comprehensive, holistic, transformative, streamline, optimize, utilize, facilitate, unlock, navigate, ecosystem, landscape).
- When you finish a skill, summarize what it does, where it lives, and how to test it.

---

Repeating the core loop for emphasis:

- Figure out what the skill is about
- Draft or edit the skill
- Run a copy of the model that has access to the skill on test prompts
- With the user, evaluate the outputs both qualitatively and quantitatively
- Repeat until you and the user are satisfied
- Run the length check before declaring the skill done
