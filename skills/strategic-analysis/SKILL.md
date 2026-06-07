---
name: strategic-analysis
description: >
  Run a strategic analysis: competitive map, market sizing, opportunity, or business model. Trigger on "analyze this market", "competitor map", "evaluate this opportunity", "market research", "SWOT", "who are the competitors", "market sizing", "TAM SAM SOM", or any variation of strategic business analysis. Also fires when the user describes a business opportunity or competitor and wants structured thinking.
why: "Grounds competitive and market analysis in your actual position and prior knowledge rather than producing a generic table that ignores what you already know or have decided."
enhance: "Populate brain/knowledge/ with notes from books and conversations about the market and competitors - the skill reads matching topics by name and uses them as prior evidence in the analysis."
allowed-tools: ["Read", "Bash"]
mcp_requirements: []
---

# Strategic Analysis Tool

Runs on: reasoning - reads your files and reasons; any capable agent can run this.

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

Before producing output, read `brain/.snapshot.md` if it exists.

If the snapshot is missing, run:

    python scripts/brain-snapshot.py --write

Then read it. If the snapshot script is also missing (older install), proceed using only the profile files. Do not block.

The snapshot tells you what flags are open, what the user is working on this week, and what the latest staleness state is. Apply this context to your output where it is relevant. Do not surface every snapshot field in every output - use judgment. For strategic analysis, open flags often reveal blocking constraints the analysis must respect, and recent decisions bound the option space you are allowed to recommend from.

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
[Matching notes from brain/knowledge/, or "No matching knowledge files found."]

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
[Matching notes from brain/knowledge/, or "No matching knowledge files found."]

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
[Matching notes from brain/knowledge/, or "No matching knowledge files found."]

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
[Matching notes from brain/knowledge/, or "No matching knowledge files found."]

VERDICT
[Viable / Viable with changes / Not viable, and the single biggest reason]
```

## Rules

- Show reasoning, not just conclusions
- Flag assumptions explicitly
- Be skeptical by default
- Numbers wherever possible
