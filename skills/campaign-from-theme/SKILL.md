---
name: campaign-from-theme
description: >
  Turn one theme into a structured marketing campaign. Say "build a campaign", "campaign for <topic>", "plan a campaign", "draft a launch campaign", or run /founder-os:campaign-from-theme. The skill REFUSES to generate content until the user has answered five funnel-gating questions: speaker (operator or brand), objective (awareness / consideration / conversion / retention / advocacy), audience segment + temperature (cold / warm / customer), channel-fit logic, and success metric. Output is a campaign brief with sequencing rationale, then 3 to 7 content drafts in the right voice. Reads brands/<slug>/voice.yml + positioning.yml if a brand is named, else core/voice-profile.yml + core/identity.md.
why: "Industry-standard campaign generators output a calendar without knowing who the campaign is for, where the audience is in the funnel, or why one piece comes before another. That produces slop that the operator has to throw away. The gate is the value - it forces audience and objective clarity before any draft, which is what makes the output usable on first attempt."
enhance: "Run brand-voice-interview for the relevant brand first - a campaign in operator voice for a brand the operator runs will sound off-brand. The skill works either way but produces sharper output when the brand layer is captured."
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob"]
mcp_requirements: []
---

# Campaign from Theme

You are turning a theme into a sequenced, funnel-aware campaign brief plus content drafts. The output is NOT a content calendar from an industry template. It is a brief that names what the campaign is supposed to accomplish, who it is for, where they are in the funnel, why each piece comes before the next, and what success looks like - followed by drafts that survive on first attempt because the inputs were forced clear up front.

<HARD-GATE>
Do not produce a single content draft until ALL FIVE gate questions are answered:

1. Speaker - operator voice or a specific brand voice
2. Objective - awareness / consideration / conversion / retention / advocacy
3. Audience - segment AND temperature (cold / warm / customer)
4. Channel-fit - which channels survive the speaker + audience + objective intersection
5. Success metric - one number that tells the operator if the campaign worked

If the user pushes for drafts without answering, say:

> I can produce drafts after the five gate questions. Industry-standard campaign generators skip these and the output gets thrown away. Five questions, then drafts.

Then ask the questions ONE at a time. Do not bundle.
</HARD-GATE>

---

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

---

## Phase 7 - Sequencing logic (before drafts)

Before writing any draft, lay out the sequence and explain WHY each piece comes before the next. Show the user:

> Sequence for this campaign:
>
> **Piece 1: <type>** on **<channel>** - role: <opens the campaign by doing X for audience at temperature Y>
> **Piece 2: <type>** on **<channel>** - role: <builds on Piece 1 by Z>
> **Piece 3: <type>** on **<channel>** - role: <converts/anchors/etc.>
> ... (continue for 3 to 7 pieces total)
>
> The sequencing rationale: <one paragraph explaining the order, why each piece earns the next, and how the audience moves through the funnel during the campaign>
>
> Confirm or adjust. Then I draft.

Wait for confirmation. Adjust if requested.

Sequencing principles (apply silently when laying out the order):

- **Cold audiences need the hook to do double duty** - introduce the brand AND the problem at once. Save the offer for piece 2 or 3.
- **Warm audiences can start at the offer** but need a piece that re-establishes context before the offer lands.
- **Customer audiences can skip introduction** and lead with the new thing.
- **Awareness campaigns end with a soft CTA, not a hard one** - if the audience just met the brand, asking for a sale is a fit fail.
- **Conversion campaigns front-load the hardest CTA** and use later pieces for objection-handling.
- **Retention campaigns lead with intimacy** (recognition, gratitude, insider language) and then offer.
- **Advocacy campaigns make the customer the hero**, not the brand. Every piece celebrates a customer or gives them a reason to talk about the brand.
- **Channel order matters** - cold audiences usually hit social before email, warm usually hit email before social, customers can hit either.

---

## Phase 8 - Draft

Now write each piece in the campaign sequence. For EACH piece:

1. Load voice profile (operator or brand) and apply it via `your-voice` skill.
2. Match the format to the channel (LinkedIn = 100 to 300 words, IG = 50 to 150, email = 200 to 500, WhatsApp = under 80, etc.).
3. Open with a hook matched to the audience temperature.
4. CTA must come from the `available_ctas` list. Never invent.
5. Apply the anti-AI baseline + brand register adjustments (read your-voice for the rules).
6. Label each piece with its role in the sequence at the top.

Output format:

```
CAMPAIGN BRIEF
==============
Theme: <theme>
Speaker: <operator | brand display_name>
Objective: <stage>
Audience: <segment> at <temperature>
Channels: <primary> + <support>
Timeline: <duration>
Success metric: <metric>
CTAs available: <list>

SEQUENCING RATIONALE
====================
<one paragraph>

PIECE 1: <type> on <channel>
----------------------------
ROLE: <one line>
HOOK ANGLE: <one line>

<draft>

CTA: <which CTA from available_ctas>

PIECE 2: ...
```

After all drafts, add:

```
WHAT TO MEASURE
===============
At end of campaign, check: <success metric>
Soft signals to watch: <2 to 3 leading indicators>

WHAT TO REVIEW IF IT FAILS
==========================
1. <most likely failure: hook did not match temperature / channel was wrong fit / CTA too hard for the stage>
2. <second most likely>
3. <third>
```

---

## Phase 9 - Save the brief

Ask:

> Save this campaign brief for later reference? It goes to `campaigns/<slug>-<date>.md`.
>
> Options: yes / no.

If yes, write to `campaigns/<slug>-<YYYY-MM-DD>.md`. Slug = kebab-case of theme. Create the `campaigns/` directory if it does not exist.

If no, just leave the output in the conversation.

---

## Re-run behavior

If the user wants to revise an existing campaign, ask:

> Adjust an existing brief, or build a new one? (adjust / new)

If adjust, ask which file under `campaigns/` and which gate to re-walk. Only re-walk the gates that changed.

---

## Rules

- The five gates are non-negotiable. Refuse to draft without all five.
- One question at a time. Wait for answer.
- If the user gives a multi-channel answer for objective ("I want awareness AND conversion"), push back once and force a single primary.
- Anti-AI rules from `your-voice` apply to every draft.
- Buyer language from positioning takes priority over invented hooks. If the audience says "I want something that lasts", use that line - do not clean it up.
- Never suggest a channel that is on the brand's `channels.off_limits` list.
- Never invent a CTA that is not in the operator's `available_ctas` list.
- If the operator says the audience is everyone, push back: "Everyone is no one. Pick the segment most likely to convert. The campaign can speak to adjacent segments without optimizing for them."
- If the operator picks 5+ channels, push back: "A campaign that runs on 5+ channels well requires more execution capacity than most solo operators have. Pick 1 primary and up to 2 support. We can repeat the model on other channels later."

---

## Failure modes to watch

- **Generating without gating.** The whole point of this skill is the gate. Skipping it produces slop. Always ask the five questions, even if the user says "just give me ideas".
- **Industry-standard sequencing.** "Hook, story, CTA" is not a sequencing rationale - it is a single-post pattern. A campaign sequence is about how piece 1 earns piece 2, not about each piece's internal structure.
- **Channel-stuffing.** More channels = more risk of misfit. Default to 1 primary + 1 support. Only add more when the operator has documented capacity.
- **Vanity metric pick.** "More followers" is rarely a success metric for a campaign. Push toward something tied to the objective.
- **Hook-temperature mismatch.** A cold-audience hook that assumes brand knowledge will fail silently. Check temperature before writing each hook.
- **Forgetting the audience pain language.** If positioning has buyer_language, lead with it. Operators are convinced their hooks are sharper than what the buyer actually says. They are usually wrong.
