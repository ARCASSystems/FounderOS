---
name: skill-creator
description: >
  Create new skills, modify and improve existing skills, and measure skill performance. Use when the user wants to create a skill from scratch, edit or improve an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or tune a skill's description for better triggering accuracy. Triggers on "create a skill", "make a skill for", "turn this into a skill", "improve this skill", "why isn't my skill triggering", "test this skill", or "tune the description".
why: "A skill that never triggers, or triggers on the wrong prompts, is dead weight - this skill makes the description (the only thing the model sees before loading a skill) something you test rather than guess at."
enhance: "Run the description length check at every edit, not just at creation - a tuning pass that scores well on triggering can quietly push the description past the install ceiling and the skill silently stops loading."
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

Based on the interview, fill in these components:

- **name**: skill identifier (matches the folder name)
- **description**: when to trigger and what it does. This is the primary triggering mechanism. Include both what the skill does AND the specific contexts for when to use it. All "when to use" information goes here, not in the body. Models tend to undertrigger skills - to not use them when they would help. To counter that, make descriptions a little pushy. Instead of "How to build a fast dashboard to display data", write "How to build a fast dashboard to display data. Use this whenever the user mentions dashboards, data visualization, metrics, or wants to display any kind of data, even if they do not explicitly ask for a dashboard."
- **the rest of the skill body**

This Founder OS repo (B) uses a folded `description: >` block plus optional `why`, `enhance`, `allowed-tools`, and `mcp_requirements` keys. Match the existing skills in `skills/` so the new skill loads the same way. Commands the skill references are namespaced `/founder-os:<name>`.

### Skill writing guide

#### Anatomy of a skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled resources (optional)
    ├── scripts/    - executable code for deterministic or repetitive tasks
    ├── references/ - docs loaded into context as needed
    └── assets/     - files used in output (templates, icons, fonts)
```

#### Progressive disclosure

Skills load in three levels:

1. **Metadata** (name + description) - always in context (~100 words)
2. **SKILL.md body** - in context whenever the skill triggers (under 500 lines ideal)
3. **Bundled resources** - as needed (scripts can execute without loading into context)

These counts are approximate. Go longer if you genuinely need to.

**Key patterns:**

- Keep SKILL.md under 500 lines. If you approach that limit, add a layer of hierarchy with clear pointers about which reference file to read next.
- Reference files clearly from SKILL.md with guidance on when to read them.
- For large reference files (over 300 lines), include a table of contents.

**Domain organization**: when a skill supports multiple domains or frameworks, organize by variant so the model reads only the relevant reference file:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

#### Principle of no surprise

Skills must not contain malware, exploit code, or anything that could compromise system security. A skill's contents should not surprise the user relative to its stated intent. Do not go along with requests to create misleading skills or skills designed to enable unauthorized access, data exfiltration, or other malicious activity. A "roleplay as an X" skill is fine.

#### Writing patterns

Prefer the imperative form in instructions.

**Defining output formats:**

```markdown
## Report structure
Always use this exact template:
# [Title]
## Summary
## Key findings
## Recommendations
```

**Examples pattern:**

```markdown
## Commit message format
Example 1:
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing style

Explain to the model why things matter rather than relying on heavy-handed MUSTs. Use theory of mind. Keep the skill general, not narrow to specific examples. Write a draft, then read it again with fresh eyes and improve it.

### Test cases

After writing the draft, come up with 2 to 3 realistic test prompts - the kind of thing a real user would actually say. Share them with the user: "Here are a few test cases I would like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json`. Do not write assertions yet - just the prompts. You will draft assertions while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of the expected result",
      "files": []
    }
  ]
}
```

## Running and evaluating test cases

This section is one continuous sequence. Do not stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, and so on) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, and so on). Create directories as you go, not all upfront.

### Step 1: spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn - one with the skill, one without. Launch everything at once so it all finishes around the same time. Do not run the with-skill runs first and come back for baselines later.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about - e.g. "the final CSV">
```

**Baseline run** (same prompt, baseline depends on context):

- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (copy the skill folder to `<workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case (assertions can be empty for now). Give each eval a descriptive name based on what it tests, not just "eval-0". Use that name for the directory too.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: while runs are in progress, draft assertions

Use this time productively. Draft quantitative assertions for each test case and explain them to the user. Good assertions are objectively verifiable and have descriptive names so they read clearly in a results viewer. Subjective skills (writing style, design quality) are better evaluated qualitatively - do not force assertions onto things that need human judgment. Update the metadata files once drafted.

### Step 3: as runs complete, capture timing data

When each subagent task completes, you receive a notification with `total_tokens` and `duration_ms`. Save it immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only chance to capture this data. Process each notification as it arrives rather than batching.

### Step 4: grade, aggregate, and review

Once all runs are done:

1. **Grade each run** - read the outputs and evaluate each assertion. Save results to `grading.json` in each run directory. For assertions that can be checked programmatically, write and run a script rather than eyeballing it.
2. **Aggregate into a benchmark** - produce a `benchmark.json` and a readable `benchmark.md` with pass_rate, time, and tokens for each configuration, mean and standard deviation, and the delta. Put each with-skill version before its baseline counterpart.
3. **Do an analyst pass** - read the benchmark and surface patterns the aggregate stats hide: assertions that always pass regardless of the skill (non-discriminating), high-variance evals (possibly flaky), and time and token tradeoffs.
4. **Show the user the results** - present each test case's prompt and output for review, plus the benchmark summary. If a tool is available to render a review viewer, use it; otherwise present the results inline in the conversation.

### Step 5: read the feedback

When the user is done reviewing, gather their per-test-case feedback. Empty feedback means the user thought it was fine. Focus improvements on the test cases where the user had specific complaints.

---

## Improving the skill

This is the heart of the loop. You have run the test cases, the user has reviewed the results, and now you make the skill better.

### How to think about improvements

1. **Generalize from the feedback.** You are trying to build a skill that works across many different prompts, not just the handful you are iterating on. Avoid fiddly, overfit changes and oppressively constrictive MUSTs. If an issue is stubborn, try a different metaphor or a different pattern of working. It is cheap to try.
2. **Keep the prompt lean.** Remove things that are not pulling their weight. Read the transcripts, not just the final outputs. If the skill is making the model waste time on unproductive steps, cut the parts causing that and see what happens.
3. **Explain the why.** Explain the reasoning behind everything you ask the model to do. Modern models have good theory of mind and go beyond rote instructions when given a good harness. If you find yourself writing ALWAYS or NEVER in all caps, that is a yellow flag. Reframe and explain the reasoning instead.
4. **Look for repeated work across test cases.** If all the test runs independently wrote a similar helper script or took the same multi-step approach, that is a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it.

Take your time and mull it over. Write a draft revision, then look at it anew and improve it.

### The iteration loop

After improving the skill:

1. Apply your improvements.
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs.
3. Show the user the new results next to the previous iteration.
4. Wait for the user to review.
5. Read the new feedback, improve again, repeat.

Keep going until the user says they are happy, the feedback is all empty, or you are not making meaningful progress.

---

## Description tuning

The description field is the primary mechanism that determines whether the model invokes a skill. After creating or improving a skill, offer to tune the description for better triggering accuracy.

### Step 1: generate trigger eval queries

Create about 20 eval queries - a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

The queries must be realistic - the kind of thing a real user would type. Concrete and specific, with detail: file paths, personal context about the user's job or situation, column names and values, company names, URLs, a little backstory. Some in lowercase, some with abbreviations or typos or casual speech. Mix lengths. Focus on edge cases over clear-cut ones.

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. revenue is in column C and costs are in column D i think"`

For the **should-trigger** queries (8 to 10), aim for coverage. Different phrasings of the same intent, some formal, some casual. Include cases where the user does not name the skill or file type but clearly needs it. Throw in uncommon use cases and cases where this skill competes with another but should win.

For the **should-not-trigger** queries (8 to 10), the most valuable are the near-misses - queries that share keywords or concepts with the skill but actually need something different. Adjacent domains, ambiguous phrasing where a naive keyword match would trigger but should not. Do not make negatives obviously irrelevant. "Write a fibonacci function" as a negative for a PDF skill is too easy and tests nothing.

### Step 2: review with the user

Present the eval set to the user. They can edit queries, toggle should-trigger, and add or remove entries. This step matters - bad eval queries lead to bad descriptions.

### Step 3: run the tuning loop

Evaluate the current description by running each query a few times to get a reliable trigger rate, then propose an improved description based on what failed. Re-evaluate. Iterate a handful of times. Split the eval set so you select the winning description by held-out test score rather than train score, to avoid overfitting.

### How skill triggering works

Skills appear in the model's available-skills list with their name and description, and the model decides whether to consult a skill based on that description. The model only consults skills for tasks it cannot easily handle on its own. Simple one-step queries like "read this PDF" may not trigger a skill even with a perfect description, because the model handles them directly. Complex, multi-step, or specialized queries reliably trigger skills when the description matches. Make your eval queries substantive enough that the model would actually benefit from the skill.

### Step 4: apply the result

Take the winning description and update the skill's SKILL.md frontmatter. Show the user before and after, and report the scores.

### Step 5: description length check (mandatory)

Run the HARD CHECK from the top of this file (at or under 900 PASS, 901 to 1024 WARN, over 1024 STOP). Tuning loops sometimes produce long descriptions that score well on triggering but exceed the install ceiling.

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
