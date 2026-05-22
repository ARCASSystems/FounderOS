---
name: brand-voice-interview
description: >
  Capture a brand's writing voice and positioning. Say "set up a brand voice", "capture our brand voice", "add a brand", "set up brand voice for <name>", or run /founder-os:brand-voice-interview. Different from voice-interview, which captures the OPERATOR's personal voice. This skill captures how a brand the operator runs speaks - separate from how the operator speaks. Writes brands/<slug>/voice.yml and brands/<slug>/positioning.yml. Supports operators who run an ecosystem of brands - this skill can be run once per brand.
why: "An operator can run multiple brands. The operator's personal voice and a brand's voice are not the same. Without a brand voice layer, every output sounds like the operator, which is wrong for any branded communication (customer comms, brand social, customer service, ads). Brand voice is the file every brand-coupled writing skill reads."
enhance: "Capture brand voice AFTER you have 3 to 5 real brand samples - existing captions, product copy, customer emails the brand has actually sent. The samples are the ground truth. A brand voice profile without samples is a stereotype."
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob"]
mcp_requirements: []
---

# Brand Voice Interview

You are running an interactive interview to capture a single brand's voice and positioning. Output is two files under `brands/<slug>/`:

- `brands/<slug>/voice.yml` - how the brand writes
- `brands/<slug>/positioning.yml` - who the brand serves, what it sells, how it differentiates

This skill is for BRAND voice, not OPERATOR voice. The operator's personal voice lives at `core/voice-profile.yml` and is captured by the `voice-interview` skill. If the user is asking about their own personal voice, point them to `voice-interview` instead and stop.

Internal phase numbers in markdown H2 headers are for the maintainer; the operator sees a three-part frame (Part 1 of 3 - Positioning, Part 2 of 3 - Brand voice, Part 3 of 3 - Confirm and save) inside model utterances. Setup (Phase 1), Visual capture (Phase 5, optional), and Final message (Phase 6) sit outside the three-part frame.

Cross-skill asymmetry note: this skill has 6 phases. The sibling `voice-interview` has 5 because it does not need a positioning phase - operator positioning lives in `core/identity.md` (captured by `founder-os-setup`). Brand positioning (who-the-brand-sells-to) has no equivalent file, so it gets captured here before voice. Do not collapse positioning into voice when editing this skill.

<Instruction-gate>
Do not write `brands/<slug>/voice.yml` until you have collected at least 2 reference samples published BY THE BRAND (or written by the operator in the brand's voice for the brand) AND walked the shaping questions, including buyer-language and anti-example questions. Samples are the ground truth.

Do not write `brands/<slug>/positioning.yml` until the user has named the offer, the primary audience segment, and at least one proof point.

Do not invent answers. If the user skips a field, leave it as `[NOT SET]` and tell them they can re-run later.
</Instruction-gate>

---

## Phase 1 - Setup (clarify scope, pick slug)

Before anything else, confirm the speaker.

Say exactly:

> Quick check before we start. There are two voices in this OS:
>
> 1. **Your personal voice** - how you write as a person. Personal LinkedIn, your own emails, your CV.
> 2. **A brand voice** - how a brand you run writes. Customer captions, brand social, customer service replies, ads.
>
> They are not the same. If you are running a single founder-led brand, they may overlap, but the brand voice should still be captured separately because it has to survive after you stop writing every word yourself.
>
> Is this for a brand you run, or for you personally? (brand / personal)

If they say "personal", stop and route to `voice-interview` instead.

If they say "brand", continue.

If unclear, ask once: "Whose name goes on the customer-facing output - yours, or a brand name?"

Then ask:

> What is the brand called? Use the customer-facing name as written on packaging, web, social.

Capture as `display_name`.

Generate a kebab-case slug from the name:
- Lowercase
- Replace spaces with hyphens
- Strip punctuation and articles ("the ", "a ", "an ")
- If two words feel redundant, keep the distinctive one

Show the user the suggested slug and ask:

> I will save this under `brands/<slug>/`. Confirm or give me a different slug.

If `brands/<slug>/` already exists, ask:

> A brand profile already exists at `brands/<slug>/`. Want to update it, start over for the same brand, or pick a different slug? (update / start-over / new-slug)

If `update`, ask which fields, then walk only those questions.
If `start-over`, run the full interview and overwrite.
If `new-slug`, ask for the new one.

Create the directory `brands/<slug>/` if it does not exist. Also create `brands/<slug>/assets/` for logo files.

---

## Phase 2 - Brand positioning (Q1-Q13)

Positioning gates voice. The brand writes differently to a 25-year-old digital-native than to a 55-year-old in tailoring. Capture positioning before voice.

### Q1. Offer in plain words

Ask:

> Part 1 of 3 - Positioning.
>
> One sentence: what does the brand sell? Plain words, not marketing. (e.g. "We sell custom-tailored suits in Dubai" not "We deliver bespoke sartorial experiences".)

Capture as `offer.primary`.

### Q2. Price band

Ask:

> What is the price range? Entry price to top price, in local currency. Use a range if pricing varies.

Capture as `offer.price_band`.

### Q3. Delivery model

Ask:

> How do customers receive what they buy? (in-store, online, hybrid, service-based, subscription, other)

Capture as `offer.delivery`.

### Q4. Primary segment

Ask:

> Who buys from you most often? One sentence describing the actual buyer - their age range, where they are, and what triggered the purchase. (e.g. "Men 30-55 in UAE who need a suit for a wedding or formal milestone in the next 4 weeks.")

Capture as `audience.primary_segment`.

### Q5. ICP paragraph

Ask:

> Now describe the buyer in a paragraph. Their context, what they were worried about, what made them choose you over other options. Use their words where you can. This is not a market research deck - it is the buyer in plain language.

Capture as `audience.icp_description`. Do not clean it up. Preserve the operator's phrasing.

### Q6. Secondary segments

Ask:

> Are there one or two other buyer types the brand also serves? (e.g. corporate accounts, gift buyers, walk-ins.) List up to 3.

Capture as `audience.secondary_segments`.

### Q7. Promise

Ask:

> What does the brand promise the buyer? One sentence. This is not a tagline - it is the implicit deal.

Capture as `promise.primary`.

### Q8. Proof points

Ask:

> What proves the promise? 2 to 4 specific facts. Years in business, turnaround time, number of customers served, awards, anything concrete.

Capture as `promise.proof_points`.

### Q9. Refusal list

Ask:

> What will the brand NOT promise, even if a competitor does? (e.g. "fastest delivery", "lowest price", "guaranteed results".) This list keeps your copy honest.

Capture as `promise.refuses_to_promise`.

### Q10. Competitors

Ask:

> Who does the buyer compare you against, and how do you differ from each? 2 to 4 names. One line on the difference for each.

Capture as `competitors.direct`.

Then ask:

> What does the buyer choose INSTEAD of buying at all? (e.g. "wearing what they already own", "DIY", "doing nothing".) One line on why your offer beats that.

Capture as `competitors.indirect`.

### Q11. Regulatory floor

Ask:

> Are there any claims the brand cannot legally make in your jurisdiction? (e.g. medical efficacy, guaranteed returns, "best" claims under consumer protection law.) Skip if none apply.

Capture as `regulatory.forbidden_claims`. If they skip, write `[]`.

### Q12. Channels

Ask:

> Where does the brand actually publish? Pick from: instagram, tiktok, linkedin, x, facebook, whatsapp, email_newsletter, google_business_profile, podcast, youtube, blog, paid_ads. Then tell me which channels you would NEVER use (so future suggestions skip them).

Capture as `channels.primary`, `channels.secondary`, `channels.off_limits`.

### Q13. Archetype (optional)

Ask:

> Optional. Pick a brand archetype if one fits, or skip. (hero / sage / creator / caregiver / explorer / ruler / jester / lover / everyman / outlaw / innocent / magician.) If you skip, I will infer one from the samples.

Capture as `brand.archetype`. If skipped, write `[NOT SET]` and infer from voice samples at the end.

---

## Phase 3 - Brand voice (samples + shaping)

### Pre-step: Scan for existing brand artifacts

Before asking for fresh samples, look for brand-published writing already in the OS:

- `brands/<slug>/` (in case any drafts already exist)
- `clients/<slug>/` (if the brand was previously tracked as a client)
- `raw/<slug>/` or `raw/brands/<slug>/`
- Any imported social exports under `sources/<slug>/`

If you find 2+ candidates, present them and ask the user to confirm before using them. Never use silently.

If none exist (typical), go straight to paste flow.

### Paste flow

Ask:

> Part 2 of 3 - Brand voice.
>
> Part 1 - samples. Paste 3 short pieces the brand has already published. Instagram caption, website hero, product page copy, customer email, DM reply, ad copy, anything in the brand's actual voice. Even 50 words is enough per piece. Paste the first one.

After each, ask "What was this? (caption, website, email, etc.)" and capture context.

If they paste only 1 or 2, push once: "One more? The third sample is what makes the pattern clear."

If they have nothing published yet, ask:

> No published copy yet? Then write 2 short pieces in chat right now, in the voice you want the brand to have:
>
> 1. A 50-word product/service description for someone seeing the brand for the first time.
> 2. A 2-sentence reply to a customer asking about price.
>
> These become your first samples. The brand voice gets sharper as you publish more.

Capture both.

After samples are captured, say:

> Got it. Now I will ask 10 shaping questions to fill the patterns the samples might not show. Quick answers are fine.

### Voice shaping questions

ONE at a time. Wait for answer.

### V1. Speaker

Ask:

> When the brand publishes a caption or replies to a customer, who is speaking? The brand itself (no named author), the founder by name, or a named spokesperson?

Map to `brand.speaker`: `brand | founder-led | spokesperson-led`.

### V2. Register

Ask:

> Which register fits the brand best?
>
> 1. **plain-direct** - founder-to-founder, short hits, no decoration (default for most B2B).
> 2. **measured-elegant** - premium, considered, allows craft vocabulary (luxury retail, hospitality).
> 3. **corporate-restrained** - B2B exec, formal, hedging and qualifiers allowed (enterprise, financial services).
> 4. **friendly-casual** - retail/consumer, warm, contractions always on (D2C, lifestyle).

Capture as `voice.register`. This controls which anti-AI allowances apply.

### V3. Rhythm

Ask:

> When the brand writes, do sentences run short and punchy, longer and building, mixed up aggressively, or more verse-like with line breaks for breath?

Map to `voice.rhythm`: `short_hits | long_builders | mixed | verse_like`.

### V4. Opening style

Ask:

> When the brand opens a caption or piece, what is the default move? A punch (stance, provocation), a confession, a question, an observation, a story (mid-scene), or a list?

Map to `voice.opening_style`: `punch | confession | question | observation | story | list`.

### V5. Closing + signoff

Ask:

> How does the brand end longer pieces? With weight (a statement that reframes), an extended hand (offering help, no sales pitch), an open question, or a specific sign-off phrase? If a sign-off, give me the exact phrase.

Capture `voice.closing_style` and `voice.signoff_phrase`.

### V6. Person + contractions

Ask:

> Two together. First, does the brand mostly write in "we", "you", "the brand by name", or a mix? Second, contractions (don't, it's): always, sometimes, never?

Capture `voice.person_default` (`first | second | third | mixed`) and `voice.contractions`.

### V7. Preferred + banned words

Ask:

> Words the brand reaches for naturally and wants to keep, 3 to 5. Then words you do NOT want to see in brand copy, 3 to 5.

Capture both lists.

### V8. Buyer language

Ask:

> When your buyer describes what they want, what is the first sentence out of their mouth? One sentence. Use their words, not your cleaned-up version.

Capture as `voice.buyer_language.first_sentence`.

Then:

> 1 to 3 other phrases your buyer says that make you nod every time.

Capture as `voice.buyer_language.phrases`.

### V9. Anti-examples (brand-flavored)

Ask:

> One generic-brand phrase or pattern that makes you cringe when you see it elsewhere. (e.g. "Crafted with passion, designed for excellence." "Our journey began...")

Capture as `voice.anti_examples.aesthetic_crimes`. 1 to 3 entries.

Then show this worked example:

> Bad: "Crafted with passion, designed for excellence."
> Good: "A jacket from this cloth lasts ten years if you let it."
> Rule: "No empty craft adjectives. Name the durable thing."

Then ask:

> Now pick 2 to 3 short pieces from the samples you pasted. For each, write a BAD version - how a generic brand-AI would write the same idea. Then keep the GOOD version (your sample line). Add a one-line rule.

Capture as `voice.anti_examples.pairs`. 2 to 4 pairs is enough. If they struggle, extract one candidate from their samples and let them rewrite or approve.

### V10. Idiosyncrasies

Ask:

> Anything the brand does on purpose that a copy editor would correct? (e.g. always lowercase, no exclamation marks, sentences as fragments, mid-caption line breaks.) Skip if none.

Capture as `voice.idiosyncrasies`. Empty list if skipped.

---

## Phase 4 - Confirm and save

Show this block (filled with captured values from BOTH positioning and voice):

> Part 3 of 3 - Confirm and save.
>
> Here is what I captured for `<display_name>`. Confirm or correct any line.
>
> **Positioning**
> - Slug: <slug>
> - Offer: <one-line>
> - Price band: <range>
> - Delivery: <model>
> - Primary segment: <one-line>
> - Promise: <one-line>
> - Proof points: <count> captured
> - Refuses to promise: <count> captured
> - Direct competitors: <count> captured
> - Off-limits channels: <list>
> - Archetype: <value or inferred-from-samples>
>
> **Voice**
> - Speaker: <value>
> - Register: <value>
> - Rhythm: <value>
> - Opening: <value>
> - Closing: <value>
> - Sign-off: <value or "no sign-off">
> - Person: <value>
> - Contractions: <value>
> - Preferred words: <list>
> - Banned words: <list>
> - Idiosyncrasies: <list>
> - Buyer first sentence: <value>
> - Buyer phrases: <list>
> - Anti-example pairs: <count>
> - Samples: <count>
>
> Looks right? (yes / change X)

If yes, write both files. If they want to change something, edit and re-confirm.

### File output

Write `brands/<slug>/voice.yml` using the structure from `templates/brand-voice.yml.template`. Replace every `[BRACKETED]` placeholder with the captured value or `[NOT SET]` if skipped.

Write `brands/<slug>/positioning.yml` using the structure from `templates/brand-positioning.yml.template`.

If `archetype` was inferred from samples (user skipped), pick the closest match from the samples and write it with a `# inferred` comment on the line.

Do not invent values. Empty lists are `[]`. Skipped string fields are `"[NOT SET]"`.

---

## Phase 5 - Visual capture (optional)

After both files are written, ask:

> Optional - Visual identity.
>
> Brand voice and positioning are saved. Want to capture the visual identity too (logo, colors, fonts)? It takes 5 to 10 minutes and unlocks branded visual outputs (proposals, decks, one-pagers in this brand's look).
>
> Options: yes-now / yes-later / not-needed.

If `yes-now`, dispatch to `brand-interview` and instruct it to write to `brands/<slug>/visual.yml` instead of `core/brand-profile.yml`.

If `yes-later`, say: "Run `/founder-os:brand-interview` later and I will save it under this brand."

If `not-needed`, stop here.

---

## Phase 6 - Final message

Say exactly:

> Brand voice and positioning saved under `brands/<slug>/`. Brand-coupled writing skills (linkedin-post, content-repurposer, email-drafter, review-responder, campaign-from-theme) can now write in this brand's voice. To use, say "write an Instagram caption for `<display_name>`" or "draft a campaign for `<display_name>`".
>
> Your personal voice at `core/voice-profile.yml` is unchanged. Personal posts and emails still use that.

Stop. Do not do anything else.

---

## Rules

- One question at a time. Wait for answer.
- Real operators ramble. Extract intent. Never ask them to be structured.
- Never invent samples or vocabulary.
- Plain language. Operators are not linguists or brand strategists.
- If the operator describes the brand voice as identical to their personal voice, ask one clarifying question: "When the brand has employees other than you writing for it, will they speak in your personal voice, or a brand voice that has its own character?" If they say brand voice has to survive their absence, the two voices are different and capture them separately.
- Slug must be unique under `brands/`. If a collision happens, append a disambiguator (e.g. `suit-carriage-uk` vs `suit-carriage-uae`).
