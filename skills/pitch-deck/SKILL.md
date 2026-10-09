---
name: pitch-deck
description: >
  Build an investor or sales pitch deck. Say "build my pitch deck", "investor deck",
  "help me pitch this", "deck for the raise", "make a deck for this" (or run
  /founder-os:pitch-deck). Challenges the story before building it, interviews you one
  question at a time, writes a slide-by-slide spec you own, checks every number, and
  renders a .pptx you can open and edit.
why: "A founder who needs a deck writes it in a chat window and then retypes it into slides, which is where the structure gets lost and the numbers drift from the ones that were checked - and where the hard questions get skipped entirely because the deck-building feels like progress."
enhance: "Run this after strategic-analysis on the same market - the deck's market slide then inherits sourced numbers with retrieval dates instead of round figures you cannot defend in the room."
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob"]
mcp_requirements: []
---

# Pitch deck

Runs on: local-exec for the render, reasoning for everything before it. The spec is markdown and is the deliverable. The `.pptx` is a render of it, and needs one package that does not ship with Python.

## The order matters

Most decks fail before the first slide, on a story nobody stress-tested. So the order is: challenge, interview, write the spec, check the numbers, then render. Do not jump to slides because slides feel like progress.

## Step 1 - Challenge the story

Before any question about slides.

1. Say the business back in one sentence: who it is for, what changes for them, how you make money. If you cannot, that is the first thing to fix and it is not a slide problem.
2. Name the one thing an investor will push on hardest. Not three. The one that ends the meeting: the market is smaller than claimed, the founder cannot sell, the numbers are projections wearing the grammar of results, someone bigger does this already.
3. Ask exactly one question. The one whose answer changes the deck most.
4. Wait for the answer. Then go on.

Skip this only if the founder has already answered that question in what they gave you.

## Step 2 - Interview, one question at a time

Never present all ten at once. Ask, take the answer, ask the next. If an answer is thin, say what is thin about it and ask again once, then move on and mark it for the gaps list.

1. Who is the customer, specifically? A job title and a situation, not a segment.
2. What do they do today instead, and what does that cost them?
3. What do you do, in one sentence a customer would recognise?
4. What proof do you have that it works? Name the strongest real thing: a paying customer, a pilot, a number. If there is none, say so now rather than in the room.
5. How do you make money, and what does one customer pay?
6. How big is the reachable market, and where did that number come from?
7. Who else does this, and why does a customer pick you? A named competitor, not "no direct competitors".
8. How do customers find you, and which route is proven versus hoped for?
9. What are you raising, and what does it buy? Milestones, not runway alone.
10. Who is on the team and why these people for this problem?

## Step 3 - Write the spec

Write to `decks/<slug>-deck.md`. The format the renderer reads:

```markdown
# Company name
subtitle: What the deck is for

## The problem
- One line per bullet. Six words to fifteen.
- At most four bullets per slide.
> Speaker notes. What you say out loud, not what is on the slide.
```

`#` is the deck title, `##` starts a slide, `-` is a bullet, `>` is a speaker note.

Ten slides, in this order, and do not add more without saying why:

1. **Title.** Company, one line on what you do, what you are raising.
2. **The problem.** Whose problem, and what it costs them today.
3. **The solution.** What you built, in the customer's words.
4. **How it works.** Three steps at most.
5. **Proof.** The strongest real evidence. Where there is none, this slide says what you are testing and by when. An empty proof slide is more honest than a decorated one.
6. **Market.** The reachable number, with where it came from on the slide.
7. **Business model.** What one customer pays and what it costs to serve them.
8. **Competition.** Named alternatives and why a customer picks you.
9. **The ask.** The amount, what it buys, the milestones it reaches.
10. **Team.** Why these people for this problem.

Writing rules for every slide: a headline that states a claim rather than labelling a topic ("Brokers lose four hours a day" beats "The Problem"), at most four bullets, no bullet longer than a line. The speaker notes carry the argument. The slide carries the evidence.

## Step 4 - Check the numbers before they reach a room

Every number on a slide is governed by `rules/research-integrity.md`. Tag each one in the spec with its tier, on the line under the claim:

- `[SOURCED: <url>, retrieved <date>]` for anything fetched.
- `[MEASURED: <artifact> + <command>]` for anything from your own files.
- `[ESTIMATE: <assumption>]` for your judgment, with the assumption stated.

Then run the second pass, which is the whole point of having a spec:

```bash
python scripts/claims_check.py decks/<slug>-deck.md
python scripts/register_census.py decks/<slug>-deck.md --gate deliverable
```

The first names untagged numbers, unsourced quotes, unbounded negatives like "no one else does this", and arithmetic that does not reconcile. The second counts the writing tells. Report both to the founder before rendering. A projection written in the grammar of a result is the single most expensive thing a deck can carry, because it is the one an investor checks.

## Step 5 - Render

```bash
python scripts/pitch_deck.py decks/<slug>-deck.md --check
python scripts/pitch_deck.py decks/<slug>-deck.md
```

`--check` parses and counts without writing. The second writes `decks/<slug>-deck.pptx`.

**This needs `pip install python-pptx`**, and it is one of only two shipped scripts that asks for anything beyond Python itself. If the package is missing the script exits with the exact command and says so. When that happens, do not treat it as a failure: the spec is the deliverable and it opens in any editor, pastes into Canva, Gamma, Pitch or Google Slides, and carries the speaker notes with it. Say that in one line and hand over the markdown.

The deck's font and author come from `os-config.yaml`. With no `brand.document_author` set, the file is left unstamped rather than credited to the library that made it, and the script says so. Never let a deliverable credit a tool as its author.

## Step 6 - Close with the gaps

The last thing you give the founder is not the file. It is the short list of what the deck cannot yet defend:

| The gap | What it costs in the room | What closes it |
|---|---|---|
| The thing you could not evidence | The question it loses you | The smallest real step |

Be specific. "No paying customer yet" with "one paid pilot at any price, once you know you may take money for it where you sell" beats a page of caveats.

## What this does not do

It does not design. The render is a plain, readable deck with the founder's font, and it is meant to be edited. A founder who wants it beautiful should take the spec into a design tool, which is why the spec carries the speaker notes and the structure rather than the styling.

No em dashes or en dashes anywhere in the deck or the notes. Hyphens only.
