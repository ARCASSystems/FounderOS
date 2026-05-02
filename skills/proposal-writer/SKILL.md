---
name: proposal-writer
description: >
  Creates consulting and service proposals for the founder. Use this skill when the user asks to "write a proposal", "create a quote", "draft a SOW", "scope of work", "put together a proposal", "pricing for", "engagement letter", or any variation of creating business proposals, quotes, scoping documents, or service agreements. Also trigger when the user describes a potential client engagement and needs it formalized. Reads `core/voice-profile.yml`, `core/brand-profile.yml`, and any relevant `context/companies/<client>.md` for engagement specifics.
allowed-tools: ["Read", "Write", "Edit"]
mcp_requirements: []
---

# Proposal Writer

You are writing a proposal for the founder. The proposal must reflect their voice, their brand, and the specifics of the prospect. It must not sound like a template.

## Before You Write

Read in this order:

1. `core/voice-profile.yml` - the founder's voice rules. If missing, fall back to the universal anti-AI baseline and warn the user.
2. `core/brand-profile.yml` - if present, governs any branded version of this proposal (PDF, DOCX). For plain-text proposals, this is optional.
3. `context/companies/<client>.md` if a relevant context file exists - prior research, scope conversations, the prospect's stated pain.
4. Any prior scoping notes the user points you at.

If a `your-deliverable-template` skill is available and this proposal is going out as a branded document, route through it for consistent visual identity.

If the user wants a plain-text proposal (email, Google Doc, plaintext), skip the brand step.

## Core Philosophy

- **Show the problem before the solution.** The prospect should see their situation reflected back accurately before you propose anything.
- **Translate symptoms to money.** Don't leave a pain point as a feeling. Connect it to a P&L line item, a hiring cost, a delay, a missed sale, a churned client. If a symptom appears in the proposal without a financial or operational translation, the proposal is incomplete.
- **Specificity builds trust.** Vague proposals lose. Name the roles, the processes, the timelines, the deliverables.
- **Price with confidence.** No apologetic pricing. No "we can discuss." State the investment clearly. If the founder genuinely needs to gather more information before pricing, scope the diagnostic phase and price that, not the full engagement.
- **Don't quote what you haven't diagnosed.** If the engagement has multiple phases, quote the first phase only. Subsequent-phase pricing comes after the first phase reveals what's actually needed.
- **Information ownership is the prospect's.** Add a line: "This document is yours regardless of whether we work together." It signals that the value is in the execution, not in the document.

## Currency Rule

Read the founder's identity or business context for their default currency. Use AED for UAE/GCC clients, USD for international, GBP for UK, EUR for Europe, INR for India - whatever matches the engagement. If unclear, ask the user before writing the price.

## Proposal Structure

```
PROPOSAL: [Engagement Title]
Prepared for: [Client Name, Company]
Prepared by: [Founder Name, Title - Company]
Date: [Date]

---

1. SITUATION
[2-3 paragraphs reflecting the prospect's current state. Show you understand the problem. Every symptom mentioned must connect to a financial or operational consequence. Mirror, not critique.]

2. WHY THIS COSTS MORE THAN IT LOOKS
[Translate 2-3 key symptoms into financial terms. Make the cost of inaction visible.]

3. WHAT WE'LL DO
Phase 1: [Phase name and duration]
-> [Deliverable 1]
-> [Deliverable 2]

[Subsequent phases described in scope terms only, not quoted. "Pricing for subsequent phases will be based on Phase 1 findings."]

4. WHAT YOU'LL HAVE WHEN WE'RE DONE
[Tangible outputs. Things they can hold, use, share with their team.]

5. TIMELINE
[Week-by-week or phase-by-phase breakdown.]

6. INVESTMENT
[Phase 1 pricing only. Clear amount. No "starting at" or ranges unless that's genuinely how the founder prices.]

7. WHAT WE NEED FROM YOU
[Client responsibilities. Time commitment. Access requirements.]

8. ENGAGEMENT TERMS
[Standard terms - see Engagement Terms section below.]

9. NEXT STEPS
[Initiation flow.]

---
Valid for 14 days from date of issue.

This document is yours regardless of whether we work together.
```

## Pricing Patterns

The founder may use different pricing approaches. Help them pick one that fits the engagement. Three common patterns:

**Fixed-fee phase pricing.** A clear number for the first phase. No hourly billing surprises. Best for diagnostic-style engagements or well-scoped work. Pair with a money-back-on-no-findings guarantee where appropriate.

**Reverse pricing (faster = higher).** Two or three options where shorter timelines cost more. Signals confidence and rewards urgency. Example: 1-week intensive at premium, 2-week standard at base. Use only if the founder can genuinely deliver faster with more focused attention.

**Retainer or part-time embedded.** Committed hours per week or month at a fixed rate. Best for ongoing advisory or fractional engagements. Be specific about what hours include and what counts as out-of-scope.

If the user hasn't told you which pattern to use, ask.

## Risk Reversal (Recommended)

If the engagement model supports it, include a guarantee tied to a measurable outcome - not a generic satisfaction guarantee. Examples:

- "No P&L outcomes identified in Phase 1? Full refund."
- "No working prototype delivered by week 4? You pay 50%."
- "If we don't hit [specific metric], we work to fix it on our time, not yours."

Tie the guarantee to something the prospect can verify. Avoid vague satisfaction promises.

## Engagement Terms (Recommended Standard Block)

Adapt to the founder's positioning. A common pattern:

### NDA Framing
The CLIENT initiates the NDA / NCC / NCA. Frame it as protecting THEIR data, not as the founder's requirement:

"During this engagement, you'll be sharing sensitive information about your suppliers, pricing, customers, and internal operations. We ask that you initiate a mutual NDA to safeguard your proprietary information."

This positions the founder as professional and the prospect as the party with information to protect.

### Information Ownership
"This document is yours regardless of whether we work together."

Include on every proposal. The value is in the execution, not in the proposal.

### Founder-specific clauses
The founder may have non-negotiable values they want surfaced in every engagement (no headcount-reduction clauses, ethical-sourcing clauses, exclusivity terms, etc.). If `core/identity.md` or `rules/operating-rules.md` calls these out, include them. If unclear, ask the founder which standard clauses they always include.

## Initiation Flow

Include in Next Steps. A typical flow:

1. Email intent to proceed to [founder's email]
2. Client sends mutual NDA / NCC / NCA
3. Both parties sign
4. Account details shared
5. Payment within 48 hours
6. Engagement begins the following week

Adjust based on the founder's actual operating cadence.

## Writing Rules

- Simple hyphens (-) not em or en dashes
- Arrows (->) for deliverable lists
- No jargon unless the client speaks that language
- No superlatives ("best-in-class", "world-class")
- No filler paragraphs about the founder's history - the proposal is about the prospect
- Numbers and specifics wherever possible
- Follow `your-voice` and the universal anti-AI baseline for all written content

## What to Ask the User

If context is thin, ask:
1. Who is this for? (Name, company, size, industry)
2. What problem are you solving for them?
3. What's the scope? Phase 1 only, or full engagement?
4. Any specific timeline discussed?
5. What pricing pattern - fixed phase, reverse, retainer?
6. Currency?
7. Has a discovery or scoping conversation already happened? Where are those notes?

If the founder hasn't specified pricing, propose one number based on the work involved and ask them to confirm before producing the final document. Never quietly invent prices.

## Self-check before delivery

1. Does the SITUATION section sound like the prospect could read it and say "yes, that's us"?
2. Are the costs of inaction quantified, not implied?
3. Are deliverables specific and tangible?
4. Is the price stated clearly without softening language?
5. Did you apply the founder's voice? (No corporate-AI tone.)
6. No banned words, no em dashes, no rule of three?
7. Does the proposal close with a clear next step the prospect can take in under 5 minutes?
