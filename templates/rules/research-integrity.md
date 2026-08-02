# Research integrity - three claim tiers and a second pass

Your OS already keeps capture honest: the provisional-fact ledger holds a name or a number as unconfirmed until you say otherwise, and confirm-or-cut makes you decide. That covers what comes IN.

This file covers what goes OUT. When the OS researches a market, sizes an opportunity, prices a proposal, or reads a competitor, it produces numbers. Those numbers get pasted into decks and shown to buyers, partners, and investors. An AI-drafted research document invents precise-looking claims, and a precise-looking claim is the one that survives review, because it looks like somebody already checked it.

The failure classes repeat, whoever is writing:

- A precise statistic with no source ("42% of buyers report...").
- A verbatim quote attributed to a person, that appears nowhere findable.
- A universal negative: "no tool does this", "nobody serves this market".
- An estimate written in the grammar of a measurement.
- Two numbers in the same document that contradict each other, which no per-page review catches.

## The three tiers

Every load-bearing claim carries one tag, inline, on its own line. Each tag is an obligation you accept, not a label you apply:

- **`[MEASURED: <artifact> + <command>]`** - reproducible from a file you hold. Name the file and the command that re-derives it. If a reader cannot re-run it, it is not measured.
- **`[SOURCED: <url>, retrieved <date>]`** - one live link and the day you fetched it. A date matters: the web changes and a link without a date cannot be audited later.
- **`[ESTIMATE: <assumption>]`** - your judgment. State the assumption inline so a reader can re-derive the number and swap the assumption for their own.

A number with no tier tag does not go in a deck. It gets tagged or it gets cut. An estimate is completely honest; an estimate dressed as a measurement is the thing that costs you the room.

## Two hard rules

1. **Quotes carry a link.** A verbatim quote attributed to a person or a publication has a retrievable URL and a date, or it is deleted. Never promote a paraphrase into quotation marks.
2. **Universal negatives become bounded searches.** "No tool does X" cannot be verified by anyone, including you. Write what you actually did: "checked A, B and C on <date>, found none." That version is true, defensible, and still makes your point.

## Arithmetic has to reconcile

Where a document shows both operands and a result, the math must check out. This is the error that hides best: a cost table where nine rows reconcile and the tenth is off by 11% reads as a careful document right up until the buyer runs it.

## The reviewer is not the writer

Run the check as a second pass over the finished document, not while drafting. The writing pass is arguing a case; the checking pass reads only for coverage and contradiction. They are different jobs and they interfere with each other.

    python scripts/claims_check.py <your-document.md>

It prints what is uncovered: untagged numbers, unsourced quotes, unbounded negatives, arithmetic that does not reconcile. It warns, it never blocks, and it never edits your file. The judgment stays yours; the script only makes the debt visible.

## Where it applies

Any output carrying numbers a decision would rest on: market sizing, competitive reads, pricing and unit economics, proposals, feasibility reads, diligence prep. The skills that produce those name this rule, and `ship-deliverable` runs the check before a research-class document leaves your machine.

A polished document does not have to show tags. It can resolve them into prose: "re-run this from the code in the repo", "source: <url>, retrieved <date>", "our estimate, assuming X". But every claim passes through the tagged draft first. Resolving a tag never removes the obligation behind it.

## What this is not

Not citation theatre. A paragraph of context needs no tags. The tag belongs on the load-bearing claim, and there is one test for that: **if this number is wrong, does the recommendation change?** If yes, tag it. If no, leave it alone.

Dates, version numbers, and amounts already fixed by a contract you hold are not claims. Neither is arithmetic you show your work for.
