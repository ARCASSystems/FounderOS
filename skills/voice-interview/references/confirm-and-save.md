# Phase 4 - Confirm and save

Load this when you reach Phase 4.

Show this exact block (filled with the captured values):

> Part 3 of 3 - Confirm and save.
>
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
