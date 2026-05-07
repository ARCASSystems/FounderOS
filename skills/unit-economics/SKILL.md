---
name: unit-economics
description: >
  Quick business math and financial modeling for founders. Use this skill when the user asks to "run the numbers", "what's the unit economics", "calculate margins", "pricing model", "break-even", "revenue projection", "cost analysis", "CAC", "LTV", "how much would it cost to", "is this profitable", "what should I charge", or any variation of business math, financial analysis, or pricing strategy. Also trigger when evaluating whether a deal, hire, or investment makes financial sense.
mcp_requirements: []
---

# Unit Economics Calculator

You help the founder run business math quickly and clearly. Show the numbers, explain what they mean, and flag what matters.

## Brain context (default)

Before producing output, read `brain/.snapshot.md` if it exists.

If the snapshot is missing, run:

    python scripts/brain-snapshot.py --write

Then read it. If the snapshot script is also missing (older install), proceed using only the profile files. Do not block.

The snapshot tells you what flags are open, what the user is working on this week, and what the latest staleness state is. Apply this context to your output where it is relevant. Do not surface every snapshot field in every output - use judgment. For unit economics, recent decisions tell you which pricing or hiring choices are off the table, and open flags often signal a stalled commercial decision the math can unblock.

## Core Metrics

### Revenue Math
- **MRR:** customers x average revenue per customer
- **ARR:** MRR x 12
- **Revenue per employee:** total revenue / headcount
- **Output per worker:** revenue generated per team member

### Customer Economics
- **CAC:** total sales + marketing spend / new customers acquired
- **LTV:** average revenue per customer x average customer lifespan
- **LTV:CAC ratio:** LTV / CAC (healthy is 3:1 or better)
- **Payback period:** CAC / monthly revenue per customer (in months)

### Profitability
- **Gross margin:** (revenue - direct costs) / revenue x 100
- **Net margin:** (revenue - all costs) / revenue x 100
- **Break-even:** fixed costs / (price - variable cost per unit)

### Service Business Specific
- **Utilization rate:** billable hours / available hours
- **Effective hourly rate:** project revenue / hours spent
- **Delivery margin:** (engagement price - cost to deliver) / engagement price

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

## Rules

- Always show your work
- USD by default unless the user specifies another currency
- Round to reasonable precision. "$48K" not "$47,832.17"
- Flag assumptions explicitly
- If the user doesn't give enough numbers, ask. Don't guess.
- Simple hyphens (-) not em or en dashes
