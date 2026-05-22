<!-- mirror: keep section headers identical to the private prospect-context.template.md -->
<!-- this is the public (generic) copy. examples are intentionally vendor-neutral. -->
<!-- This template is for companies you DO NOT run. For operator companies see `business-context.template.md`. -->
<!-- Wikilink note: reference prospect files by full path (`[[companies/prospects/<slug>]]`) so wikilinks do not collide with operator files at `companies/<slug>-business.md`. -->

---
template:
 id: prospect-context.template
 version: 1
 variant: public
 created: 2026-05-22
 refresh_cadence: as-touched
---

# Prospect Context Template

Lightweight record for a company you are watching, selling to, or otherwise tracking. Unlike `business-context.template.md`, this file does not require every field to be useful. Fill what you know. Add fields as you learn them.

## How to use this file

1. Copy this file to `companies/prospects/<prospect-slug>.md` (the `prospect-init` flow does this for you).
2. Fill fields you already know. Leave the rest blank or write `unknown`. The template is intentionally light - you do not have to complete every field for the file to be useful.
3. Append to **Notes** every time you learn something. Update **Last touched** with the date.
4. When the relationship moves from prospect to client, copy the relevant content into `companies/<slug>-business.md` (operator path) or keep this file as the record of how the relationship started.

---

## Identity

- **Company name:**
- **Sector / industry:**
- **Headcount range:** (e.g. 10-50, 50-200, 200+)
- **Geography:**
- **Website / primary public surface:**

## Why you are tracking them

One paragraph. What made them worth tracking? A specific event, a referral, a piece of work they shared publicly, a fit against your ICP. Be concrete.

## Current relationship

- **Stage:** (cold / warm / engaged)
- **Last touched:** (YYYY-MM-DD)
- **Channel:** (e.g. LinkedIn, email, in-person, mutual contact)
- **Owner on your side:** (you / a teammate / unassigned)

## Fit signals

- **Matches your ICP?** (yes / partially / no - and why)
- **Anti-ICP?** (yes / no / unclear - flag if this company looks attractive but violates an anti-ICP rule from your operator business-context)
- **Source of intel:** (where the information here came from - a meeting, a deck, public sources, a referral)

## Notes

Append entries as you learn. Most recent on top.

- YYYY-MM-DD - one line on what changed, with `[[raw/<source>]]` reference if a source backs it.

---

## End of template
