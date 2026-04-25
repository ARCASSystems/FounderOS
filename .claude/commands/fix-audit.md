---
description: Read open audit issues from GitHub and fix flagged integrity problems directly in the repo.
allowed-tools: ["Bash", "Read", "Edit", "Grep"]
---

# Fix Audit

Reads open `[Audit]` issues from this repo and applies fixes directly. No API key needed — runs entirely inside your Claude Code subscription.

## Procedure

### 1. Find open audit issues

Run:
```
gh issue list --state open --search "[Audit] in:title" --json number,title,body,createdAt --limit 5
```

If zero issues are returned, reply: `No open audit issues. Repo is clean.` and stop.

If multiple issues exist, pick the most recent one (highest issue number). Show the user the issue title and number before proceeding.

### 2. Parse the findings

Extract from the issue body:
- Each finding block: check name, severity, pattern, and the code matches shown
- The high-impact path changes list (if present)

### 3. Confirm before fixing

Tell the user which findings you are about to fix and how, in one short message. Ask: `Fix all of these now? (yes / no)`

Wait for the reply. If no, stop.

### 4. Apply fixes — one finding at a time

Work through each finding in severity order (CRITICAL first):

**`pii_names`**
- For each match line (format `./path/file.md:42:...`), open the file with Read, identify the exact line, and remove it or replace the name with `[name redacted]` if context requires a placeholder.
- Use Edit to apply.

**`internal_ids`**
- Delete the entire line for each match. These must not appear in any form.
- Use Edit to apply.

**`internal_codenames`** (`paperclip`, `founder-os-product`)
- Replace with `FounderOS` (exact case match). Use Edit with replace_all where appropriate.

**`old_namespace`** (`/personal-os:`)
- Replace with `/founder-os:`. Use Edit with replace_all.

**`stale_version`** (`15 skills`, `1.0.1`)
- `15 skills`: run `ls skills/ | wc -l` to get the real count, then update the number in each match.
- `1.0.1`: read `VERSION` file, replace `1.0.1` with the current version in each match.

**High-impact path changes** (`LICENSE`, `README.md`, `.claude-plugin/`)
- Read the file and summarise the recent change for the user in 2 sentences. Ask if the change was intentional. Do not modify unless the user says so.

### 5. Verify

After all edits, run the audit scan to confirm zero findings:
```
python3 .github/scripts/audit.py
```

If findings remain, repeat step 4 for whatever is left. Do not proceed until the scan is clean.

### 6. Commit and push

Ask: `All clean. Commit and push fixes? (yes / no)`

If yes:
- Stage only the files you edited: `git add <files>`
- Commit with message: `fix: resolve audit flags from issue #<N>`
- Push: `git push -u origin <current-branch>`

Then close the issue:
```
gh issue close <N> --comment "Fixed in $(git rev-parse --short HEAD). Audit scan now passes."
```

### Rules

- Never delete a file — only edit lines within it.
- Never use `git add -A` or `git add .` — stage specific files only.
- Do not push unless the user explicitly confirms in step 6.
- If a match line cannot be parsed (malformed grep output), skip it and tell the user which file to check manually.
- If `gh` is not authenticated, tell the user to run `gh auth login` and stop.
