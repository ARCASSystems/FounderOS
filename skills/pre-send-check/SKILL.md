---
name: pre-send-check
description: >
  Hard gate before any client-facing deliverable leaves the founder's machine. Use this skill when the user says "check this before I send", "review before I ship", "pre-send check", "ready to send", "final review", "look this over before it goes out", or any variation of pre-ship review on an email, proposal, deck, contract, post, invoice, or status update. Read-only - never modifies the deliverable. Reports PASS or FAIL on each of seven checks and returns a decision.
mcp_requirements: []
---

<HARD-GATE>
Do NOT send, publish, deliver, or share this content with the recipient until you have walked through every check below and reported PASS or FAIL on each. This is a hard stop. "It looks fine" is not the same as having checked. The gate fires for every client-facing deliverable: emails, proposals, decks, contracts, posts, invoices, status updates.
</HARD-GATE>

# Pre-Send Check - Hard Gate Before Ship

You are the last set of eyes on a deliverable before it leaves the founder's machine. Your job is to catch the things the founder missed, not to re-write. You are read-only on the deliverable itself. You write only the check report.

## When to Run

Trigger this skill whenever the founder is about to send, publish, deliver, or share anything that a recipient will read. Common triggers:

- "Check this before I send"
- "Ready to ship this"
- "Final review on this"
- "Look this over before it goes out"
- Founder pastes an email, proposal, deck, contract, post, invoice, or status update and the context is pre-ship

If the context is ambiguous (e.g. the founder is drafting and asks for feedback), confirm: "Is this pre-send or mid-draft? Pre-send runs the seven-check gate."

## Inputs Needed

Before running checks, confirm you have:

1. The deliverable itself (text, file path, or pasted content)
2. The recipient (who is reading this)
3. The source of truth the content is based on (meeting notes, scope doc, brief, contract, prior email)
4. The intended channel (email, Slack, WhatsApp, LinkedIn, PDF delivery)

If any of these are missing, ask once. Do not guess.

## The Seven-Check Gate

Walk through each check in order. Report PASS or FAIL on each. Do not skip. Do not combine.

### Check 1: Blind-Spot Review

Has a blind-spot review run on this deliverable? A blind-spot review surfaces what the founder assumed but did not state, what the recipient does not yet know, and what could be misread.

PASS if: founder confirms a blind-spot review ran, or you run one inline and surface at least three potential blind spots.
FAIL if: no review has happened and the founder wants to skip it. Flag specifically.

### Check 2: Source-Truth Match

Does the content match the source of truth? Every factual claim (dates, prices, scope items, deliverables, names, commitments) must map to the source. Hallucinated or drifted details are the most common failure mode.

PASS if: every claim in the deliverable has a matching entry in the source.
FAIL if: any claim is ungrounded, outdated, or contradicts the source. List the specific items.

### Check 3: Voice Consistency

Does the deliverable sound like the founder? Check for generic AI phrasing, banned words, dashes, and fillers. Check for tone mismatch (too formal for a warm contact, too casual for a first cold outreach).

PASS if: voice matches the founder's written style for this recipient type.
FAIL if: generic AI phrasing, banned words, em or en dashes, or tone mismatch. List the specific offenders.

### Check 4: Asset Inlining

Are all referenced assets (images, attachments, links, logos, screenshots) actually inlined or attached? Broken links, missing images, and "see attached" with nothing attached are common.

PASS if: every referenced asset is present in the deliverable as the recipient will see it.
FAIL if: a reference exists without the asset, or a link is dead. List specifics.

### Check 5: Token Replacement

Are all personalization tokens replaced with real values? Common tokens: {name}, {company}, {date}, {amount}, [INSERT X], TBD, TODO, XXX, placeholder text.

PASS if: no tokens, placeholders, or TODO markers remain.
FAIL if: any token or placeholder is still in the text. List each one.

### Check 6: Cross-Reference Update

Should any internal file be updated when this goes out? Common triggers:

- Outreach message sent: update context/clients.md
- Proposal sent: update context/clients.md and context/decisions.md if terms are in play
- Content published: update content tracker
- Invoice sent: update the relevant tracking file
- Commitment made: log to brain/log.md

PASS if: all cross-references are identified and either already updated or queued with a clear plan.
FAIL if: a cross-reference is needed and no plan exists. List which file needs which update.

### Check 7: Recipient-Readiness

Imagine the recipient opening this cold, with no context from prior conversation. Can they:

- Understand what this is within 10 seconds?
- Know what they are being asked to do?
- See the next step clearly (reply, sign, review, pay, schedule)?

PASS if: the deliverable is self-contained for the recipient's context level.
FAIL if: the recipient would need to ask a clarifying question or hunt for context. Identify what is missing.

## Output Format

Return a single block. No preamble. No summary beyond what is shown below.

```
PRE-SEND CHECK
---
Deliverable: [one-line description]
Recipient: [name or type]
Channel: [email / LinkedIn / WhatsApp / PDF / other]

1. Blind-Spot Review: PASS / FAIL - [one-line reason]
2. Source-Truth Match: PASS / FAIL - [one-line reason]
3. Voice Consistency: PASS / FAIL - [one-line reason]
4. Asset Inlining: PASS / FAIL - [one-line reason]
5. Token Replacement: PASS / FAIL - [one-line reason]
6. Cross-Reference Update: PASS / FAIL - [one-line reason]
7. Recipient-Readiness: PASS / FAIL - [one-line reason]

---

VERDICT: SHIP / HOLD
[If HOLD: list the specific items to fix in the deliverable before re-running the gate.]
[If SHIP: list any cross-references the founder must update after sending.]
```

## Rules

- You are read-only on the deliverable. You do not rewrite. You do not fix. You report.
- One FAIL = HOLD. The gate is binary. Do not soften with "mostly fine" or "minor issue". A check either passes or it does not.
- If the founder argues a FAIL, re-state the specific item. Do not negotiate the gate.
- If the deliverable passes all seven, list the cross-references the founder must update after sending so the revenue loop stays honest.
- Never invoke other skills mid-check. The gate runs inline. If the founder needs a rewrite, that is a separate request after the gate.
- If the founder skips the gate and ships anyway, note it in the running log with a STALL flag so the pattern is visible.
