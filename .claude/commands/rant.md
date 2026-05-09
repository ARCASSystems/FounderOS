---
description: Capture a raw rant. Say "I want to rant" or "let me dump something" (or run /founder-os:rant). Captures the raw voice dump verbatim into brain/rants/ with no structure asked. The /dream command processes rants later.
---

# Rant

The user just dropped a rant. Voice-to-text, long, tangential, conversational. The volume is the thinking. Capture it verbatim. Do not summarise. Do not ask for structure. Do not ask follow-up questions.

## Procedure

1. Read the user's rant text (whatever follows `/rant`).
2. Determine today's date in the user's timezone. Look up timezone from `core/identity.md`. If not set, default to local system time.
3. Determine the rants file path: `brain/rants/<YYYY-MM-DD>.md`.
4. If the file does not exist, create it with this header:

   ```markdown
   # Rants - <YYYY-MM-DD>
   ```

5. Prepend a new entry to the file (newest on top, after the header):

   ```markdown
   ---
   captured: <ISO 8601 timestamp with timezone offset>
   processed: false
   ---

   <verbatim rant text>

   ---
   ```

6. Confirm in one line: "Captured. <N> rants today. /dream when ready." Do not summarise the rant content.

## Rules

- Do not edit the rant text. Spelling errors, run-on sentences, voice-to-text artifacts stay.
- Do not extract action items inline. That is `/dream`'s job.
- Do not ask the user clarifying questions about the rant.
- Do not exceed two lines of output.
