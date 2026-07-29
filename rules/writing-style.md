# Writing Style

> These rules apply to all written output: emails, documents, posts, proposals, scripts, Notion pages, everything.
> When in doubt, write like a smart person talking to another smart person. Not like an AI.

---

## Formatting Rules

- No em dashes (--). No en dashes. Simple hyphens only ( - ), with spaces around them.
- Max two hyphens per piece of writing.
- No semicolons. Break into two sentences instead.
- No rule-of-three constructions. (Not "fast, reliable, and scalable.")
- No meta-commentary. Don't say "In this section we will cover..." Just cover it.
- Contractions always. "Don't" not "do not." "It's" not "it is."

---

## Tone

- Calm authority from lived experience. Direct, specific.
- Simple language. If a simpler word exists, use it.
- Non-native English speakers may be reading. Avoid idioms and jargon.
- {{FOUNDER_COMMUNICATION_STYLE}}
  (e.g. "Founder-to-founder. We've both been in the room." or "Practitioner who's done the work, not a consultant describing it.")

---

## Banned Words and Phrases

Never use these:

- delve
- robust
- seamless
- leverage (as a verb)
- comprehensive
- holistic
- transformative
- streamline
- optimize (use "improve" or be specific)
- utilize (use "use")
- facilitate
- unlock
- navigate (metaphorically)
- ecosystem
- landscape (business landscape, competitive landscape)
- cutting-edge
- best-in-class
- world-class
- game-changer
- innovative

---

## Structural Tells

Everything above is phrase-level, and a find-and-replace pass fixes phrase-level problems. These four survive that pass, which is why they are what remains in current AI writing once the vocabulary is clean. Check for them last, after the word list.

**Aphorism budget: one per document.** The banned-phrase rules catch a formula like "X is the new Y". They do not catch the habit of ending every third paragraph on a quotable line. Three or four epigrams in one document is the tell, even when each one is individually good. Keep the best and say the rest plainly.

**No label-colon openers.** "Why this exists." / "The bar:" / "The rule:" / "The problem:" opening a paragraph. It reads as a slide title, and the sentence after it would almost always have opened the paragraph fine on its own. Delete the label.

**Do not define a thing by what it is not.** "This is not a framework." "It is not a general-purpose checker." Say what the thing is. A negation earns its place only where it stops a real misuse someone would otherwise make, or names a limit that genuinely surprises. Used as decoration it is filler wearing a serious face.

**A docstring is a contract, not a case study.** Fifteen lines at most: what the module does, its invariants, how to call it. The story of the defect that motivated it belongs in the commit that fixed it, with a pointer from the docstring if it is worth finding. This half is also the self-documenting-code bar in `rules/os-as-harness.md`.

---

## What Good Writing Sounds Like

Good: "The process takes three steps. Most people skip the second one. That's where it breaks."
Bad: "Our comprehensive, holistic approach streamlines your workflow to unlock transformative results."

Good: "I've seen this fail before. Here's why and what to do instead."
Bad: "In this increasingly complex landscape, it's crucial to leverage a robust framework."

---

## Document Defaults

- Default font: {{DEFAULT_FONT}} (e.g. Poppins, Inter, Georgia)
- Headers: clear and descriptive, not clever
- Lists: use when order matters or when items are genuinely parallel. Not as a way to avoid writing prose.
- Tables: use for comparisons and structured data only

---

## Voice Calibration

{{VOICE_CALIBRATION_NOTES}}
(e.g. "First person. Witness not commander. 'The team figured out...' not 'I built...'")
(e.g. "No titles in bylines unless the context requires it.")
