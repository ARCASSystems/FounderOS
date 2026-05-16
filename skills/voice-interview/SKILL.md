---
name: voice-interview
description: >
  Set up the writing-voice profile. Say "set up my voice profile", "set up my voice", "voice interview", or "capture my voice" (or run /founder-os:voice-interview). Interactive interview that captures rhythm, openings, closings, contractions, idiosyncrasies, and writes the result to `core/voice-profile.yml`. Asks for samples first because samples beat self-description, then asks shaping questions to fill the gaps. Extracts intent from messy real-world answers, never asks the user to be structured.
allowed-tools: ["Read", "Write", "Edit"]
mcp_requirements: []
---

# Voice Interview

You are running an interactive interview to capture the user's writing voice. The output is `core/voice-profile.yml`. The voice-profile feeds the `your-voice` skill, which then writes everything as the user from that point on.

<HARD-GATE>
Do not generate `core/voice-profile.yml` until you have collected at least 2 reference samples (pasted in chat OR sourced from existing session artifacts: `brain/rants/*.md`, `context/decisions.md`, `brain/log.md` recent entries, or `clients/*/communications/`) AND walked the shaping questions, including buyer-language questions and anti-example questions. Samples are the ground truth. If the user has no existing artifacts and refuses to paste samples, ask them to write 2 short pieces in the chat right now (a 2-sentence work email and a LinkedIn-style hook). Don't proceed without samples - the profile without samples is a stereotype.

Do not invent answers. If the user skips a question, leave the field as `[NOT SET]` and tell them they can re-run the interview later.
</HARD-GATE>

---

## Phase 0 - Welcome

Say exactly:

> Voice interview. About 10 minutes. The output is a voice profile file that will write everything as you from now on - emails, posts, scripts, cover letters, whatever you generate later. We'll do it in three parts: paste a few samples of your writing, walk a few shaping questions, then you confirm and we save. Ready?

Wait for confirmation.

---

## Phase 1 - Samples (the ground truth)

### Pre-step: Scan for existing artifacts

Before asking for fresh samples, run a quick scan for writing the user has already produced in this OS:

- `brain/rants/*.md` (raw voice rants from `/rant` captures)
- `brain/log.md` (recent #written or #drafted entries from the last 30 days)
- `context/decisions.md` (decision rationales the user has authored)
- `clients/*/communications/*.md` (email drafts and outbound messages)

If 2 or more candidates are found, present them as:

> I found writing on your system from <list 2-3 candidates with source + first 60 chars>. Should I use the first two as your reference samples? Or would you rather paste fresh ones?

If the user says yes, count those as samples 1 and 2 and skip ahead to "After samples are captured" further down this Phase. If they want fresh, fall through to the paste flow.

If fewer than 2 candidates exist (typical for a fresh install), skip this pre-step and go straight to the paste flow.

Never use session-sourced samples without the user's explicit yes. The samples drive the voice profile - silent capture would feel surveillance-y.

### Paste flow

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

> Got it. Now I'll ask 12 shaping questions to fill in patterns the samples might not show. Quick answers are fine.

---

## Phase 2 - Shaping questions

Ask each one in order. ONE at a time.

### Q1. Sentence rhythm

Ask:

> Question 1. When you write, do your sentences run short and punchy, longer and building, mixed up aggressively, or more like verse with line breaks for breath? Pick the one that feels closest. Or describe it your own way.

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

### Q7. Buyer first sentence

Ask:

> Question 7. When your buyer describes their problem to you, what is the first sentence out of their mouth?

Capture as `buyer_language.first_sentence`. If they say they do not know, write `[NOT SET]`. Do not rewrite it into cleaner marketing language. The rough phrasing is the useful part.

### Q8. Buyer phrases

Ask:

> Question 8. What is a phrase your buyer says that makes you nod every time? One to three phrases is enough.

Capture as `buyer_language.phrases`. These phrases help `linkedin-post`, `email-drafter`, `proposal-writer`, and `client-update` meet the buyer in their own words.

---

## Phase 2.5 - Anti-examples

Ask each one in order. ONE at a time.

### Q9. Contrarian take

Ask:

> Question 9. Name one belief you hold about your work that most people in your field would push back on. One sentence.

Capture as `anti_examples.contrarian_takes`. If they give more than one, keep 1 to 3 entries. If they skip, write `[]`.

### Q10. Aesthetic crime

Ask:

> Question 10. What is one phrase, sentence structure, or formatting tic that makes you cringe when you see it in writing? Doesn't have to be in your own writing - anywhere.

Capture as `anti_examples.aesthetic_crimes`. If they give more than one, keep 1 to 3 entries. If they skip, write `[]`.

### Q11. Red flag

Ask:

> Question 11. When you read something and immediately suspect the writer is faking expertise, what was the tell? Name one specific pattern.

Capture as `anti_examples.red_flags`. If they give more than one, keep 1 to 3 entries. If they skip, write `[]`.

### Q12. Anti-example pairs

First show this worked example:

> Bad: "It's not just about hiring fast - it's about hiring right."
> Good: "Most of the bad hires came from agreeing too quickly."
> Rule: "Cut negation-contrast openings. Lead with the specific incident."

Then ask:

> Question 12. Now pick 3-6 short pieces from the samples you pasted earlier. For each one, write a BAD version: how Claude or a generic AI would have written the same idea. Then write your GOOD version (which is the original sample line, slightly tightened if needed). Add a one-line rule that explains what the rewrite changes.

Capture as `anti_examples.pairs`. Each pair has `bad`, `good`, and `rule`. The BAD line must be plausible, not a strawman. The GOOD line must be drawn from or directly inspired by a real sample. The rule must be one line and usable by a writing skill.

If the user struggles, offer to extract one candidate pair from their pasted samples and ask them to confirm or rewrite it. Do not write the pair until they approve it. Capture 3 to 6 pairs. If the user gives fewer than 3 after one prompt, accept what they have and write only those pairs.

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
> - Buyer first sentence: <value>
> - Buyer phrases: <list>
> - Contrarian takes: <list>
> - Aesthetic crimes: <list>
> - Red flags: <list>
> - Anti-example pairs: <count> pairs captured
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
  buyer_language:
    first_sentence: "<what the buyer says first>"
    phrases:
      - "<phrase>"
      - "<phrase>"
  anti_examples:
    pairs:
      - bad: "<sentence the user would never write>"
        good: "<the user's rewrite of the same idea>"
        rule: "<one-line rule the rewrite teaches>"
    contrarian_takes:
      - "<belief the user holds that their field pushes back on>"
    aesthetic_crimes:
      - "<phrase, structure, or word that makes the user cringe>"
    red_flags:
      - "<pattern that signals fake expertise>"
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

If a field is not set, write `"[NOT SET]"` for strings, `0` for numbers, or `[]` for lists. If an anti-example sub-block is empty, write that sub-block as `[]`. Do not invent values.

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
- Plain language. The user is not a linguist.
