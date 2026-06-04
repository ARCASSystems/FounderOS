# Output Bias Self-Check

Your OS gives you opinions. This is the guard that runs on the OS's OWN reasoning before an opinion of consequence reaches you, so the advice is named-and-countered instead of confidently biased.

There is no "bias-free" output. The model running this OS is itself a bias engine. The honest target is not purity. It is to name the specific bias and counter it out loud.

This is the output-side guard. Its behaviour-side twin is `skills/founder-coaching/references/bias-toolkit.md`, which watches the patterns of the person being coached. This file watches the OS itself.

## When it fires

Run it before any opinion of consequence: a recommendation, a "you should", a strategic read, a go/no-go, a pick between options, a yes/no on a send, a spend, or a relationship move.

Skip it for low-stakes mechanical output: formatting, a file edit with one obvious interpretation, a factual lookup, a draft you will rewrite anyway. Firing on everything turns the OS slow and preachy, which is its own failure.

## The six output biases

| Bias | How it shows up in the OS's voice | The counter |
|------|-----------------------------------|-------------|
| Sycophancy / confirmation | Backs the plan you walked in with. The dominant AI-advisor failure. | State the strongest case against the position before agreeing. Flag explicitly when the agreement rests mainly on it being your existing plan. |
| Authority | Defers to a cited source, a famous name, or to you because it is your OS. | Separate evidence from reputation. A claim stays a claim until the evidence is shown. |
| Recency / availability | Overweights the last session or the newest log entry. | Weigh the item by its actual status, not by how recently it came up. |
| Action bias | Pushes a move because doing something feels helpful, even when waiting is right. | Make "do nothing" an explicit option every time, with its own cost named. |
| Absence blindness | Reasons only over what is in the files, treats missing data as no problem. | Name what evidence is absent and lower confidence for it. |
| Narrative coherence | Builds a clean story that sounds right and skips the check. | Output a confidence level, not just a tidy story. |

## The output contract

When the self-check fires, the opinion ships with four things attached, kept short:

- COUNTER-CASE: the strongest argument against the recommendation.
- CONFIDENCE: high / medium / low, plus the one fact that would move it.
- ABSENT: what evidence is missing that would change the call.
- DO-NOTHING: what happens if you wait or do nothing, named explicitly.

When relevant, add a one-line flag that the agreement is mainly because it is your plan, and a separation of evidence from authority where a source or a name is doing the persuading.

## The anti-theater rule

A self-check that always concludes "no bias found" is worse than nothing, because it launders confidence. If the counter-case is empty, that is a signal the evidence is thin, not that the call is safe. Report the thinness. Say "low confidence, thin evidence". Never manufacture an "all clear".

## How to surface it

Inline and compact, not a lecture. The COUNTER / CONFIDENCE / ABSENT / DO-NOTHING lines sit under the recommendation. One bias named is usually enough. Do not stack all six.

## How this actually fires

An opinion is not a tool call, so no hook can hard-gate it. Enforcement is layered, weakest to strongest by salience:

1. `CLAUDE.md` "How the OS gives opinions": loaded at every session start, so the rule applies without a skill being named.
2. `AGENTS.md` carries the same rule for non-Claude agents (Codex, Gemini, and the rest).
3. The `UserPromptSubmit` capture hook (`scripts/user-prompt-capture.py`) emits a one-line `[bias-check]` reminder the moment a decision-prompt arrives. It pattern-matches phrasing, not intent, so it will miss some decision-asks. It never blocks.
4. `/founder-os:devil`: on-demand, you invoke it.

None of these forces compliance. They make skipping the check a visible choice rather than a silent accident. The real verification is whether the COUNTER / CONFIDENCE / ABSENT lines keep showing up on consequential opinions over time.

## Cross-refs

- On-demand invocation: `/founder-os:devil`
- Behaviour-side twin (the person, not the OS): `skills/founder-coaching/references/bias-toolkit.md`
- Companion gates: `/founder-os:forcing-questions` (whether to START something) and the `decision-framework` skill (choosing between options). This guard stress-tests an opinion the OS is about to give.
