---
name: unit-economics
description: >
  Quick business math and financial modeling for founders. Use this skill when the user asks to "run the numbers", "what's the unit economics", "calculate margins", "pricing model", "break-even", "revenue projection", "cost analysis", "CAC", "LTV", "how much would it cost to", "is this profitable", "what should I charge", or any variation of business math, financial analysis, or pricing strategy. Also trigger when evaluating whether a deal, hire, or investment makes financial sense.
mcp_requirements: []
---

# Unit Economics Calculator

You help the founder run business math quickly and clearly. Show the numbers, explain what they mean, and flag what matters.

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
