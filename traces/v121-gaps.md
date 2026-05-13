---
trace: v121-gaps
version: 1.21.0
date: 2026-05-14
purpose: Gap synthesis from Maya (B2C) and Dev (ops-not-founder) traces.
---

# v1.21 Gap Synthesis

## Maya gaps observed

**M1 - CRM question assumes a sales pipeline, not a subscriber base.**
The setup wizard's tool-stack question includes "CRM" as a category (HubSpot, Airtable, etc.).
For a B2C founder, the relevant construct is "audience" or "subscriber list" (Mailchimp,
Klaviyo, ConvertKit), not a sales CRM. Maya would answer "none" to the CRM question even
though she actively manages 8,000 subscribers. The wizard has no path for "my CRM is my
email platform."

**M2 - Menu does not surface the user's declared primary channel.**
Maya declared Instagram as her primary marketing channel during setup. The menu skill scores
capabilities based on log history and state, but does not weight declared channel preference
from setup. After setup with no log history, `linkedin-post` surfaced before `instagram-caption`
despite Instagram being Maya's primary channel. A founder who declares their channel in setup
should see that channel's skill in their first menu pass.

**M3 - Buyer-language questions work well; no gap.**
Q7 and Q8 of the voice interview ("buyer first sentence," "buyer phrases") were answered
naturally by Maya despite the "buyer" framing mapping to a consumer, not a B2B customer.
Maya translated without friction. No patch needed.

## Dev gaps observed

**D1 - "Founder OS" branding creates a mild authority confusion for operator-not-founder users.**
The product's name and framing ("for founders", "Founder OS", wizard phase headers like
"your business") assume the operator is the business owner. Dev flagged this immediately:
"I'm not the founder though." The wizard did not acknowledge this or adjust its framing.
The files created say "your business" when Dev's correct framing is "Raj's business."
The skills work, but the framing creates a small ongoing context mis-match: Dev is using
a tool designed for someone with ownership authority he does not have.

**D2 - Buyer-language in setup is less useful for ops-not-founder users.**
The three positioning questions (0.2.5) generated buyer-persona data that Dev explicitly
does not control or use. The data got captured accurately, but it belongs to Raj and the
sales team. Future skill outputs (email-drafter, proposal-writer) may pull this data and
produce outputs in a voice and pitch that Dev would not be the one sending. This is not a
crash but a context-mismatch that could confuse.

**D3 - Weekly-review balance check hardcodes founder perspective.**
The weekly-review skill contains a "Marketing/Sales/Delivery Balance Check" that checks
whether the founder is selling enough vs. building. The check ends with "If Delivery is
dominating and Sales is under 40%, flag it: 'You're building when you should be selling.'"
For Dev, this check is not applicable - he has no sales responsibility. The check would
fire incorrectly if Dev ever runs weekly-review, calling his entirely ops work "too much
delivery." This is a behavioral gap, not just cosmetic.

**D4 - Decision-framework defaults to first-person ownership framing.**
The decision-framework skill assumes the operator is the decision-maker. Dev tracks decisions
on behalf of Raj. When Dev asks "help me think through the Speedex trial," the skill will
frame the recommendation as if Dev is making the call. Dev would actually need to frame this
as "a recommendation for Raj." Minor framing gap that does not block use.

**D5 - Voice interview and SOP-writer work cleanly for operator-not-founder users; no gap.**
Q9-Q12 produced strong anti-example signal from Dev despite him not being a marketing-voice
user. The SOP-writer used Dev's snapshot context correctly. The queue was persona-agnostic.
No patches needed for these surfaces.

## Patch decisions

**M1 - CRM question assumes a sales pipeline**
DEFER TO v1.22 - Fixing this requires adding a branch to the setup wizard's tool-stack
question: a fourth category for "audience/subscriber list" tools alongside the existing
CRM options. This is a wizard refactor that touches the setup skill, the stack.json schema,
and potentially the email-drafter skill's stack-resolution logic. More than 4 file edits
likely if done properly.

**M2 - Menu does not weight declared primary channel**
DEFER TO v1.22 - Fixing this requires `scripts/menu.py` to read the declared marketing
channel from the founded's setup answers (currently not stored in a structured field) and
weight the matching skill higher. Requires a setup-wizard change to persist `primary_channel`
to a readable field AND a menu-engine change to read it. Two-part change, but the setup
schema change touches multiple files. Defer.

**D1 - "Founder OS" branding creates authority confusion for operators**
ACCEPT - The OS is intentionally named and framed for founders and owners. Operators who
use it are a secondary case - the product works for them but is not positioned for them.
Rebranding or adding operator-specific paths is a product decision beyond the scope of
v1.21. The trace evidence shows the OS is usable for operators; the framing is just
founder-centric by design.

**D2 - Buyer-language less useful for ops-not-founder**
ACCEPT - Same reasoning as D1. The buyer-language data is captured accurately. Ops-not-founder
users who set up FounderOS will have some context fields that are less relevant to them.
The system does not fail; it is just slightly mis-calibrated for this persona. Accept as
a known limitation of the single-archetype setup flow.

**D3 - Weekly-review balance check hardcodes founder perspective**
PATCH IN v1.21 - The fix is one sentence: add a guard condition that skips the
Marketing/Sales/Delivery check if `core/identity.md` contains a "not a founder" signal
OR if the operator's declared role is non-owner. Simpler: make the check conditional on
whether the operator owns sales responsibility. One file edit: `skills/weekly-review/SKILL.md`.

**D4 - Decision-framework defaults to ownership framing**
ACCEPT - The decision-framework skill is designed for the operator making a call. An
ops-manager using it to structure a recommendation for their boss can adapt the output
framing without the skill needing to know this. Accept as user responsibility.

---

*PATCH IN v1.21 total: 1 file edit (skills/weekly-review/SKILL.md - D3 guard).*
*Well within the 4-file-edit cap.*
