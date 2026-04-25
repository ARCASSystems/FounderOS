---
name: voice-interview
description: >
  Interactive interview that captures the user's writing voice and writes it to core/voice-profile.yml. Run this as part of /personal-os:setup, or standalone if the user wants to refresh their voice. The interview extracts intent from messy real-world answers - it does not require the user to be structured. It asks for samples first because samples beat self-description, then asks shaping questions to fill in the gaps.
allowed-tools: ["Read", "Write", "Edit"]
---

# Voice Interview

You are running an interactive interview to capture the user's writing voice. The output is `core/voice-profile.yml`. The voice-profile feeds the `your-voice` skill, which then writes everything as the user from that point on.

<HARD-GATE>
Do not generate `core/voice-profile.yml` until you have collected at least 2 reference samples AND walked the shaping questions. Samples are the ground truth. If the user refuses to paste samples, ask them to write 2 short pieces in the chat right now (a 2-sentence work email and a LinkedIn-style hook). Don't proceed without samples - the profile without samples is a stereotype.

Do not invent answers. If the user skips a question, leave the field as `[NOT SET]` and tell them they can re-run the interview later.
</HARD-GATE>

---

## Why this works the way it does

People are bad at describing their own voice. Ask "what's your writing style?" and they say "professional and friendly." That's useless.

Samples are the ground truth. The shaping questions exist to fill in patterns the samples don't show (vocabulary blacklist, sign-off phrasing, person default for content the user has not written yet).

The interview should feel like a 10-minute conversation, not a 30-minute form. Adapt to messy input. If the user rambles, extract the answer from the ramble and reflect it back in one line. If they answer multiple questions at once, capture all of them and skip ahead. Never tell the user to be more concise.

---

## Phase 0 - Welcome

Say exactly:

> Voice interview. About 10 minutes. The output is a voice profile file that will write everything as you from now on - emails, posts, scripts, cover letters, whatever you generate later. We'll do it in three parts: paste a few samples of your writing, walk a few shaping questions, then you confirm and we save. Ready?

Wait for confirmation.

---

## Phase 1 - Samples (the ground truth)

Ask:

> Part 1 - samples. Paste 3 short pieces of your writing. They can be a recent LinkedIn post, an email you wrote to someone you respect, a cover letter, a journal entry, a Slack message, anything where you wrote in your real voice. Each piece can be short - even 50 words is enough. Paste the first one.

After they paste, ask: "What was this? (LinkedIn post, work email, cover letter, etc.)" Capture context.

Repeat for samples 2 and 3.

If they paste only 1 or 2, ask once more: "One more? Even a short one. The third sample is what makes the pattern clear instead of guesswork."

If they refuse to paste 3, ask them to write 2 short pieces in the chat right now:
- A 2-sentence work email saying no to a meeting they don't want.
- A LinkedIn-style opening line on a topic they care about.

This always works. Capture both as samples.

After samples are captured, say:

> Got it. Now I'll ask 6 shaping questions to fill in patterns the samples might not show. Quick answers are fine.

---

## Phase 2 - Shaping questions

Ask each one in order. ONE at a time.

### Q1. Sentence rhythm

Ask:

> Question 1 of 6. When you write, do your sentences run short and punchy, longer and building, mixed up aggressively, or more like verse with line breaks for breath? Pick the one that feels closest. Or describe it your own way.

Map the answer to: `short_hits | long_builders | mixed | verse_like`. If they describe it their own way, infer the closest match and reflect it back: "Sounds like X to me. Right?"

### Q2. Opening style

Ask:

> Question 2. When you start a piece, do you usually open with a punch (a position or provocation), a confession (something vulnerable), a question, an observation, a story (mid-scene), or a list? Or something else?

Map to: `punch | confession | question | observation | story | list`.

### Q3. Closing style + sign-off

Ask:

> Question 3. How do you end a longer piece? With weight (a statement that reframes), an extended hand (offering help, no sales pitch), a question that doesn't have an easy answer, or a specific sign-off phrase? If you sign off, what's the exact phrase you use?

Map closing to: `weight | hand | question | signoff`. If signoff, capture the exact phrase.

### Q4. Person + contractions

Ask:

> Question 4. Two quick ones together. First, when you write, do you mostly use "I", "you", or both? And do you use contractions (don't, it's, can't) always, sometimes, or never?

Capture both. Map to `first | second | mixed` and `always | sometimes | never`.

### Q5. Vocabulary

Ask:

> Question 5. Two parts. First, are there words you reach for naturally that feel like you? Three to five examples. Second, are there words you hate seeing in your own writing? Three to five examples.

Capture both lists. Add the hated words to the user's `banned_words` (on top of the universal blacklist).

### Q6. Quirks

Ask:

> Question 6. Anything you do on purpose that grammar-check would correct? Like saying "alot" instead of "a lot", or starting sentences with "And" or "But", or using parentheses for side thoughts. Things you don't want me to clean up.

Capture as `idiosyncrasies` list. If they say "no quirks", leave the list empty.

---

## Phase 3 - Confirm and save

Show this exact block (filled with the captured values):

> Here's what I captured. Confirm or correct any line.
>
> - Rhythm: <value>
> - Opening: <value>
> - Closing: <value>
> - Sign-off: <value or "no sign-off">
> - Person: <value>
> - Contractions: <value>
> - Reading level: 8 (default - I can change this if you want simpler or more technical)
> - Hedging: occasional (default - I can adjust if you hedge more or less)
> - Preferred words: <list>
> - Banned words (in addition to universal blacklist): <list>
> - Idiosyncrasies: <list>
> - Samples: <count> pieces captured
>
> Looks right? (yes / change X)

If yes, write `core/voice-profile.yml` from the captured values.

If they want to change something, edit the value and re-confirm.

---

## File output

Write `core/voice-profile.yml`. Use this exact structure:

```yaml
voice:
  rhythm: "<value>"
  opening_style: "<value>"
  closing_style: "<value>"
  signoff_phrase: "<value or empty string>"
  person_default: "<value>"
  contractions: "<value>"
  hedging: "<value>"
  reading_level: <number>
  preferred_words:
    - "<word>"
    - "<word>"
  banned_words:
    - "<word>"
    - "<word>"
  idiosyncrasies:
    - "<quirk>"
    - "<quirk>"
  samples:
    - title: "<title>"
      context: "<context>"
      text: |
        <pasted text>
    - title: "<title>"
      context: "<context>"
      text: |
        <pasted text>
    - title: "<title>"
      context: "<context>"
      text: |
        <pasted text>
```

If a field is not set, write `"[NOT SET]"` for strings, `0` for numbers, or `[]` for lists. Do not invent values.

---

## Phase 4 - Final message

Say exactly:

> Voice profile saved to core/voice-profile.yml. From now on, anything I generate for you will use this voice - emails, posts, scripts, cover letters, whatever. If something I write doesn't sound like you, tell me and we'll refine the profile.

Stop. Do not do anything else.

---

## Re-run behavior

If the user runs this skill and `core/voice-profile.yml` already has real values (not template placeholders), ask:

> A voice profile already exists. Want to start over from scratch, or just update specific fields? (start-over / update)

If `update`, ask which fields, then walk only those questions.
If `start-over`, run the full interview.

---

## Rules

- One question at a time. Wait for answer.
- Real users ramble. Extract intent. Don't ask them to be more structured.
- Never tell the user to be more concise. The volume is the thinking.
- Never invent samples. Never invent vocabulary.
- No em dashes, no en dashes. Hyphens with spaces.
- Plain language. The user is not a linguist.
