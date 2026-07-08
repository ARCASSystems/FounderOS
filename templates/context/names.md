# Names glossary

Canonical spellings of the people, companies, and products in your world, plus the ways dictation tools mis-hear them. Every capture pass (catch-up, capture-meeting, ingest) reads this file BEFORE writing any name anywhere, and appends every correction you make - so the same mishearing never survives twice.

## People

| Canonical name | Also heard as | Who they are |
|---|---|---|
| {{FOUNDER_NAME}} | | you |

## Companies and products

| Canonical name | Also heard as | What it is |
|---|---|---|
| {{COMPANY_NAME}} | | your company |

## How the OS uses this file (the rules)

- A name in a capture that matches an entry here (or a listed mishearing) is silently corrected to the canonical spelling.
- A name that matches nothing is written as heard and marked `(sp?)`. The OS asks you about all unknowns in one batch, never one by one.
- When you correct a name, the wrong-to-right pair is appended to the "Also heard as" column. The glossary teaches itself.
- The OS never guesses. A close-but-unlisted name is a question, not a substitution - a confident wrong name in the brain is worse than a marked uncertain one.
