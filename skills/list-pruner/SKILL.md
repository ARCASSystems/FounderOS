---
name: list-pruner
description: Clean a contact list before outreach - remove duplicate emails, flag missing fields, and score each row High / Medium / Low. Say "prune this list", "clean my contact list", "remove duplicates", "score this list", or run /founder-os:list-pruner. Accepts a CSV path or a pasted table. Returns a clean markdown table; writes a file only if you ask.
why: "A list full of duplicates and half-filled rows turns a focused outreach week into busywork. Scoring and de-duping it up front means every row you contact is worth contacting."
summary: "Clean a contact list before outreach - de-dupe, flag gaps, score each row."
enhance: "Run it before any outreach push, not after - the High, Medium, Low score is most useful when it decides who you contact first, not when you are already halfway down the list."
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep"]
mcp_requirements: []
---

# List Pruner

Prepare a contact list for outreach planning. The skill removes duplicate emails, flags missing fields, assigns a quality score, and returns a clean markdown table or CSV-ready output.

## Pre-flight

If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`

## When to invoke

Invoke when you provide a CSV, a pasted table, or a path to a contact list before outreach. Also invoke during a list review when a campaign list may contain stale rows.

## Protocol

1. Read the input list from a CSV path or a pasted table.
2. Confirm the required columns are present, or map similar columns to `name`, `email`, `company`, `title`, `persona`, and `signal`.
3. Normalize emails to lowercase.
4. Remove duplicate rows by email. Keep the row with the most filled fields.
5. Flag any missing email, company, title, persona, or signal.
6. Score each row:
   - `High` when email, company, title, persona, and signal are all present.
   - `Medium` when email is present and exactly one non-email field is missing.
   - `Low` when email is missing, or two or more non-email fields are missing.
7. Return a clean table with `score` and `flag` columns.
8. Write a clean CSV only if you ask for a file. If writing, confirm the output path first.
9. Append a one-line trace to `brain/log.md` (`#acted` tag) recording input rows, clean rows, and duplicates removed.

<!-- private-tag: not applicable: the brain/log.md write is a computed run trace (row counts and duplicates removed), not user-provided speech, so the private-tag filter does not apply here. -->

## Output schema

```yaml
list_pruner:
  status: ok | blocked
  input_rows: <number>
  clean_rows: <number>
  duplicates_removed: <number>
  flagged_rows: <number>
  output_table:
    - name: "<name>"
      email: "<email@example.com>"
      company: "<company>"
      title: "<title>"
      persona: "<persona>"
      signal: "<signal>"
      score: High | Medium | Low
      flag: "<none | missing_email | missing_company | missing_title | missing_persona | missing_signal>"
```

## Failure modes

- **No email column:** proceed only if you confirm the outreach channel is not email.
- **Unreadable CSV:** stop and ask for a pasted table or a valid path.
- **Empty list:** stop with `blocked_empty_list`.
- **Real credentials found in the file:** stop and report the path. Do not echo the secret.
- **File write requested but output path missing:** ask for a path before writing.

## Composes with

- `linkedin-network-scan`, which produces a ranked worklist from your LinkedIn export - this skill cleans a list assembled by hand or from another source before you act on it.
- `email-drafter`, which drafts outreach to the cleaned rows one at a time.
- `context/leads.md`, the OS leads file. After pruning, the High-scored rows are the natural candidates to add as new `Stage: Raw` leads. The skill does not auto-write that file; it surfaces the candidates and you add them through your normal leads flow.

## Free-tier path

Free-tier users paste the CSV contents straight into chat. The model returns the clean table for manual copy into a spreadsheet or into `context/leads.md`. File writes are optional, not required.

## Worked example

Input:

```csv
name,email,company,title,persona,signal
Jordan Lee,jordan@example.com,Example Labs,Head of Ops,operator,hiring ops roles
Jordan Lee,JORDAN@example.com,Example Labs,,operator,hiring ops roles
Mira Patel,mira@example.com,Northstar Demo,Founder,builder,posted about outbound
```

Output:

```yaml
list_pruner:
  status: ok
  input_rows: 3
  clean_rows: 2
  duplicates_removed: 1
  flagged_rows: 0
  output_table:
    - name: Jordan Lee
      email: jordan@example.com
      company: Example Labs
      title: Head of Ops
      persona: operator
      signal: hiring ops roles
      score: High
      flag: none
    - name: Mira Patel
      email: mira@example.com
      company: Northstar Demo
      title: Founder
      persona: builder
      signal: posted about outbound
      score: High
      flag: none
```

## Cross-reference

- `skills/linkedin-network-scan/SKILL.md` - builds a ranked list from your own network export.
- `skills/email-drafter/SKILL.md` - drafts the outreach to each clean row.
- `context/leads.md` - where High-scored rows become tracked leads.
