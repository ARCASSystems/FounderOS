---
name: strategic-analysis
description: >
  Run a strategic analysis: competitive map, market sizing, opportunity, or business model. Trigger on "analyze this market", "competitor map", "evaluate this opportunity", "market research", "SWOT", "who are the competitors", "market sizing", "TAM SAM SOM", or any variation of strategic business analysis. Also fires when the user describes a business opportunity or competitor and wants structured thinking.
why: "Grounds competitive and market analysis in your actual position and prior knowledge rather than producing a generic table that ignores what you already know or have decided."
enhance: "Populate brain/knowledge/ with notes from books and conversations about the market and competitors - the skill reads matching topics by name and uses them as prior evidence in the analysis."
allowed-tools: ["Read", "Bash", "WebSearch", "WebFetch"]
mcp_requirements: []
---

# Strategic Analysis Tool

Runs on: reasoning, with optional web reach - reads your files and reasons. Where the web
is reachable it grounds the market half in live sources; where it is not, it says so in one
line and works from your files alone. It never quietly produces an ungrounded market table.

No fluff. Every insight should lead to a decision or an action.

## Before You Write

First, run: `python scripts/check-identity-ready.py`

If exit code is 1, read the output line and surface it to the user verbatim. Do not run the analysis. Stop.

Then read these files so the analysis is grounded in the user's actual position, not a generic competitive table.

1. **`core/identity.md`** - the founder's businesses and what they are building. The analysis is from THEIR seat, not from a neutral observer.
2. **`context/companies.md`** - portfolio of companies and projects. Lift competitor and adjacent-business context from here before doing fresh research.
3. **`context/decisions.md`** - prior decisions that bound the option space. Do not recommend an option already ruled out.
4. **`brain/knowledge/`** - captured notes relevant to the market, competitor, framework, customer segment, or prior pattern. Read frontmatter and top headings first. Reference matching topics by name.
5. **Company-specific context (if analysing a specific company).** Two-path check:
   1. `companies/<slug>-business.md` (operator path - the company you run, if the analysis is about a brand you operate)
   2. `companies/prospects/<slug>.md` (prospect path - a competitor or target company you have tracked)

   Prefer the operator file if both exist. If neither exists and the analysis is about a specific named company, name the gap explicitly in the OUR POSITIONING block - do not invent fit signals, anti-ICP signals, or relationship state.

If a file is empty or missing, name the gap explicitly in the OUR POSITIONING block. Do not silently default to a generic stance.

## Brain context (default)

Before producing output, read `brain/.snapshot.md`. If it is missing, or its `date:` line is more than 3 days old, run `python scripts/brain-snapshot.py --write` first and read the fresh one - a stale snapshot read as current presents last week's flags and must-dos as today's, which is worse than no memory at all. If Python is unavailable, proceed without it and say so.

If the snapshot is missing, run:

    python scripts/brain-snapshot.py --write

Then read it. If the snapshot script is also missing (older install), proceed using only the profile files. Do not block.

The snapshot tells you what flags are open, what the user is working on this week, and what the latest staleness state is. Apply this context to your output where it is relevant. Do not surface every snapshot field in every output - use judgment. For strategic analysis, open flags often reveal blocking constraints the analysis must respect, and recent decisions bound the option space you are allowed to recommend from.

## Challenge the inputs before you analyse anything

An analysis built on a premise nobody tested is a confident answer to the wrong
question, and it is harder to unpick later than a blank page. So before the
framework, before any search, stress-test what you were handed.

1. Say back the premise in one sentence, in your own words. If you cannot, the
   ask is not clear enough to analyse yet.
2. Name what a sceptical buyer or investor would push on first. Not three things.
   The one that would end the meeting.
3. Name what you would need to know to answer it, and whether you can get it.
4. Ask exactly one question. The one whose answer changes the analysis most.
5. Wait for the answer. Then analyse.

Skip this only when the founder has already answered that question in the ask
itself. Do not skip it because the ask sounds clear: the clear-sounding ones are
where an untested premise hides.

## Grounding the market half in live sources

The files tell you your position. They do not tell you the market. Both halves
are needed and they come from different places, so keep them separate and keep
the sourcing honest.

1. **Search for what you actually need**, not for the topic. A search for
   "the coffee market" returns a report summary. A search for "what three
   competitors charge for a monthly plan" returns something you can put in a
   table. Name the question before the query.

2. **Fetch the page, do not trust the summary.** A search result snippet is
   somebody's description of a number. Open the page with `WebFetch`, or where
   a page needs more careful extraction, run the `web-fetch-extract` skill,
   which uses `python scripts/scrape.py <url>` and falls back to `WebFetch`
   when the script or its packages are missing.

3. **Every fetched number becomes a `[SOURCED: <url>, retrieved <date>]`.** The
   date is not decoration: the web changes, and a link without a date cannot be
   audited six months later when somebody asks where the figure came from. A
   number you reasoned to is an `[ESTIMATE: <assumption>]` and is completely
   honest as one. An estimate dressed as a measurement is what costs you the room.

4. **When the web is not reachable, say so in one line and carry on.** Web
   search is not available on every plan or in every surface, and an org can
   switch it off. If `WebSearch` is unavailable or returns nothing usable, do
   not silently produce a market table that looks sourced and is not. Say:
   `Web search was not available, so the market numbers below are estimates from
   your files and my reasoning, not live sources.` Then tag every one of them
   `[ESTIMATE: ...]`, and put the searches you would have run into the research
   table at the end so the founder can run them by hand or paste a page in.

   If the founder gives you a URL directly, `web-fetch-extract` works with no
   search at all. One named page beats a search you cannot run.

## Framework Selection

**"Who are we competing with?"** -> Competitor Map
**"How big is this market?"** -> Market Sizing
**"Should we enter this market?"** -> Opportunity Assessment
**"Is this a good business model?"** -> Business Model Evaluation

## Competitor Map

```
COMPETITOR MAP: [Market]
---
DIRECT COMPETITORS
| Company | What They Do | Strength | Weakness | Price |
|---------|-------------|----------|----------|-------|

INDIRECT COMPETITORS
| Company | How They Differ | When They Win | When We Win |
|---------|----------------|---------------|-------------|

SUBSTITUTES
-> [What the customer does instead of buying from any of us]

OUR POSITIONING
[One paragraph]

RELEVANT KNOWLEDGE
[Matching notes from brain/knowledge/, or "No knowledge notes matched the terms searched (<terms>) - if notes exist under another name, name the topic or run /founder-os:brain-pass."]

GAPS IN THE MARKET
[What nobody is doing well]
```

## Market Sizing

```
MARKET SIZE: [Market]
---
TAM: [Everyone who could theoretically use this. Math shown.]
SAM: [The portion we can actually reach.]
SOM: [What we can realistically capture in 12-24 months.]

RELEVANT KNOWLEDGE
[Matching notes from brain/knowledge/, or "No knowledge notes matched the terms searched (<terms>) - if notes exist under another name, name the topic or run /founder-os:brain-pass."]

ASSUMPTIONS
[Every assumption listed]

SENSITIVITY
[Which assumptions matter most]
```

## Opportunity Assessment

```
OPPORTUNITY: [Description]
---
THE CASE FOR: [Evidence, not hope]
THE CASE AGAINST: [Be honest]

RELEVANT KNOWLEDGE
[Matching notes from brain/knowledge/, or "No knowledge notes matched the terms searched (<terms>) - if notes exist under another name, name the topic or run /founder-os:brain-pass."]

WHAT WOULD HAVE TO BE TRUE
-> [Condition 1]
-> [Condition 2]

MINIMUM VIABLE TEST
[Smallest thing to test whether this works]

RECOMMENDATION
[Pursue / Don't pursue / Test first]
```

## Business Model Evaluation

```
BUSINESS MODEL: [Name]
---
VALUE PROPOSITION
[What job it does for the customer, in one sentence]

CUSTOMER SEGMENTS
[Who pays. Who uses. Whether they are the same.]

REVENUE MODEL
[How money comes in. Unit price, frequency, contract shape.]

COST STRUCTURE
[Biggest cost lines. Fixed vs variable. What scales linearly.]

KEY RESOURCES
[What the business cannot operate without]

KEY ACTIVITIES
[What the team has to be good at]

KEY PARTNERS
[Who carries load the business does not own]

CHANNELS
[How the offer reaches the customer and how the customer reaches back]

COMPETITIVE MOAT
[Why this is hard to copy. Be honest if it is not.]

RELEVANT KNOWLEDGE
[Matching notes from brain/knowledge/, or "No knowledge notes matched the terms searched (<terms>) - if notes exist under another name, name the topic or run /founder-os:brain-pass."]

VERDICT
[Viable / Viable with changes / Not viable, and the single biggest reason]
```

## Every number carries a tier

This skill produces market sizes, competitor prices, growth rates and counts. Those numbers get pasted into decks and shown to buyers and investors, so they are governed by `rules/research-integrity.md`.

Tag every load-bearing claim inline with one of three tiers. Each is an obligation, not a label:

- `[MEASURED: <artifact> + <command>]` - reproducible from a file you hold.
- `[SOURCED: <url>, retrieved <date>]` - one live link and the day you fetched it.
- `[ESTIMATE: <assumption>]` - your judgment, with the assumption stated so a reader can swap it.

Two rules bite this skill hardest. A GAPS IN THE MARKET line saying "nobody is doing this" is a universal negative that nobody can verify: write what you actually did instead, "checked A, B and C on <date>, found none". And a competitor quote in quotation marks carries a URL and a date, or it comes out.

Before the analysis goes anywhere, run the second pass. The reviewer must not be the writer:

    python scripts/claims_check.py <the document>

It warns, never blocks, never edits your file.

## Close with what to research next (every analysis, no exceptions)

An analysis that ends at its conclusion leaves the founder holding a verdict and
no next move. The last section is always this table, and it is the part most
likely to get used:

| The gap | Why it matters | Paste this to close it |
|---|---|---|
| What you could not establish | What decision it blocks, in one line | A prompt or a search they can run as written |

Three rules for it:

- **Name real gaps, not polite ones.** If the whole market size is an estimate,
  the first row says so. A table of minor caveats under a confident analysis is
  worse than no table.
- **The third column has to be runnable as written.** Not "research competitor
  pricing". A prompt they can paste, or a search string, or a named page to
  fetch. If you could not reach the web, this column is where those searches go.
- **Order by what it unblocks**, not by how hard it is.

## Rules

- Show reasoning, not just conclusions
- Flag assumptions explicitly
- Be skeptical by default
- Numbers wherever possible, each one tagged per `rules/research-integrity.md`
