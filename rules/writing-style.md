# Writing Style

> These rules apply to all written output: emails, documents, posts, proposals, scripts, Notion pages, everything.
> When in doubt, write like a smart person talking to another smart person. Not like an AI.

---

## Formatting Rules

- No em dashes (--). No en dashes. Simple hyphens only ( - ), with spaces around them.
- The spaced hyphen is what replaces the em dash, so it carries real work and cannot be capped at two. Keep it under about ten per thousand words, which is roughly one per paragraph. Past that it stops reading as punctuation and starts reading as a tic. (This replaces the old "max two per piece" rule, which was measured against this repo's own pages in September 2026 and found to be unfollowable: they run five to twenty-six per thousand words, and the rule above the line is the reason.)
- No semicolons. Break into two sentences instead.
- No rule-of-three constructions. (Not "fast, reliable, and scalable.")
- No meta-commentary. Don't say "In this section we will cover..." Just cover it.
- Contractions in anything that talks: posts, emails, captions, messages. "Don't" not "do not." Not a rule for a contract, a doctrine page, or a spec, where the long form is normal and forcing contractions reads worse.

---

## Tone

- Calm authority from lived experience. Direct, specific.
- Simple language. If a simpler word exists, use it. Target a reading grade under 8.
- Non-native English speakers may be reading. Avoid idioms and jargon. "Move the needle", "low-hanging fruit" and "circle back" do not translate.
- One idea per paragraph. Four or more sentences running past seventy-five words is two paragraphs that have not been split yet.
- Do not signal your own honesty. "To be honest", "the honest answer", "worth saying", "frankly". The sentence is either true or it is not, and announcing it is true reads as though the rest was not.
- Do not hedge a fact you know. "Arguably", "to some extent", "it seems fair to say". Either say it or leave it out.
- Do not point a finger at what nobody did. "Nobody has ever used it", "the least-used asset", "this has been ignored". Say what to do now instead.
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

**No cross-references inside a document.** "As noted above", "see page 4", "the section below". A reader who has to hold two places in their head at once is being asked to do the work of an editor. Say the thing where it is needed, even if that means saying it twice.

**A heading over a single sentence is a label the sentence did not need.** Delete the heading and keep the sentence.

**No negation-contrast.** "It's not about the tool, it's about the outcome." "Not just faster, but cheaper." The shape is a rhythm borrowed from advertising. Say the positive claim on its own.

---

## How this page is enforced

Everything above that can be counted is counted by `scripts/register_census.py`. It reads the banned list off this page, so there is one list and it is the one you are reading. Zero-LLM, no key, no network: it runs on any plan.

```bash
python scripts/register_census.py drafts/proposal.md --lines
python scripts/register_census.py drafts/proposal.md --gate deliverable
```

The score starts at 100 and comes down by density, per thousand words, so a long document is not marked down for being long. Three gate profiles, because a client deliverable and a note to yourself fail for different things: `deliverable`, `content`, `internal`.

| Class | The rule it enforces |
|---|---|
| `banned_word` | the banned list on this page |
| `dash` | no em dashes, no en dashes |
| `hyphen_density` | the spaced hyphen stays under about ten per thousand words |
| `semicolon` | no semicolons |
| `triplet` | no rule-of-three constructions |
| `meta_commentary` | no meta-commentary |
| `idiom` | avoid idioms, non-native readers |
| `no_contraction` | contractions in writing that talks (scored on `content` only) |
| `paragraph_overload` | one idea per paragraph |
| `cross_ref` | no cross-references inside a document |
| `hedge_of_fact` | do not hedge a fact you know |
| `honesty_signal` | do not signal your own honesty |
| `finger_pointing` | do not point a finger at what nobody did |
| `negative_parallelism` | no negation-contrast |
| `aphorism_closer` | aphorism budget, one per document |
| `label_colon` | no label-colon openers |
| `define_by_exclusion` | do not define a thing by what it is not |
| `heading_one_liner` | a heading over one sentence is a label the sentence did not need |

Two things it cannot do. It cannot tell whether what you wrote is true, which is what `scripts/claims_check.py` and the reading pass are for. And it cannot tell a load-bearing use of a banned word from a lazy one, which is what `rules/banned-words-exceptions.txt` is for: record the judgment once and the gate stops raising it.

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
