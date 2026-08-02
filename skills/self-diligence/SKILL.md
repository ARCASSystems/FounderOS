---
name: self-diligence
description: >
  Stress-test your own venture the way an investor, an acquirer, or a serious partner will, before they do it to you. Trigger on "what would an investor say", "diligence read", "score my business", "am I ready to raise", "pressure-test this before the meeting", "what will they ask me", or when preparing for a funding, partnership, or acquisition conversation. Produces five scored dimensions, a SWOT, the critical challenges, and the questions you must be able to answer in the room.
why: "A diligence analyst reads your business against a scoring frame and a list of questions you never see until you are in the room. This runs that frame over your own files first, so the hard questions arrive while you can still do something about them."
enhance: "The more of your real state is written down - priorities, decisions, clients, unit economics, the brain log - the more of this is scored rather than left as an open question. An empty OS produces mostly questions, which is itself an honest answer."
allowed-tools: ["Read", "Bash"]
mcp_requirements: []
---

# Self-diligence

Runs on: reasoning - reads your files and reasons; any capable agent can run this.

Someone is going to score your business. An investor, an acquirer, a bank, a large customer's procurement team, a partner deciding whether to bet their own reputation on you. They will do it against a frame you never see, and they will do it after you have already made your case, when you can no longer fix anything.

This runs that frame first, over your own files, while there is still time.

## The one rule this whole skill rests on

**Anything you cannot ground in the founder's own files becomes a question to the founder. It is never invented, and it is never softened into a hedge.**

A diligence analyst who fills in the missing half from general knowledge is worse than useless, because their confidence hides exactly where the risk is. So is this skill if it does that. If the files do not say what the churn rate is, the output does not estimate the churn rate, does not say "churn appears healthy", and does not quietly leave it out. It says: **not in your files - what is it, and how do you know?**

That is not a limitation to apologise for. The unanswerable questions ARE the deliverable. They are the ones you will be asked.

## Before you start

Run `python scripts/check-identity-ready.py`. If it exits 1, surface the line verbatim and stop: a diligence read built on an empty identity file is a template with your name on it.

Then read, in this order, whichever exist:

1. `core/identity.md` and `core/founder-snapshot.md` - who is running this and what stage they say they are at.
2. `context/priorities.md`, `context/decisions.md` - what they are actually doing and what they have already ruled out.
3. `context/clients.md`, `context/leads.md` - real revenue and real pipeline, which is the difference between a story and a business.
4. `brain/log.md`, `brain/flags.md` - what has actually happened, and what is already known to be broken.
5. `cadence/weekly-commitments.md` - whether the stated plan and the enacted week are the same thing.
6. Anything under `companies/` for the entity being scored.

Read the files. Do not ask the founder to summarise what is already written down.

## The five dimensions

Score each 0 to 10 with three parts: strengths, considerations, and one recommendation. The frame is the one a real diligence house uses; the discipline is that every score cites the file it came from.

| # | Dimension | What it actually scores |
|---|---|---|
| 1 | Market potential | Is the "why now" real and evidence-backed, or a narrative. Is the sizing built bottom-up from countable units, or a top-down market report multiplied down. Is near-term revenue broad, or three big lumps that could each slip a quarter. |
| 2 | Differentiation | What is genuinely hard here. What stops a well-funded competitor doing this next quarter. If the honest answer is "nothing", that is a 3, not a diplomatic 6. |
| 3 | Team | Has anyone here shipped the hardest part before. What is the named gap, and is there a plan for it that is not "we will hire someone". A solo founder is not a low score by itself; an unacknowledged single point of failure is. |
| 4 | Business model and commercial path | Does the money mechanism work at the unit level. Is there a signed anything. What is the path from one-off work to repeatable, and has any part of it repeated yet. |
| 5 | Readiness for the conversation | Is the evidence assembled. Are the risks disclosed before they are found. Would a diligence pass turn up surprises. This is the dimension most founders score worst on and think they score best on. |

## The scoring floor

**No evidence is not a 5.** A dimension with nothing behind it in the files is reported as `unscored - no evidence in your files`, plus the specific question that would produce the evidence. Averaging in an invented middle score launders an unknown into a number, and the number is what gets remembered.

Report the overall average only when at least four of five are scored. Otherwise report the scored ones and say plainly which are not and why.

Every number in the output carries a tier tag per `rules/research-integrity.md`. A score is an `[ESTIMATE]` with its basis named. It is never dressed as a measurement.

## Output

```text
SELF-DILIGENCE READ: <business>
Run <YYYY-MM-DD> against <n> files in your OS

OVERALL: <x.x>/10 - <one line> | or: 3 of 5 scored, see gaps

SCORES
1. Market potential          <x.x>/10  <one line, citing the file>
2. Differentiation           <x.x>/10  <one line>
3. Team                      <x.x>/10  <one line>
4. Business model            <x.x>/10  <one line>
5. Readiness                 <x.x>/10  <one line>

PER DIMENSION
<for each: Strengths / Considerations / Recommendation>

SWOT
Strengths      <from evidence, not aspiration>
Weaknesses     <the ones you would rather not write down>
Opportunities  <only where a path exists, not every adjacent market>
Threats        <including the boring ones: a key client leaving, a rate change>

CRITICAL CHALLENGES
<the three to five things that actually decide whether this works>

DISCLOSED GAPS
<what your files do not answer, stated plainly>

THE QUESTIONS THEY WILL ASK
<every ungrounded claim, rewritten as the question a diligence analyst asks>
```

## Why the disclosed-gaps section is a feature

A real diligence analysis of a pre-seed company scored it 7.0 out of 10, and named the reason confidence went UP rather than down: metrics audited downward rather than up, an honest ledger of what had not been captured yet, abandoned attempts disclosed rather than buried, and a named known-risks section that pre-empted the diligence process instead of waiting to be caught by it. The analyst called it a rare and positive signal of founder integrity.

That is the whole argument for this skill. The transparency founders instinctively hide is scored as integrity by the exact audience they are hiding it from. So the disclosed gaps go in the document as a section with a heading, not as a hedge in the last paragraph.

## Rules

- Never invent a fact, a number, or a customer. An ungrounded claim becomes a question. This is not negotiable and it is the only reason to trust the output.
- Score on evidence in the files, not on the story in the room. Founder confidence is not evidence.
- If you cannot write a real Weaknesses section, you have not read hard enough. Go back. Every business has them and the reader knows it.
- Cite the file behind each score, so the founder can go fix the source rather than argue with the number.
- This reads the venture, not the person. Whether this founder should be running this business is a different question and not this skill's call.
- Simple hyphens (-), no em or en dashes.
