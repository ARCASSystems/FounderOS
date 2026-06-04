# Test cases, running, and evaluating

Read this when you reach the test-case and evaluation part of the loop.

## Test cases

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
