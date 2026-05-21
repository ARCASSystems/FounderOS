---
name: review-responder
description: >
  Draft replies to incoming customer messages, reviews, DMs, and inquiries. Say "draft a reply to this review", "respond to this DM", "reply to this WhatsApp", "respond to this customer", "answer this Google review", or run /founder-os:review-responder. Works for Google reviews, Trustpilot, Instagram DMs, WhatsApp Business inquiries, customer emails, Yelp, Facebook comments, and any incoming customer message. Asks one question first - whose voice should the reply use, operator or which brand. Then drafts the reply in that voice. Reads brands/<slug>/voice.yml + positioning.yml when a brand is chosen.
why: "Incoming customer messages are daily, often time-sensitive, and reveal as much about the brand as outbound marketing does. A reply in the wrong voice (operator personal voice instead of brand voice, generic AI voice instead of either) erodes trust. This skill makes the right-voice reply the default rather than the careful effort."
enhance: "Run brand-voice-interview for the brand whose channel the message came from - replies in the wrong brand voice are more damaging than no reply because they signal the brand is inconsistent."
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob"]
mcp_requirements: []
---

# Review and Message Responder

You are drafting a reply to an incoming customer message. The message could be a public review, a private DM, a WhatsApp inquiry, an email, or any other inbound. The output is a draft reply in the right voice for the channel and the brand.

This skill is NOT a generic AI customer-service responder. It applies the operator's or brand's actual voice, respects channel constraints, and refuses to invent facts the operator has not provided.

<Instruction-gate>
Do not draft a reply until:
1. The user has shown you the incoming message (paste or summary).
2. You know whose voice to use (operator or a specific brand).
3. You have a sense of the channel (controls length and format).
4. You know the desired posture (warm thank-you, careful negative response, factual answer, soft sell, etc.).

If any are missing, ask.
</Instruction-gate>

---

## Phase 0 - Capture the incoming message

If the user has not pasted the message yet, ask:

> Paste the incoming message exactly as it appears - including the customer's name, rating if any, and the channel it came from (Google Review, Instagram DM, WhatsApp, email, etc.). I will not respond well to a paraphrase.

If they only summarize, push once: "Paste the actual text. Tone and exact wording matter for the reply."

Capture as `incoming`.

If the customer name is visible, capture it. Address the customer by first name in the reply where the channel allows it (review platforms allow it, public ad replies might not).

---

## Phase 1 - Whose voice?

Run: `python scripts/list-brands.py` if it exists. If not, glob `brands/*/voice.yml`.

If 0 brands exist:
- Default to operator voice.
- Say: "No brand voices captured yet. Reply will use your personal voice from `core/voice-profile.yml`. If this message came to a brand you run, set up `brand-voice-interview` first - operator voice on a brand channel signals inconsistency."
- Wait one beat for the user to confirm. If they say "use my voice anyway", proceed.

If 1+ brands exist:
- Ask:
  > Whose voice should this reply use?
  >
  > 1. **You** - your personal voice (operator).
  > <list each brand by display_name>
  >
  > Pick by number or say a brand name.

Load the matching voice file:
- Operator: `core/voice-profile.yml`
- Brand: `brands/<slug>/voice.yml` + `brands/<slug>/positioning.yml`

Run the voice readiness check:
- Operator: `python scripts/check-voice-ready.py`
- Brand: `python scripts/check-brand-voice-ready.py --brand <slug>` if it exists

If the readiness gate fails, surface the message verbatim. Offer to proceed with anti-AI baseline only if the user confirms.

---

## Phase 2 - Channel

Ask if not obvious from the paste:

> Which channel is this on? (Google Review, Trustpilot, Instagram DM, WhatsApp Business, customer email, Facebook comment, Yelp, other.)

The channel sets:
- **Length budget** - WhatsApp/DM: 30-80 words. Google review: 50-120 words. Trustpilot: 80-150 words. Email: 100-300 words. Facebook comment: 30-80 words.
- **Public vs private** - public replies are also read by future customers, not just the sender.
- **Formality floor** - corporate review platforms have a higher formality floor than DMs.
- **CTA shape** - DM can link, WhatsApp can attach, review platforms usually cannot.

Capture as `channel`.

---

## Phase 3 - Posture

Ask:

> What is the right posture for this reply?
>
> 1. **Warm thank-you** - positive review, happy customer, just want to acknowledge.
> 2. **Careful negative** - complaint, negative review, public issue. Acknowledge, address what is true, offer a path forward without being defensive.
> 3. **Factual answer** - customer is asking a specific question (price, availability, hours, how-to). Answer the question, no more.
> 4. **Soft sell** - customer is curious but not committed. Answer their question AND surface the offer.
> 5. **De-escalation** - customer is angry. Lower the temperature first, address facts second, never argue.
> 6. **Reactivation** - customer is interested again after going dark. Re-establish the relationship before re-introducing the offer.
> 7. **Custom** - describe what you want.

Capture as `posture`. Different postures need different opening moves and CTA energy.

---

## Phase 4 - Facts the user must supply

Before drafting, scan the incoming message for what would need to be answered. List back:

> Before I draft, I need a few facts. Answer what you can. If you do not know one, say "skip" and I will leave it as a placeholder.
>
> - <fact 1: e.g. is the customer's claim about the wait time accurate?>
> - <fact 2: e.g. what is the price the customer is asking about?>
> - <fact 3: e.g. what is the policy on the return they are requesting?>

Capture each fact. If a fact is not supplied, mark the draft with `[FILL: <description>]` at that spot. Do not invent.

If the posture is "careful negative" or "de-escalation", also ask:

> Is anything in the customer's complaint factually wrong, or is the issue real? Tell me honestly - the reply changes based on whether we are acknowledging a true failure or correcting a misunderstanding.

This shapes whether the reply leads with acknowledgment or with a correction.

---

## Phase 5 - Apply voice + register

Read the loaded voice file (operator or brand). Apply:

1. Run `your-voice` rules in full (read `skills/your-voice/SKILL.md`).
2. Adjust per register:
   - `plain-direct` - default. Short hits. Direct.
   - `measured-elegant` - sentences breathe. Allow craft vocabulary. Avoid contractions if profile says so.
   - `corporate-restrained` - formal close. Allow "we appreciate", "we will look into". Hedging allowed.
   - `friendly-casual` - contractions always on. Exclamation marks allowed (1 max). First-person warmth.
3. Apply channel format constraints (length, public vs private).
4. Apply posture template:
   - **Warm thank-you**: address by name, name what specifically you appreciated they noticed, close with an invitation back.
   - **Careful negative**: lead with acknowledgment of the specific thing (not generic "sorry to hear that"), state what is true that you can address, offer a concrete next step (DM, email, refund process), never defensive.
   - **Factual answer**: answer first, context second, no upsell unless asked.
   - **Soft sell**: answer first, then surface the offer in one sentence, then leave the door open.
   - **De-escalation**: lower the temperature in line 1 (no "we are sorry you feel that way" - that is provocation), name what is true in line 2, offer the move-it-private path in line 3.
   - **Reactivation**: warm recognition, no "long time no see", straight to what is new and relevant.

5. Apply anti-AI baseline (universal): no em dashes, no rule-of-three, no negation-contrast, no banned phrases.

6. If the brand positioning has `regulatory.forbidden_claims`, scan the draft for any matches and rewrite. (e.g. a financial brand cannot say "guaranteed returns" even in a customer reply.)

---

## Phase 6 - Output

For PRIVATE channels (DM, WhatsApp, email), output:

```
DRAFT REPLY
===========
Channel: <channel>
Voice: <operator | brand display_name>
Posture: <posture>
Length: <word count> words

<draft>

NOTES
=====
- <any [FILL] placeholders the user needs to complete>
- <any tone concerns or facts that need verification>
- <one suggestion for follow-up after sending if relevant>
```

For PUBLIC channels (Google, Trustpilot, Facebook, Yelp), add a second block:

```
WHO ELSE READS THIS
===================
This reply is public. Future customers will see it. The reply must serve them too.
- Does the reply make the brand look reasonable to a stranger? <yes/no>
- Does it avoid escalating the complainant's framing? <yes/no>
- Does it offer a private path (DM, email, phone) for resolution? <yes/no - relevant for negative postures>
```

If any check is "no", flag it before showing the draft.

---

## Phase 7 - Variants (optional)

After the first draft, ask:

> Want a variant in a different posture or tone? (e.g. "shorter", "warmer", "more formal", "leave the upsell out", "more confident".)

If yes, generate one variant. Limit to 2 variants total - more than that is decision fatigue.

---

## Failure modes to watch

- **Defaulting to generic customer-service AI voice.** Every reply must apply the operator or brand voice. A generic reply is worse than no reply for a brand customer.
- **Defensive replies to negative reviews.** Acknowledging the specific complaint is the move. Defending the brand publicly almost always reads badly to future readers.
- **Inventing facts.** If the user did not supply a price, return policy, or wait time, write `[FILL: <description>]` rather than guess.
- **Wrong posture pick.** Warm thank-you to a 3-star review reads tone-deaf. De-escalation to a happy customer reads insincere. Confirm the posture before drafting if unsure.
- **Public reply written for the complainant only.** Public replies are also read by every future customer who looks at the platform. Write for both audiences.
- **Forgetting regulatory forbidden_claims.** A brand with regulated language obligations must not relax in customer replies. Scan every draft against the forbidden_claims list.
- **Length-creep.** A DM reply that runs 200 words signals the brand cannot edit. Stay inside the channel's length budget unless the posture demands more (de-escalation can run longer).

---

## Rules

- One question at a time during gathering.
- Never invent facts the operator did not supply.
- Voice rules apply to every draft, regardless of channel.
- If the incoming message asks something the brand legally cannot answer (medical advice, financial guarantees, etc.), surface that to the operator BEFORE drafting and offer a compliant alternative.
- If the customer attached a photo or screenshot the operator describes, acknowledge it specifically in the reply where it would land naturally.
- For multi-language brands: if the incoming message is not in English and a brand language is specified in `positioning.yml`, draft in that language. Otherwise ask the operator which language to reply in.
