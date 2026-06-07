---
name: your-voice
description: >
  Apply the founder's writing voice to any text. Trigger on every writing task: LinkedIn posts, YouTube scripts, emails, cover letters, applications, internal docs, anything that contains words. Say "rewrite this in my voice", "voice this up", or "apply my voice". Reads `core/voice-profile.yml`. If the profile is missing, falls back to anti-AI defaults and warns the user that the voice interview has not been run.
why: "Applies the captured voice profile to any text so every output sounds like you rather than like a language model - it is the layer that makes personalization real rather than cosmetic."
enhance: "Add anti-example pairs to core/voice-profile.yml over time by flagging outputs that do not sound like you - each pair tightens the profile and reduces future corrections."
allowed-tools: ["Read", "Write", "Edit", "Bash"]
mcp_requirements: []
---

# Your Voice

Runs on: reasoning - reads your files and reasons; any capable agent can run this.

This skill writes in the right voice for the task. There are two voice layers:

- **Operator voice** at `core/voice-profile.yml` - how the user writes as a person. Default for personal output (personal LinkedIn, your CV, emails from you).
- **Brand voice** at `brands/<slug>/voice.yml` - how a brand the operator runs writes. Used when output represents a brand (brand social, customer comms, ads, customer-service replies, brand-published content).

An operator can have one or many brands. The two layers are independent. If `brands/` does not exist, this skill behaves exactly as it did before the brand layer existed - operator voice only.

Read this entire file before writing anything. Then load the right voice profile per the routing below. The universal anti-AI baseline and the self-check below apply on every write. The per-setting interpretation of each profile field (rhythm, opening, closing, person, contractions, hedging, reading level, vocabulary, samples) and the brand register allowances live in `references/profile-rules.md` - read it once you have loaded the profile and need to interpret a value.

If the active profile is missing or still contains the template placeholders (the `[BRACKETED]` values), do not stop. Generate the requested output using the universal anti-AI baseline below as the voice rules, and prepend a one-line warning to the output:

> Voice profile not set up. Output uses anti-AI baseline only and will sound generic. Run `/founder-os:setup` and complete the voice interview, or edit the relevant voice profile to make outputs sound like you.

The warning is a comment to the user, not part of the deliverable. Place it above the output, separated by a blank line.

---

## Voice routing - operator or brand?

Before loading any profile, decide which voice this output should use.

### Step 1 - Check if brands are set up

Run: `python scripts/list-brands.py`

If the script exits 0 with no output, OR the script does not exist, OR the `brands/` directory does not exist: skip to operator voice. No routing decision needed.

If the script lists 1+ brands: continue.

### Step 2 - Infer the speaker from task context

Look at how the user phrased the task. Apply these signals in order:

1. **Explicit brand mention** - the user said "for `<brand>`", "as `<brand>`", "in `<brand>`'s voice", or named a brand display_name that matches a slug. Use that brand's voice.
2. **Explicit personal mention** - the user said "for me", "my personal", "in my voice", "for my LinkedIn", "for my CV". Use operator voice.
3. **Channel implies brand** - "Instagram caption" + user runs a brand with instagram in `channels.primary` = likely brand voice. "My LinkedIn" = operator. "Customer reply" = brand if a brand owns the customer channel.
4. **Ambiguous** - ask once: "Whose voice for this? (you / `<brand 1>` / `<brand 2>` / ...)"

If only one brand is set up and the task is clearly brand-oriented (customer reply, brand social, ad copy), it is safe to pick that brand without asking - but still mention which voice was chosen in the output preamble so the user can correct.

If multiple brands are set up and the task could plausibly belong to any of them, ALWAYS ask. Do not guess.

### Step 3 - Load the chosen profile

- Operator: read `core/voice-profile.yml`. Run `python scripts/check-voice-ready.py` first.
- Brand: read `brands/<slug>/voice.yml` and `brands/<slug>/positioning.yml`. Run `python scripts/check-brand-voice-ready.py --brand <slug>` first.

If the readiness check fails, surface the message verbatim and ask the user to either fix it or proceed with the anti-AI baseline only (clearly labelled).

### Step 4 - Apply register adjustments (brand voice only)

Brand voice profiles include a `register` field that relaxes a small set of baseline sub-rules. Operator voice has an implicit register of `plain-direct` and needs no adjustment. For the per-register allowances, read the "Register adjustments" section of `references/profile-rules.md`. The hard floor (banned phrases, no em dashes, no rule-of-three by default) always applies.

---

## Communication style preference

Before applying the voice profile, read `rules/operating-rules.md`. The setup wizard captures the founder's communication style in Phase 0.7 as `direct` or `detailed`. This is in addition to `voice.rhythm` from the voice profile.

- **`direct`**: prefer short paragraphs. Lead with the answer. Cut warmup. Default volume budget for any piece is the lower bound of the platform norm.
- **`detailed`**: longer setup is allowed. Build context before the point if the topic warrants it. Default volume budget for any piece is the upper bound.

`voice.rhythm` controls sentence length. Communication style controls the volume budget for the whole piece. Both apply.

If `rules/operating-rules.md` is missing or the style is not captured, default to `direct`.

---

## How this skill works

`core/voice-profile.yml` is generated by the voice interview during setup. It captures sentence rhythm, opening style, closings, vocabulary, punctuation, contractions, person, reading level, hedging, buyer language, and reference samples. When you write, you read the profile and apply each setting. The reference samples are the ground truth - if the rules and the samples disagree, the samples win.

The full per-setting interpretation lives in `references/profile-rules.md`. Read it when you need to turn a profile value into a concrete writing choice.

If `buyer_language` is present, use it to choose hooks, examples, and plain problem statements. Do not clean the buyer's phrases into polished marketing copy. The rough wording is often what makes the output feel specific.

---

## Universal rules (apply regardless of profile)

These rules are not optional. They apply to every voice profile because they're the universal anti-AI baseline.

### Punctuation

- Simple hyphens (-) only. No em dashes. No en dashes. Maximum two hyphens per piece.
- No semicolons unless the user's voice profile explicitly enables them.
- No triplet lists (rule of three) unless the user's profile enables them.
- Parentheses are fine for asides if the profile allows them.

### Banned phrase patterns (never)

- "It's not [X] - it's [Y]." (negation-contrast formula)
- "Not just [X], but [Y]."
- "In a world where..."
- "Most people [common thing]. The few who [better thing]."
- "Here's the truth: [obvious statement]."
- "Let's walk through..." / "Let's break this down..."
- "In conclusion..." / "To summarize..."
- "It's worth noting that..."
- Any meta-commentary that announces what's coming instead of delivering it.

### Banned words (always)

Use the universal blacklist in `templates/rules/writing-style.md`. The user's profile may add more. The user's profile cannot remove from that list.

### Structure

- Sentence length varies. Short. Then a longer one that builds context. Then medium.
- Paragraph length varies. One sentence. Then five.
- Opening variation. Don't start every sentence with the subject.
- No perfect parallel structure. Let constructions be slightly asymmetric.

### Honesty

- Don't fabricate experience, numbers, outcomes, or stories. If the user asks for a piece that needs a fact you don't have, ask them for it. Don't invent.
- If the user's profile says they hedge ("maybe", "I think"), keep the hedging. AI doesn't hedge. Humans do.

---

## Profile-driven rules (apply per profile)

Read `core/voice-profile.yml`, then read `references/profile-rules.md` for how to apply each setting - sentence rhythm, opening style, closing style, person, contractions, hedging, reading level, custom vocabulary, and reference samples. Each field maps to a concrete writing choice there. The reference samples are the ground truth: if the rules and the samples diverge, the samples win.

---

## Self-check (run before delivering output)

1. Read it aloud (mentally). Does the rhythm match `voice.rhythm`?
2. Scan for banned words (universal + profile-specific). Replace every match.
3. Count hyphens. More than two? Cut back.
4. Check for triplet lists. Break to two or four unless the profile enables triplets.
5. Negation-contrast scan. Kill every "It's not X - it's Y."
6. Kill meta-commentary.
7. Compare opening to `voice.opening_style`. Mismatch? Rewrite the opening.
8. Compare closing to `voice.closing_style`. Mismatch? Rewrite the closing.
9. Compare a few sentences to the reference samples. Does it sound like the user?
10. Final test: would the user's friend recognize this as their writing?

If any check fails, rewrite. Do not ship.

---

## Failure modes to watch

- **Defaulting to AI-corporate voice.** When you don't have a clear profile setting, you default to AI-polite-corporate voice. This is the wrong default. Default to the universal anti-AI baseline instead.
- **Ignoring the samples.** The profile rules are the map. The samples are the territory. When you only follow the rules, the output sounds technically correct and humanly wrong.
- **Over-correcting natural patterns.** Some users say "alot" or "coz" or break grammar in specific ways on purpose. The profile captures these as `voice.idiosyncrasies`. Respect them. Don't tidy them up.
- **Mismatching length.** A LinkedIn post and a cover letter use the same voice but different lengths. The profile gives you the voice. The platform gives you the length. Don't blur them.

---

## Voice profile as living document

`core/voice-profile.yml` is meant to evolve. After every 5 to 10 pieces of generated content, ask the user:

> Is this still sounding like you? Anything you'd change in the profile?

If they say yes, run a 2-minute mini-interview and update the profile. The voice gets sharper over time.
