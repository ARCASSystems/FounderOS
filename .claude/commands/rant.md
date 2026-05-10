---
description: Capture or route a raw rant. Say "I want to rant" or "let me dump something" (or run /founder-os:rant). Asks one short question, then routes to a decision, draft, plan, or plain capture.
---

# Rant

The user just dropped a rant. Voice-to-text, long, tangential, conversational. The volume is the thinking. Keep the raw text intact, but do not assume capture is enough when the rant is asking for action.

Ask exactly one qualifying question:

> Does this need a decision, a draft, a plan, or just to be captured?

Do not run a multi-turn intake. If the user answers with more context, extract the route from that answer and proceed.

## Routing

- `decision` -> invoke `decision-framework` with the rant as the decision context.
- `draft` -> choose the writing skill from the rant: `linkedin-post` for post or content, `email-drafter` for email or follow-up, `proposal-writer` for proposal or scope, `client-update` for client status. If unclear, default to `email-drafter` when the rant names a lead or client follow-up; otherwise default to `linkedin-post`.
- `plan` -> invoke `priority-triage` if the rant is about what to do next, or `forcing-questions` if it is about starting a new initiative.
- `capture`, `just capture`, unclear, or skipped answer -> use the capture procedure below.
- `log` -> invoke `brain-log` instead of writing to `brain/rants/`.

## Capture procedure

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
- Ask only the one qualifying question above. Do not interview the user.
- If the user chooses a route, do not also write the rant file unless they asked to capture it too.
- If the user says "just capture", keep the old dump path and let `/dream` process it later.
- Do not exceed two lines of output.
