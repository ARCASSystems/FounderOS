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

## Release commits

A version bump is still a commit, so it follows the same rule. The subject is the user-visible headline of the release in present tense, with no version number. The version lives in the git tag and, when useful, the body.

**Release commit shape:**
- Subject: the single most user-visible thing this release delivers, 72 characters or fewer.
  Good: `ZIP installs work end to end and updates keep your edits`
  Bad: `v1.42.0` or `v1.42.0 - release`
- Body: the version on its own line, then the changelog highlights. For example:
  ```
  v1.42.0

  ZIP is a first-class install path. Update proposes migrations instead of
  overwriting founder-authored files. One cross-platform hook dispatcher
  replaces the old shell pairs.
  ```
- Tag: `git tag v1.42.0` carries the version for anyone browsing releases.

Never lead a release subject with the version. `v1.42.0 - release` tells a visitor nothing about what changed.

## Banned patterns

- Bare version bumps as subject (`v1.4.3`)
- Tool jargon as primary subject (`audit fixes`, `hook copy`, `bash decay scanner regex`)
- AI attribution trailers
- Em or en dashes in subject or body. Hyphens only, with spaces around them.
- Banned words from `templates/rules/writing-style.md`

## Push cadence - the rule that stops stale-truth work

This one only applies once your OS lives in more than one place: a copy on your machine plus a synced remote that something else reads (a backup you run routines against, a second machine, a cloud session).

**The rule: push at the end of every session that changed anything.**

The failure it prevents is specific and it is not obvious the first time it bites. Anything reading the remote composes its work from what the remote holds. If you decided something at your desk on Monday and did not push, then Tuesday's remote run rebuilds its picture from Sunday, re-raises the question you already answered, and hands you back work you already did. The answers look confident and they are out of date. You lose trust in the thing before you find the cause.

The same push is your off-site backup, which is the second reason to make it a cadence and not a decision.

Three qualifiers:

- **A public repo is different.** Publishing is an explicit choice every time, never a cadence. This rule is for your own OS, not for anything the world can read.
- **If the push is rejected because the remote moved,** pull with rebase, resolve, push. Never force push.
- **A session that ends without pushing says so, and says why.** Mid-rebase, or you asked it to hold. Silence is what creates the stale-truth case.

If your OS only exists in one place, ignore all of this. It costs nothing to skip and it is the first rule to adopt the day you sync.

## Reference

Cross-linked from `CLAUDE.md` and `AGENTS.md` so every agent operating in this repo reads it before composing commits.
