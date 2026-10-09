---
name: unit-economics
description: >
  Run business math: unit economics, pricing, CAC, LTV, margins, break-even. Trigger on "run the numbers", "what's the unit economics", "calculate margins", "pricing model", "break-even", "revenue projection", "cost analysis", "CAC", "LTV", "how much would it cost to", "is this profitable", "what should I charge", or any variation. Also fires when evaluating whether a deal, hire, or investment makes financial sense.
why: "Runs business math in a structured format that shows assumptions and scenarios rather than a single number that can be misread without context."
enhance: "Give real numbers rather than ranges when you can - the skill flags assumptions that could change the answer, but it cannot flag the ones you did not provide."
allowed-tools: ["Read", "Bash"]
mcp_requirements: []
---

# Unit Economics Calculator

Runs on: local-exec when Python is present - the arithmetic runs through `scripts/unit_math.py`. On a surface without Python I reason and show every step, so any capable agent can still run this.

You help the founder run business math quickly and clearly. Show the numbers, explain what they mean, and flag what matters.

## Identity preflight (soft)

Before producing output, run:

    python scripts/check-identity-ready.py

If exit code is 1, print the returned line as a one-line note above the result and continue. The math runs without identity set up, but the recommendation gets sharper once `/founder-os:setup` has filled in `core/identity.md` (the skill can then frame numbers against the founder's actual business model).

## Brain context (default)

Before producing output, read `brain/.snapshot.md`. If it is missing, or its `date:` line is more than 3 days old, run `python scripts/brain-snapshot.py --write` first and read the fresh one - a stale snapshot read as current presents last week's flags and must-dos as today's, which is worse than no memory at all. If Python is unavailable, proceed without it and say so.

If the snapshot is missing, run:

    python scripts/brain-snapshot.py --write

Then read it. If the snapshot script is also missing (older install), proceed using only the profile files. Do not block.

The snapshot tells you what flags are open, what the user is working on this week, and what the latest staleness state is. Apply this context to your output where it is relevant. Do not surface every snapshot field in every output - use judgment. For unit economics, recent decisions tell you which pricing or hiring choices are off the table, and open flags often signal a stalled commercial decision the math can unblock.

## Lead with the business model's numbers

Read `business_model` from `stack.json` before framing anything. The Core Metrics below are universal, but which ones LEAD is decided by the model - a service founder asking "am I profitable" needs utilization and effective day rate first, not MRR. These mappings are textbook-stable, so branching on them is honest determinism:

- **`service`** - lead with: utilization rate, effective hourly / day rate, delivery margin per engagement, capacity (how many engagements the team can hold before quality slips). Pricing conversations anchor on value and scope, not hours, but the floor is always cost-to-deliver.
- **`ecommerce`** - lead with: average order value (AOV), contribution margin per order (after product cost, shipping, packaging, payment fees, returns), blended CAC, inventory turns, and cash tied up in stock. A "profitable" product with two turns a year can still starve the business of cash - say so when the numbers show it.
  - **Made in batches (food, baking, small-batch products):** cost the batch, not the item. Cost per sellable unit = batch cost / units left after waste. Cost per box = that x units per box + packaging, then add per-order delivery, platform and payment fees. Whole boxes matter: units left over after the last full box either carry into the next batch or are wasted, and the cost per box is very different in the two cases, so show both. The founder's own time is an economic cost (hours x what an hour of their time is worth): show it as its own line and say it is not cash unless they pay themselves. Capacity per week (one oven, the hours they have) caps revenue before demand does, so show it.
- **`saas_software`** - lead with: MRR, net and gross churn, CAC payback in months, LTV:CAC, and burn vs. months of runway. Growth claims mean nothing next to churn - check churn first.
- **`marketplace`** - lead with: GMV, take rate, net revenue (GMV x take rate), liquidity (fill rate / time-to-match), and CAC split by side. Name which side is the constraint before any spend recommendation.
- **`content_creator`** - lead with: audience reach per channel, revenue per thousand (RPM) or per sponsorship, conversion to owned audience (email), and income concentration (one platform or sponsor over half of revenue is a flag, not a win).
- **`regulated_deep_tech` / `other`** - lead with the domain-agnostic layer only: burn rate, runway, cost per experiment or milestone, and break-even at the accounting level. Then apply the domain-honesty rule below.
- **`null` (not set)** - ask one question ("how does the business make money?") and proceed with the closest set. Suggest capturing it: "say 'update my stack' and I will remember the model."

## Domain-honesty rule (regulated_deep_tech and other)

The accounting-level math above is safe for any business - cash in, cash out, runway, margins. What is NOT safe is generating domain economics the OS cannot validate: clinical trial cost structures, regulatory approval timelines, lab yield assumptions, legal exposure pricing. For those, state plainly that this needs the operator's own domain expertise or their expert's numbers, ask for the inputs, and run the arithmetic on what they provide. Never fill a domain-specific assumption from general knowledge and present it as a planning number - a confident wrong assumption survives review precisely because it looks like the others.

## Core Metrics

### Revenue Math
- **MRR:** customers x average revenue per customer
- **ARR:** MRR x 12
- **Revenue per employee:** total revenue / headcount
- **Output per worker:** revenue generated per team member

### Customer Economics
- **CAC:** (sales spend + marketing spend in a period) / new customers won in the same period. No customers won means CAC is undefined, not zero.
- **Contribution per customer per month:** revenue per customer per month - the variable cost to serve them (product or delivery cost, payment fees, support)
- **LTV (contribution):** contribution per customer per month x average customer lifetime in months. This is the LTV to compare with CAC.
- **LTV (revenue):** revenue per customer x lifetime. If you show it, label it as revenue, and do not compare it with CAC - it hides the cost of serving the customer.
- **LTV:CAC ratio:** contribution LTV / CAC (3:1 or better is a common rule of thumb)
- **CAC payback:** CAC / monthly contribution per customer (in months). If CAC is positive and monthly contribution is zero or negative, CAC is never paid back - say that instead of printing a number. If CAC is zero there is nothing to pay back, which is a different case: say so separately, and say how the customers were won.

### Profitability
- **Gross margin:** (revenue - direct costs) / revenue x 100
- **Net margin:** (revenue - all costs) / revenue x 100
- **Contribution per unit:** price - variable cost per unit
- **Break-even units:** fixed costs / contribution per unit, rounded up. If contribution per unit is zero and fixed costs are positive, the fixed costs are never recovered: selling more neither helps nor hurts. If contribution is zero and there are no fixed costs, profit is already zero at any volume. If contribution is negative, every extra sale makes the loss bigger. Say which case it is.

### Default alive (pre-profit ventures)
A separate test, not a unit metric. It needs five inputs: cash in the bank, monthly fixed costs, current monthly contribution, monthly growth rate of that contribution, and the months you are willing to plan for. The venture is default alive if, at current growth and costs, monthly contribution reaches monthly fixed costs before the cash runs out. If any input is missing, say the test cannot be run yet and ask for it - do not fill it from unit numbers.

### Service Business Specific
- **Utilization rate:** billable hours / available hours
- **Effective hourly rate:** project revenue / hours spent
- **Delivery margin:** (engagement price - cost to deliver) / engagement price

## Do the arithmetic with the calculator

When Python is available, run the numbers through `scripts/unit_math.py` instead of working them out in prose, and quote its output. A model doing arithmetic in a sentence is how a per-box cost ends up off by a few dirhams, and how a price for a 40 percent margin gets rounded down to one that gives 39.7 percent.

    python scripts/unit_math.py --currency AED batch --batch-cost 30 --hours 1 --hourly 40 --units 12 --waste 1 --pack-size 6 --packaging 2 --price 60
    python scripts/unit_math.py price --cost 44 --margin 40
    python scripts/unit_math.py breakeven --fixed 1200 --price 60 --variable 44
    python scripts/unit_math.py cac --marketing 300 --customers 4
    python scripts/unit_math.py payback --cac 75 --contribution 20 --lifetime 6
    python scripts/unit_math.py runway --cash 5000 --fixed 1000 --contribution 400 --growth 10

It never fills in a number you did not give it, and it says what a missing one leaves unknown. Without Python, do the same steps by hand and show every one.

## Pricing advice stays conditional

The costs give the lowest price that holds a margin. They do not give the price buyers will pay. Until the missing costs (delivery, platform and payment fees, waste, your time) and some evidence of what buyers pay are both in, say the price the costs need, label every other price as a test, and do not call a number a floor, a premium position or what the market will bear. Never say an unknown cost "fits in the buffer": an unknown is unknown. A price you suggest testing is also a money test, so it waits until the founder knows they may take money for this activity where they sell.

## Output Format

### Quick Calculation
```
NUMBERS
---
[The calculation, step by step]

WHAT THIS MEANS
[One to three sentences]

WATCH OUT FOR
[Assumptions that could change the answer]
```

### Full Model
```
MODEL: [What you're modeling]
---
ASSUMPTIONS
[List every assumption with its value]

CALCULATIONS
[Step by step, show the math]

SCENARIOS
Conservative: [numbers]
Base case: [numbers]
Optimistic: [numbers]

BOTTOM LINE
[What the numbers are telling you]
```

## Where the input numbers came from

The math is only as honest as what goes in. Any number that did not come from your own records carries a tier tag per `rules/research-integrity.md`: `[MEASURED: artifact + command]`, `[SOURCED: url, retrieved date]`, or `[ESTIMATE: assumption]`. An industry benchmark or a "typical" conversion rate is the dangerous kind: it either carries a live source or it becomes an ESTIMATE with the assumption written out.

Show both operands and the result on the same line where you can, so anyone can re-run it. The error that hides best is a cost table where nine rows reconcile and the tenth is off by 11 percent - it reads as a careful document right up until the buyer checks it.

Second pass before the model leaves your machine:

    python scripts/claims_check.py <the document>

## Rules

- Always show your work
- Use the founder's own currency. If none is given, ask once
- One currency and one period per calculation. If inputs mix currencies (AED and USD) or periods (monthly and yearly), convert explicitly with the rate or factor shown, or ask
- A missing input is labelled unknown, never filled in
- Round to reasonable precision. "$48K" not "$47,832.17"
- Flag assumptions explicitly
- If the user doesn't give enough numbers, ask. Don't guess.
- Outside numbers carry a tier tag per `rules/research-integrity.md`
- Simple hyphens (-) not em or en dashes
