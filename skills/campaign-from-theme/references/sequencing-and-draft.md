# Phases 7-9 - Sequencing logic, drafting, and saving

Load this once all five gates plus constraints are answered.

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
