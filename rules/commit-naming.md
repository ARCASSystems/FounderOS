# Commit Naming Rule

Public repo commits are read by visitors who do not have your context. The subject line states **what changed for the user**, not what was edited internally.

## The rule

1. Subject line states the user-visible change in plain language. 72 characters or fewer.
2. Body explains why the change matters and the user impact. Optional but encouraged for any commit a visitor might want to understand.
3. No version numbers as the primary subject. `v1.4.3` alone is meaningless to a visitor.
4. No tool-jargon-first subjects. `audit fixes` says nothing.
5. No AI attribution. No `Co-authored-by: Claude`, no Generated-with footer, ever.
6. Present tense. User-noun first when possible.

## Examples

**Bad subjects (the pattern this rule corrects):**
- `fix: v1.4.2 - audit fixes, Windows hooks, voice fallback, bash decay scanner`
- `feat: v1.4.0 - wiki graph builder + brain substrate`
- `chore: drop legacy internal name from public docs`

**Good subjects (the target pattern):**
- `Windows users now get the session brief without git-bash`
- `Wiki graph builds after every session that adds cross-references`
- `Setup wizard no longer leaks legacy internal naming`

The pattern: **what visible thing now works, or no longer breaks, for someone who installs this**.

## When a commit bundles multiple changes

If you have to ship N unrelated fixes in one commit, the subject names the **most user-visible** one. The body lists the rest.

If the bundle has no single most-visible change, split the commit.

## Banned patterns

- Bare version bumps as subject (`v1.4.3`)
- Tool jargon as primary subject (`audit fixes`, `hook copy`, `bash decay scanner regex`)
- AI attribution trailers
- Em or en dashes in subject or body. Hyphens only, with spaces around them.
- Banned words from `templates/rules/writing-style.md`

## Reference

Cross-linked from `CLAUDE.md` and `AGENTS.md` so every agent operating in this repo reads it before composing commits.
