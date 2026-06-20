---
name: reconnect-prompt
description: Turn an expired-token or 401 failure into one copy-paste reconnect prompt and log the failed call. Say "the integration broke", "my token expired", "reconnect <tool>", or "I got a 401". Stops the failing action, never retries, never asks for credentials. Routes the failure to the quarantine catch-net so a dead connector does not stay silent.
why: "A connected tool that quietly stops working is the worst failure in an integrated OS - the next run looks fine until you notice a week of missing data. This turns a silent 401 into one visible prompt and one logged entry."
summary: "Turn an expired-token or 401 failure into one copy-paste reconnect prompt."
enhance: "Run it the moment a tool throws a 401 rather than retrying blind - the logged entry is what lets stall detection see the outage instead of mistaking it for a quiet week."
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep"]
mcp_requirements: []
---

# Reconnect Prompt

Runs on: local-writes - creates or edits files in your OS folder; needs an agent with write access.

Handle expired auth for connected tools without silent retries or automatic re-auth. The skill gives you one clear prompt to paste into the relevant tool's reconnect flow and records the failed call so it does not disappear.

## Pre-flight

1. If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
2. Read `stack.json` to resolve which placeholder failed (`{knowledge_base}`, `{email_platform}`, `{calendar}`, `{automation_platform}`, `{crm}`, `{file_storage}`, `{meeting_notes}`, `{prospecting_db}`, `{video_tool}`, `{booking}`, `{primary_channel}`, or another key in that file). If `stack.json` is missing, proceed with the placeholder name the calling skill passed.

## When to invoke

Invoke when an integration-backed action returns any of:

- HTTP 401.
- Expired token.
- Invalid grant.
- Revoked consent.
- Missing refresh token.
- Auth scope no longer valid.

## Protocol

1. Receive the auth failure from the calling skill: source skill, stack key, action attempted, and a one-line error summary.
2. Stop the calling action. Do not retry.
3. Produce one reconnect line you can paste into the tool's reconnect UI.
4. Tell the operator which `stack.json` key failed.
5. Log the failure to the quarantine catch-net (see below).
6. Return control to the calling skill only after the operator confirms the tool is reconnected.

This skill never asks for credentials and never stores tokens.

## Where the failure is logged

The public OS has a silent-failure catch-net at `system/quarantine.md` (template fallback `templates/system/quarantine.md`). Append one `Status: ACTIVE` entry there using the entry format documented in that file: timestamp, source (`reconnect-prompt`), trigger (the action attempted), error (the summary), context (the stack key). The SessionStart brief counts ACTIVE entries, so the dead connector surfaces at the next session.

If neither `system/quarantine.md` nor its template exists on this install, degrade gracefully: produce the reconnect prompt and append a one-line note to `brain/log.md` instead. Do not invent a quarantine file - one line in the log is enough to keep the failure visible.

<!-- private-tag: not applicable: the brain/log.md fallback write is a computed failure trace (the logged 401/auth error), not user-provided speech, so the private-tag filter does not apply here. -->

When the operator confirms the reconnect worked, update that quarantine entry's `Status: ACTIVE` to `Status: RESOLVED <YYYY-MM-DD>` so it stops surfacing.

## Output schema

```yaml
auth_reconnect:
  status: blocked
  source_skill: "<skill-name>"
  stack_key: "<stack.json key>"
  action_attempted: "<one-line action>"
  error_summary: "<short error>"
  reconnect_prompt: "Reconnect <stack_key> for the OS, then rerun <source_skill>."
  log_path: "<path to system/quarantine.md, or brain/log.md if no catch-net exists>"
```

## Failure modes

- **No stack key provided:** ask the calling skill to identify the failed binding before logging anything.
- **No catch-net file:** fall back to a one-line `brain/log.md` entry, never a fabricated path.
- **Operator asks for auto-login:** refuse and restate that reconnect is manual. The skill does not handle credentials.
- **Repeated failure after reconnect:** log a second ACTIVE entry, then ask the operator to inspect the tool's authorized scopes in its own settings UI.
- **Free-tier user has no integration:** there is nothing to reconnect. Return the manual-paste path instead of a reconnect prompt.

## Composes with

Every integration-touching skill should catch auth failures and route here. Expected callers in the public OS:

- `meeting-prep` for `{calendar}` or `{meeting_notes}`.
- `email-drafter` for `{email_platform}`.
- `knowledge-capture` for `{knowledge_base}` when the source lives outside the repo.
- `session-handoff` for `{knowledge_base}` when writing the handoff to a connected store.

## Free-tier path

If the operator is on a free tier with no live connector, there is nothing to reconnect. The calling skill should switch to manual mode: ask the operator to paste the needed data, then continue without tool access. No quarantine entry is needed for an expected manual fallback.

## Worked example

Input:

```yaml
source_skill: meeting-prep
stack_key: "{calendar}"
action_attempted: "list events for 2026-06-02"
error_summary: "HTTP 401 expired token"
```

Output:

```yaml
auth_reconnect:
  status: blocked
  source_skill: meeting-prep
  stack_key: "{calendar}"
  action_attempted: "list events for 2026-06-02"
  error_summary: "HTTP 401 expired token"
  reconnect_prompt: "Reconnect {calendar} for the OS, then rerun meeting-prep."
  log_path: "system/quarantine.md"
```

Quarantine entry written:

```
## 2026-06-02 09:14 - reconnect-prompt - HTTP 401 expired token

**Source:** reconnect-prompt
**Trigger:** meeting-prep tried to list events for 2026-06-02
**Error:** HTTP 401 expired token
**Context:** stack key {calendar}
**Status:** ACTIVE

---
```

## Cross-reference

- `system/quarantine.md` - the silent-failure catch-net this skill writes to.
- `skills/verify/SKILL.md` - the substrate health check that also reads the quarantine count.
- `stack.json` - the placeholder-to-tool bindings the failed key resolves against.
