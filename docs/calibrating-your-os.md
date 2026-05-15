# Calibrating your OS

FounderOS guarantees some behaviors in code and asks you to trust others to the model. This page tells you which is which, and shows you how to test the trust-based ones yourself when it matters.

If you do not yet have budget for the API and time for the work below, skip this page. The defaults are fine.

---

## Two layers of reliability

**Python-enforced.** A small Python script preflights the skill. If a required file is missing or empty, the script exits with a non-zero code and the skill stops. The model cannot drift past an exit code. Behavior is deterministic.

**Instruction-only.** The skill is a markdown body the model follows. There is no script gate. The model follows the instructions because they are clearly written and the model is well-trained. Behavior is model-dependent and varies across sessions.

Most skills in FounderOS are instruction-only. The five writing skills (LinkedIn, email, client update, proposal, content repurpose) and four reasoning skills (weekly review, decision framework, meeting prep, strategic analysis) have a Python gate before they produce output. Brain-pass has one before it scans the log.

To see the table, run `/founder-os:verify` and read the Skill reliability section.

---

## When "good enough" is good enough

Instruction-only skills work fine for most operators. Two reasons.

First, the SKILL.md bodies are explicit. Voice rules are spelled out, banned phrases listed, structure prescribed. A modern model follows that scaffolding closely.

Second, the user is in the loop. You read the output. If a draft sounds wrong, you say so and the next pass corrects. The cost of a bad first draft is a 30-second redo, not a shipped bad draft.

For most operators, this is the right tradeoff. Do not invest in calibration unless you have a specific reason.

---

## When to invest in calibration

Calibrate when one of these is true:

- You are about to ship something where a generic-sounding output costs real money (a high-stakes proposal, a partnership pitch, a public post on a sensitive topic).
- You have noticed a specific skill producing inconsistent output across sessions and want to know whether it is the skill or your own input that varies.
- You are comparing two model versions (e.g. Claude moves from one release to the next) and want to know if behavior shifted on a skill you depend on.
- You are evaluating FounderOS for a team and want evidence that the skills you care about hold up across runs.

In each case, the investment is bounded and the payoff is concrete. Otherwise, do not bother.

---

## How to run a behavioral trace yourself

You do not need a framework. You need a question, a target, and 30 minutes.

### Step 1 - Pick the skill and define good output

Pick one skill. Write down, in one or two sentences, what a good output looks like. Be specific. Examples:

- LinkedIn post: opens with a confession or contrarian stance, every line one thought, no rule-of-three lists, ends without "what do you think?"
- Email drafter: under eight sentences, leads with the point, no warm-up greeting, signs off with first name only.
- Decision framework: leads with the user's decision style (gut, data, dialogue, mixed) from `core/identity.md`, then runs the standard framework after.

If you cannot describe good output in two sentences, your spec is fuzzy and any trace will be noisy. Tighten the spec first.

### Step 2 - Pick three to five inputs

Use real situations, not toy examples. The more your test inputs resemble actual prompts you would type, the more useful the trace. For a LinkedIn skill, three real topic ideas. For an email skill, three real situations needing replies.

Save the inputs in a plain text file so you can re-run them later against a different model version.

### Step 3 - Run each input three times in a fresh session

Open a new Claude Code session for each run. Do not chain runs in one session - the model carries context from earlier turns and the trace becomes unreliable.

For each input, run the skill three times and save the three outputs. You now have 9 to 15 outputs.

### Step 4 - Score each output against your spec

For each output, mark every spec rule as pass / fail. Do not score on a 1-5 scale - it invites compromise. Pass or fail.

Count the failures across all outputs. Three buckets:

- Zero or one fail across all runs: the skill is reliable for your use. Stop here.
- Two to four fails, but they cluster on the same rule: the SKILL.md is unclear or the rule is hard to follow. Read the relevant section of the SKILL.md and tighten it. Re-run.
- More than four fails, spread across rules: the model is not following the skill scaffolding. Two options - either rewrite the skill to be more explicit, or accept that this skill is for first drafts only and you will edit every output.

### Step 5 - Re-run when the model changes

When you upgrade your Claude version (or any time you suspect drift), re-run the same input file against the new model. Compare the new fail counts to the old. If they got worse, investigate.

This is the whole loop. No framework, no Anthropic API calls, no library. Just a question, a spec, and 30 minutes per skill.

---

## What FounderOS does not do for you

FounderOS does not run behavioral traces for you. That work is yours.

There are reasons it stays this way. Running a trace costs API tokens and time. Most operators do not need it. The skills that matter most for first-time setup are already Python-gated (voice, identity, log history). Building an automated trace runner would push every operator to pay for tokens they do not need.

If a future version of FounderOS adds an automated trace runner, it will be opt-in and you will see it in the release notes.

---

## See also

- `/founder-os:verify` - the reliability table for every writing and reasoning skill
- `rules/operating-rules.md` Honest Degradation section - the OS rule on what to do when a gate fails or context is stale
- `scripts/check-voice-ready.py`, `scripts/check-identity-ready.py`, `scripts/check-log-has-history.py` - the three gate scripts that enforce Python-level guarantees
