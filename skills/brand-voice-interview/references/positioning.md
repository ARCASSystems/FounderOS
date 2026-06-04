# Phase 2 - Brand positioning (Q1-Q13)

Load this when you reach Phase 2. Positioning gates voice. The brand writes differently to a 25-year-old digital-native than to a 55-year-old in tailoring. Capture positioning before voice.

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
