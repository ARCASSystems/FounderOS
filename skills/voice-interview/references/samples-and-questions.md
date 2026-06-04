# Phase 2 - Samples + Phase 3 - Shaping questions (Q1-Q12)

Load this when you reach Phase 2. Walk samples first, then the 12 shaping questions, ONE at a time.

## Phase 2 - Samples (the ground truth)

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

> Part 2 of 3 - 12 shaping questions. Quick answers are fine.

---

## Phase 3 - Shaping questions (Q1-Q12)

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

### Anti-examples (Q9-Q12, continues Phase 3)

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
