<!-- mirror: keep section headers identical to the private business-context.template.md -->
<!-- this is the public (generic) copy. examples are intentionally vendor-neutral. -->

---
template:
 id: business-context.template
 version: 1
 variant: public
 created: 2026-04-25
 refresh_cadence: quarterly (sections 11-12) / annual (sections 1-10)
 must_fill_for_useful_output: [1, 2, 3, 4, 5, 6, 7]
 mature_stage_optional: [8, 9, 10]
 quarterly_refresh: [11, 12]
---

# Business Context Template

This file gives your AI assistant the operating context for your business so its responses are grounded in what you actually do, not generic advice. Fill it once. Refresh per the cadence above.

## How to use this file

1. Copy this file to `companies/<your-company-slug>-business.md`.
2. Replace every `[FILL]` with the real answer. Use `[SKIPPED]` if the question genuinely doesn't apply. Use `[PENDING]` if you don't know yet but plan to.
3. Update the per-section `Last refreshed` date when you change anything inside that section.
4. The `business-context-loader` skill scans this file and tells you what's missing, what's stale, and what action to take next based on what's filled.

## Marker legend

- `[FILL]` - not yet answered, blocking
- `[PENDING]` - answer not known yet, will be filled when known
- `[SKIPPED]` - does not apply to this business (e.g. brand rules for a pre-launch company)
- `[STALE]` - content is older than the refresh cadence, needs review

---

## 1. Identity & Stage

**Last refreshed:** [FILL - YYYY-MM-DD]

- **Company name:** [FILL]
- **Legal entity status:** [FILL - registered / pre-licence / dba / subsidiary of X]
- **Founders + equity split:** [FILL - name : % : role]
- **Headcount today:** [FILL]
- **What the company is, in one paragraph (no jargon):** [FILL]
- **Where it is now (month-1 / year-1 / year-3 picture):** [FILL]

## 2. Problem & Thesis

**Last refreshed:** [FILL - YYYY-MM-DD]

- **What problem does the business solve?** [FILL]
- **Why is the existing solution wrong / inadequate?** [FILL]
- **What is the underlying belief that makes this business different from competitors?** [FILL]

## 3. Value Model

**Last refreshed:** [FILL - YYYY-MM-DD]

- **What does the buyer pay for?** [FILL - information / execution / outcome / access / certainty]
- **Pricing posture:** [FILL - premium / mid-market / discount]
- **Pricing model:** [FILL - reverse pricing / standard / subscription / retainer / one-off / mixed]
- **What's free vs paid?** [FILL]

## 4. ICP (Ideal Customer Profile)

**Last refreshed:** [FILL - YYYY-MM-DD]

- **Who buys this?** [FILL - one-paragraph description of the ideal buyer]
- **Firmographic axis:** [FILL - primary axis is headcount / revenue / sector / geography]
- **Size range:** [FILL]
- **Sector / industry:** [FILL]
- **Geography:** [FILL]
- **Buyer archetype (behaviour, what they say, what they don't say):** [FILL]
- **Symptom-to-pain mapping (what they report → what's actually broken → cost in their P&L):** [FILL]
- **Anti-ICP (who is NOT a fit, even if they ask):** [FILL]

## 5. Offer & Delivery

**Last refreshed:** [FILL - YYYY-MM-DD]

- **Offer tiers (name + one-line description for each):** [FILL]
- **Engagement structure (how does a project flow from contact to close-out?):** [FILL]
- **Phases (what are the named phases of delivery?):** [FILL]
- **What's in scope for each tier:** [FILL]
- **What's explicitly out of scope:** [FILL]
- **Guarantees / risk reversal (do you have any? what triggers them?):** [FILL]

## 6. Pricing

**Last refreshed:** [FILL - YYYY-MM-DD]

- **Anchor numbers (typical price for typical engagement):** [FILL]
- **Floor (minimum below which you walk away):** [FILL]
- **Ceiling (maximum you'd quote without partner involvement):** [FILL]
- **How pricing scales (with what variable):** [FILL - company size / scope / urgency / complexity]
- **Payment terms:** [FILL - % up-front / milestones / net-30]
- **Currency default:** [FILL]

## 7. Market Position

**Last refreshed:** [FILL - YYYY-MM-DD]

- **Direct competitors (named):** [FILL]
- **Adjacent threats (categories that could eat the lunch):** [FILL]
- **Differentiators (5-15 specific anchors that competitors don't have):** [FILL]
- **Positioning sentence (one line, no jargon):** [FILL]
- **What the buyer would Google to find this category:** [FILL]

---

## 8. Operating Cadence

**Last refreshed:** [FILL - YYYY-MM-DD]

_Section 8 onwards is for businesses past month-3. If pre-launch, leave as `[PENDING]`._

- **Sales cycle length (first contact → signed agreement):** [FILL]
- **Delivery cycle length (signed → close-out):** [FILL]
- **Cash conversion cycle (signed → cash in bank):** [FILL]
- **Team size required per active engagement:** [FILL]
- **How many active engagements can run in parallel?** [FILL]

## 9. Brand Rules

**Last refreshed:** [FILL - YYYY-MM-DD]

_Skip this section if the business is pre-launch. Fill it as the brand matures._

- **Voice / tone:** [FILL]
- **Banned words (this business never uses):** [FILL]
- **Visual anchors (colours, fonts, logo treatment) - only if mature:** [FILL]
- **Document templates (where they live, what they look like) - only if mature:** [FILL]
- **Naming discipline (any words that must be used precisely):** [FILL]

## 10. AI / Tooling Stance

**Last refreshed:** [FILL - YYYY-MM-DD]

- **How does the business use AI publicly (in marketing, positioning, claims)?** [FILL]
- **How does the business use AI internally (operations, delivery)?** [FILL]
- **What's banned (e.g. AI-generated client deliverables without review)?** [FILL]
- **What's required (e.g. specific AI tool for all drafting)?** [FILL]
- **Tool stack (the canonical stack the business runs on):** [FILL]

---

## 11. Current State Snapshot (refresh quarterly)

**Last refreshed:** [FILL - YYYY-MM-DD]

Three lists. Be specific. No platitudes.

- **What's working (3-5 items):** [FILL]
- **What's broken (3-5 items):** [FILL]
- **What's blocking growth right now (1-3 items):** [FILL]

## 12. Automation Map (refresh quarterly)

**Last refreshed:** [FILL - YYYY-MM-DD]

This section is the bridge between the business and the systems that run it.

- **Currently automated workflows (process : tool : owner):** [FILL]
- **Currently manual workflows that should be automated (process : pain level : tool candidate):** [FILL]
- **Handoffs that drop balls (between whom : how often : cost of the drop):** [FILL]
- **Data sources (where the canonical data lives):** [FILL]
- **Tool stack (full inventory):** [FILL]
- **Immediate automation needs (next 30 days):** [FILL]
- **Eventual automation needs (next 6 months):** [FILL]

---

## Refresh log

Append a one-line entry every time any section changes. Keep the most recent 10 entries.

- [YYYY-MM-DD] [section number] [what changed in one sentence] - [who edited]

---

## End of template

If you're reading this in a filled instance and any section above is `[FILL]`, run the `business-context-loader` skill and it will tell you what to do next.
