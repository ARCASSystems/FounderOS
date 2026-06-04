# Phase 3 - Brand voice (samples + shaping)

Load this when you reach Phase 3.

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
