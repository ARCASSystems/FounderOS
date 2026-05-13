---
trace: v121-dev
persona: Dev
version: 1.21.0
date: 2026-05-14
purpose: Multi-archetype coverage. Daily-ops manager at a 15-person logistics firm. NOT a founder.
name_check: "Dev" searched repo pre-trace - 0 standalone-token matches in tracked files. Name clear.
---

# Trace: v1.21 - Dev

Dev is the daily-operations manager at a 15-person Mumbai-based logistics company. Three years
in the role. Reports to the founder (who is NOT Dev). Does not own P&L. Owns the weekly operations
meeting and tracks decisions on behalf of the founder. Comfortable with markdown, not a developer.
Wants an OS that surfaces what the team committed to last week and what slipped.

---

## 1. Setup Wizard Run

**Wizard:** "Let's set up your Founder OS. First - what's your name, and what do you do?"

**Dev:** "I'm Dev. I run daily operations at a logistics company here in Mumbai - 15 people, we
move last-mile freight. I'm not the founder though. I report to him. I want this to help me
track what I committed to and what the team said they'd do."

*[ANNOTATION: Dev immediately flags "I'm not the founder." The wizard's name is "Founder OS"
and its description throughout says "for founders." This is the most significant framing tension.
The wizard does not crash - it asks follow-up questions - but it does not acknowledge the
"not a founder" statement or adjust its framing. It proceeds as if Dev is the decision-maker.]*

**Wizard:** "Got it. For this company - name, what it does, and who else is involved?"

**Dev:** "Quickmove Logistics. Last-mile delivery in Mumbai and Pune. The founder is Raj - he owns
the business. I manage the 12-person ops team. There are also three sales people who report to Raj."

**Wizard (0.2.5 Positioning - Q1 of 3):** "Who is your ideal buyer? Describe the person
you most want to sell to."

**Dev:** "I don't sell. Raj and the sales team handle that. Our buyers are e-commerce companies
and D2C brands who need reliable last-mile."

*[ANNOTATION: Q1 assumes Dev is the person selling. He is not. He answered honestly - "I don't
sell" - but the wizard has no branch for this. It continues with the positioning questions as if
the answer is still relevant for an operator-not-founder user. The setup will populate
`buyer_language` fields that Dev will never use.]*

**Wizard (0.2.5 Q2):** "What is the specific moment when your buyer realizes they have the
problem you solve?"

**Dev:** "I'll answer for the company even though I don't close deals - it's when a courier fails
a delivery and the customer is the last to know. That's our pitch."

*[ANNOTATION: Dev adapts. He knows the answer but frames it as "for the company, not for me."
The wizard captured the answer but does not surface that this context mismatch exists. Future
skills (email-drafter, proposal-writer) will load buyer phrases that Dev wrote on behalf of
a sales team he does not control.]*

**Wizard (0.2.5 Q3):** "What is the one thing they would say about you three months after
becoming a customer?"

**Dev:** "Our route accuracy went up 15%. And the team actually know what to do when something
goes wrong instead of calling me at 9pm."

**Wizard (tools Q):** "Which tools do you use?"

**Dev:** "Google Sheets for ops tracking. Gmail. WhatsApp for team. No Notion. No automation
platform - everything is manual or in Sheets."

**Wizard (priorities):** "What are the MUST DOs for this week?"

**Dev:** "Renegotiate the courier contract before it auto-renews Friday. Fix the daily-ops doc
template the team keeps drifting from. Write up the Q3 logistics review for Raj."

*[ANNOTATION: Dev's priorities are clearly ops-manager tasks, not founder tasks. The system
handles them fine - they populate correctly into cadence. But the context files now say
"your business" and "your clients" in places where Dev would say "Raj's business" and
"Raj's clients." This is cosmetic but could create confusion in skill outputs.]*

*Setup completes. The biggest gap: the system calls itself a "Founder OS" and frames everything
around the operator as the business owner. Dev is not the owner. The files are still useful
to him but several will contain buyer-persona data he does not control and client-relationship
context he tracks on someone else's behalf.*

---

## 2. Voice Interview Run (Phase 1 + 2 + 2.5, Q1-Q12)

**Sample 1 (pasted - Slack message to the ops team):**
"Team - Friday route audit found 4 delays, 3 from the same courier partner (Skyline). Two of
those were no-update to customer. Escalating to Raj and opening a performance review. By EOD
Monday I need each of you to pull your Skyline jobs from last week and flag any gaps. Use the
ops-doc template, not a verbal. Thanks."

**Sample 2 (pasted - weekly ops meeting notes excerpt):**
"OPS MEETING 2026-05-09

Committed last week:
- Ritu: audit Pune routes for time-window accuracy. Status: done.
- Arun: draft new courier escalation flow. Status: SLIPPED. Rescheduled to this week.
- Dev: set up Q3 review template. Status: in progress.

This week:
- Ritu: [...]"

**Sample 3 (pasted - note to Raj on a vendor decision):**
"Raj - quick update on the Speedex situation. They've come back with a rate 8% below Bluedart.
I'd recommend we trial them on Pune outbound (lower stakes) before committing city-wide.
Risk: their customer comms are weaker - I've logged two complaints this month. Happy to
draft the trial structure if you want to move forward."

**Q1 (Sentence rhythm):** "Short and punchy, longer and building, mixed up, or verse-like?"

**Dev:** "Short. Direct. I don't have time for long sentences when I'm writing ops notes.
If it takes more than one sentence to say it, I break it into a list."

*Mapped to: short_hits.*

**Q2 (Opening style):** "How do you open a piece?"

**Dev:** "Status. 'Here's what happened.' Or 'Here's what we committed to and here's the gap.'"

*Mapped to: observation (status-first).*

**Q3 (Closing style):** "How do you end?"

**Dev:** "I always close with the next action. Who is doing what by when. If I don't close
with that, the thing just floats."

*Captured: weight (action-oriented close).*

**Q4 (Person + contractions):** "I/you/both? Contractions?"

**Dev:** "'We' more than 'I' when I'm talking to the team. 'I' when I'm reporting up to Raj.
Contractions - sometimes. I'm more formal in written docs than in Slack."

*Mapped to: mixed (we for team, I for upward reports), contractions: sometimes.*

**Q5 (Vocabulary):** "Words you reach for? Words you hate?"

**Dev:** "Words I use: 'committed,' 'slipped,' 'gap,' 'by EOD,' 'escalate.' Words I hate:
'synergy,' 'circle back,' 'take this offline,' 'low-hanging fruit.'"

*Captured. Anti_examples.aesthetic_crimes updated.*

**Q6 (Quirks):** "Anything you do on purpose that grammar rules would flag?"

**Dev:** "I write dates like 2026-05-09 and times like EOD. And I use ALL CAPS for status
words like SLIPPED, DONE, BLOCKED. I want people to see the status immediately."

*Captured: ISO dates, EOD/EOW, ALL CAPS status words.*

**Q7 (Buyer first sentence):** "When your buyer describes their problem..."

**Dev:** "That's still Raj's world. But if I'm being asked for what the customer says: 'Our
customers are complaining about late deliveries and we can't tell them why.'"

*[ANNOTATION: Q7 is slightly awkward for Dev but he adapts. Captured as-is. The buyer-language
data will be less relevant for Dev's own writing but still useful if he ever drafts outreach.]*

**Q8 (Buyer phrases):** "What phrase does your buyer say that makes you nod?"

**Dev:** "'We need real-time visibility.' Also: 'Your team promised X and delivered Y.'"

*Captured.*

**Q9 (Contrarian take):** "One belief most people in your field would push back on."

**Dev:** "Meeting notes are useless if they don't show who slipped. Most people write meeting
notes to document what was discussed. I write them to document what was promised."

*[ANNOTATION: Q9 produced strong signal even for a non-marketing-voice user. The question
is universal. No gap.]*

**Q10 (Aesthetic crime):** "One phrase or structure that makes you cringe."

**Dev:** "'We'll circle back on this.' It means: nobody owns this and it will never happen."

*Captured as aesthetic_crimes.*

**Q11 (Red flag):** "Tell for fake expertise?"

**Dev:** "When someone presents a deck without numbers. And when the numbers they do show
don't have a comparison point. '85% delivery success' - compared to what?"

*Captured as red_flags.*

**Q12 (Anti-example pairs):**

**Dev:**
"Bad: 'We'll take this offline and align on next steps.'
Good: 'Dev and Arun own this. Friday EOD.'
Rule: End every action with a name and a date, not a process word.

Bad: 'There were some challenges last week.'
Good: 'Three deliveries slipped. Two from the same partner.'
Rule: Name the thing. Give the number.

Bad: 'Going forward, we should improve our courier selection process.'
Good: 'Skyline is under performance review. Trial Speedex on Pune routes this week.'
Rule: No 'going forward.' What is happening, starting when, owned by who."

*Voice profile complete. Dev's voice is highly actionable and accountability-oriented.
Q9-Q12 produced strong anti-example signal despite Dev not being a marketing-voice user.
The voice interview works for operator-not-founder users.*

---

## 3. Menu Run

**Invocation:** "show me what you can do"

**Menu output (simulated from scripts/menu.py against Dev's state):**

```
Here is what I can do right now based on your state:

1. Write an SOP for your team (or run /founder-os:sop-writer)
   Why now: no SOP created yet, you mentioned a daily-ops doc template gap.

2. Run my weekly review (or run /founder-os:weekly-review)
   Why now: weekly-commitments.md is fresh, no retro logged.

3. Prep for your meeting with Raj (or run /founder-os:meeting-prep)
   Why now: no meeting prep logged this week.

4. Log a decision (say "log this decision")
   Why now: context/decisions.md is empty.

5. Add things to the queue (or run /founder-os:queue)
   Why now: queue is empty, you have committed items from setup.
```

*[ANNOTATION: The menu output is useful for Dev. SOP-writer correctly surfaced first given
the declared gap. No "draft a proposal" or "write a LinkedIn post" in top 5 - the menu
engine did not hard-push B2B or content skills.]*

*[ANNOTATION: "meeting-prep" suggests "your meeting with Raj" - this implies Dev is the
one called into the meeting. Accurate for his context. No gap here.]*

*[ANNOTATION: "log a decision" surfaced correctly. Dev tracks decisions for the team - this
is directly useful. However the decision-framework skill defaults to "the founder's decision"
language. For Dev, the useful framing is "decision Raj needs to make" not "your decision."
This is a minor framing gap in decision-framework, not in the menu.]*

---

## 4. SOP Writer Run (replacing LinkedIn for Dev)

**Invocation:** "Write an SOP for: standardize how the warehouse team flags missing items
on the daily ops doc"

**SOP-writer output (applying Dev's voice profile, with snapshot context read):**

---

**SOP: Missing-Item Flags on the Daily Ops Doc**
Owner: Warehouse leads (Ritu and Arun)
Last updated: 2026-05-14

---

PURPOSE

When items are missing from a delivery batch, the warehouse team flags it in the daily ops
doc. This SOP ensures the flag is consistent, visible, and actionable before the courier
picks up.

TRIGGER

Flag any missing item before the courier departs. Do not flag after departure.

STEPS

1. Open the daily ops doc (link in Slack #ops-general pinned messages).
2. Find the row for the affected shipment. Use the order ID from the manifest.
3. In the "Status" column, type: MISSING - [item name] - [quantity].
4. In the "Owner" column, enter your name.
5. In the "Next action" column, enter one of: HOLD (stop the courier), PARTIAL-SHIP
   (send what we have, flag the customer), ESCALATE (Dev to decide).
6. Tag @Dev in Slack #ops-alerts. Paste the row link.

RULES

- "MISSING" in capitals only. No "item shortage", no "incomplete", no variations.
- Flag before courier pickup. After pickup, use the late-flag SOP instead.
- If you are unsure whether to HOLD or PARTIAL-SHIP, default to HOLD and tag Dev.

WHAT NOT TO DO

- Do not call or WhatsApp Dev first. Flag the doc first, then tag.
- Do not leave the Status column blank and tell someone verbally.

---

*[ANNOTATION: The SOP output reflects Dev's voice accurately - actionable, no soft language,
ALL CAPS for status words, clear escalation path. The snapshot-read context (new in v1.21)
correctly pulled in the "daily-ops doc template" must-do from setup. The draft shows the
week's priority, not a generic SOP.]*

*[ANNOTATION: No "founder" assumptions in the SOP output. The SOP writer adapts to the user's
context without requiring a "founder" framing. The skill works cleanly for a non-founder user.]*

---

## 5. Queue Run

**Invocation:** "add to queue: renegotiate courier contract"

**Skill response:** "Added to backlog: renegotiate courier contract."

**Invocation:** "add to queue: fix the daily-ops doc template"

**Skill response:** "Added to backlog: fix the daily-ops doc template."

**Invocation:** "add to queue: draft the Q3 logistics review for Raj"

**Skill response:** "Added to backlog: draft the Q3 logistics review for Raj."

**Invocation:** "start: renegotiate courier contract" (ACTIVE = 0, should succeed)

**Skill response:** "Started: renegotiate courier contract. ACTIVE is now 1/3."

**Invocation:** "start: fix the daily-ops doc template" (ACTIVE = 1, should succeed)

**Skill response:** "Started: fix the daily-ops doc template. ACTIVE is now 2/3."

**Invocation:** "start: draft the Q3 logistics review" (ACTIVE = 2, should succeed)

**Skill response:** "Started: draft the Q3 logistics review. ACTIVE is now 3/3."

**Invocation:** "add to queue: brief the Pune team on the new route audit format"

**Skill response:** "Added to backlog: brief the Pune team on the new route audit format."

**Invocation:** "start: brief the Pune team" (ACTIVE = 3 - gate should fire)

**3-item gate fires (verbatim):**

> ACTIVE is at capacity (3/3). Which of these gets paused (back to BACKLOG) or
> killed (removed entirely) before this one starts?
>
> Current ACTIVE items:
> - [2026-05-14] renegotiate courier contract | next action: TBD | source: inbound
> - [2026-05-14] fix the daily-ops doc template | next action: TBD | source: inbound
> - [2026-05-14] draft the Q3 logistics review for Raj | next action: TBD | source: inbound

**Dev:** "Park the Q3 review - Raj doesn't need it until end of month. Start the Pune team brief."

**Skill response:** "Parked: draft the Q3 logistics review for Raj. Back in BACKLOG.
Started: brief the Pune team on the new route audit format. ACTIVE is now 3/3."

*Gate fires correctly for a non-founder user. Dev's items - all ops-manager tasks - move
through the queue without any "founder" assumption in the skill behavior. The queue is
persona-agnostic.*
