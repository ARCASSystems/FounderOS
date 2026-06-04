# Phases 0-6 - Theme capture + the five gates + constraints

Load this when you start the gating sequence. Walk these in order, ONE question at a time. Do not produce a single content draft until all five gates are answered.

## Phase 0 - Theme capture

Ask:

> One sentence: what is the theme of the campaign? This is not the headline. It is the underlying idea. (e.g. "Why bespoke beats off-the-rack for weddings", "The cost of waiting to hire", "How our retainer model changed last quarter".)

Capture as `theme`. If the user gives a topic without an angle, ask one follow-up: "What is the angle on that theme - what do you want the audience to walk away believing or feeling?"

---

## Phase 1 - Gate 1: Speaker

### List brands

Run: `python scripts/list-brands.py` if the script exists. If not, glob `brands/*/voice.yml`.

If 0 brands exist:
- Say: "No brand voices captured yet. This campaign will use your personal voice from `core/voice-profile.yml`. If you want it in a brand voice instead, run `/founder-os:brand-voice-interview` first."
- Set speaker = `operator` and continue.

If 1+ brands exist:
- Ask:
  > Whose voice should this campaign use?
  >
  > 1. **You** - your personal voice (operator).
  > <list each brand by display_name>
  > N+1. **Set up a new brand voice** - run brand-voice-interview first.
- Capture the choice as `speaker`. Save the brand slug if a brand was chosen.

Load the matching voice + positioning files:
- If operator: read `core/voice-profile.yml` + `core/identity.md`.
- If brand: read `brands/<slug>/voice.yml` + `brands/<slug>/positioning.yml`.

If a brand was chosen but `brands/<slug>/positioning.yml` is missing, push the user to complete it first:

> The brand voice is captured but the positioning file is missing. Campaign needs audience, offer, and proof points from positioning. Run `/founder-os:brand-voice-interview` and complete Phase 1 of the questions, then come back.

Stop until positioning is captured.

---

## Phase 2 - Gate 2: Objective

Ask:

> What is this campaign FOR? Pick one. The whole sequence will be built around this objective.
>
> 1. **Awareness** - the audience does not yet know the brand or the problem exists. Goal: get the right people to recognize and remember.
> 2. **Consideration** - the audience knows the brand exists but has not decided. Goal: make the offer feel relevant, credible, and worth comparing.
> 3. **Conversion** - the audience is ready to act. Goal: remove the last friction and trigger the action.
> 4. **Retention** - the audience already bought once. Goal: keep them engaged, get them to repurchase or renew.
> 5. **Advocacy** - the audience is loyal. Goal: turn them into a referral source.

Capture as `objective`. If the user picks more than one, push back:

> A campaign can support more than one stage but it should be built around one primary stage. Which is the primary? The others become secondary effects.

Force a single primary.

---

## Phase 3 - Gate 3: Audience (segment + temperature)

### Segment

If a brand was chosen and positioning is loaded, show the captured segments:

> Positioning says the primary segment is `<positioning.audience.primary_segment>` and secondary segments are `<list>`. Pick one for this campaign, or describe a different segment.

If operator was chosen or no positioning exists, ask:

> Describe the audience for this campaign in one sentence. (Demographic, geography, context, what they care about.) Use plain language.

Capture as `audience.segment`.

### Temperature

Ask:

> How well does this audience know you or the brand?
>
> 1. **Cold** - they have never heard of the brand. They do not know they have the problem the brand solves. Hooks must do the work of introducing both.
> 2. **Warm** - they have seen the brand at least once. They may have engaged. They know the problem exists but have not committed. Hooks can assume awareness and focus on the offer.
> 3. **Customer** - they have bought already. They trust the brand. Tone is intimate, no introduction needed.

Capture as `audience.temperature`. This is the most-skipped question in industry generators and the most expensive to skip.

### Pain language

If positioning has `voice.buyer_language`, surface it now:

> Buyer first sentence captured: `<value>`. Buyer phrases: `<list>`. The campaign will use these as raw material for hooks.

If buyer_language is empty, ask:

> Quick capture: in the audience's own words, what is the first sentence out of their mouth when they describe the problem this campaign addresses?

Capture and add to the campaign brief.

---

## Phase 4 - Gate 4: Channel-fit logic

This is where industry generators fail hardest. They suggest "post on LinkedIn AND Instagram AND TikTok" because more is more. Real campaigns survive on 1 to 3 channels run well.

### Start from positioning channels

If brand positioning was loaded, the candidate channels are `positioning.channels.primary` + `secondary`. Off-limits channels are blocked.

If operator: ask what channels they actually publish on.

### Apply the speaker + audience + objective intersection

For each candidate channel, score it against three filters:

1. **Speaker fit** - does this channel match how this speaker actually shows up? (A corporate-restrained B2B brand on TikTok is a fit fail. A measured-elegant retail brand on Twitter/X is a fit fail.)
2. **Audience fit** - does the audience actually consume this channel for this kind of content? (Cold consumers on LinkedIn = mostly no. Cold B2B on Instagram = mostly no.)
3. **Objective fit** - does this channel support this funnel stage? (Awareness on Google Business Profile = unlikely. Conversion on a podcast = unlikely.)

Show your reasoning to the user:

> Channel-fit analysis for this campaign:
>
> - **<channel 1>**: <speaker fit> | <audience fit> | <objective fit> | overall: <strong / partial / weak>
> - **<channel 2>**: <same>
> - <continue for each candidate>
>
> Recommended channel mix for this campaign:
>
> - **Primary**: <1 channel - the one this campaign hinges on>
> - **Support**: <0 to 2 channels - amplification or sequencing>
>
> Confirm or override.

Capture as `channels.primary` and `channels.support`. Wait for confirmation.

---

## Phase 5 - Gate 5: Success metric

Ask:

> What is the ONE metric that tells you this campaign worked? Pick the one closest to the objective.
>
> - Awareness: impressions, reach, new followers, brand-search lift.
> - Consideration: profile visits, link clicks, replies, saves, time-on-page.
> - Conversion: bookings, sales, signups, inquiries, form fills, store visits.
> - Retention: repeat purchase rate, renewal rate, engagement frequency.
> - Advocacy: referrals, shares, tagged user-generated content, testimonial responses.
>
> Vanity metrics (likes alone) are not a success metric. Pick something that ties to the objective.

Capture as `success_metric`. If they pick a vanity metric, push back once.

---

## Phase 6 - Constraints

Ask:

> Two more quick ones before I draft.
>
> 1. **Timeline** - how many days does this campaign run over? (Single day, 5-day sequence, 2-week drip, 30-day campaign, ongoing.)
> 2. **CTAs available** - what can the audience actually do? (Book a call, WhatsApp, DM, click a link to <where>, walk in to <location>, reply to email, etc.) List all available actions.

Capture as `timeline` and `available_ctas`. The available CTAs constrain what every piece can ask for.
