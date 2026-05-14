---
title: FounderOS v1.23 deferred decisions
date: 2026-05-15
status: documented (not findings)
---

# v1.23 deferred decisions

Items raised by review (Codex final-release verdict on v1.22.0, follow-up
verdict on v1.23.0) that we deliberately did NOT fix. Documented here so a
future review does not flag them as oversights.

## 1. Git author email visible in commit history

**What:** Every commit since the repo was created shows author
`ARCASSystems <2547468@gmail.com>`. The local part of that email is also
one of the private tokens the v1.22 sweep regex looked for, so it appears
on every commit's author and committer line in `git log`.

**Why we didn't fix:** Fixing requires a destructive history rewrite
(filter-branch / git-filter-repo / force-push). The email is the
operator's actual public git identity; replacing it across history would
break commit hashes and any external references to them.

**How to apply:** Treat this as the public git identity for ARCAS Systems
on this repo. A future maintainer who chooses to rewrite history can do
so as a one-time operation on a tagged commit (cut a fresh history at
`v1.22.0` and force-push), but that is out of scope for routine patches.

## 2. "v1.22 is the final feature release" framing

**What:** README and `skills/index.md` describe v1.22 as the final
feature release. v1.23 has shipped since.

**Why we didn't change the framing:** It is still accurate. v1.23 ships
patches only (privacy sweeps, false-positive closures, hook fixes). No
new skills, commands, or features. The framing was tightened in v1.23
to say "v1.22 *was* the final feature release; v1.23 ships review-driven
patches only" but the underlying claim stands.

**How to apply:** Do not re-flag this as drift. If a future patch
release adds a new skill or command, the framing must move with it.

## 3. `tests/test_menu.py:195` em-dash

**What:** `tests/test_menu.py:195-196` contains the literal em-dash and
en-dash characters inside `assertNotIn` checks. A sweep for em-dashes
will surface this file.

**Why we didn't fix:** The em-dash characters are the assertion targets;
removing them would break the test that enforces "no em-dashes in menu
output." This is correct usage, not a violation.

**How to apply:** When sweeping for em-dashes, exclude
`tests/test_menu.py` from the sweep, or treat that file's matches as
expected.

## 4. `notes/` and `traces/` retention policy

**What:** Codex v1.22 review Finding 18 raised whether internal review
artifacts (`notes/v1.7-*.md`, `traces/v121-*.md`, `traces/v122-skill-audit.md`)
belong in a public tagged release.

**Why we kept them:** `traces/README.md` documents that these traces
are retained for auditability and as a fork-maintainer reference for
what was reviewed and why. They are not product documentation; they are
review provenance.

**How to apply:** A future final release may choose to drop `notes/` and
`traces/` from the tagged tarball without removing them from git
history. That is a separate decision and not in scope for v1.23 patches.

## Review-process commitment

Going forward, any item documented in this file is not a finding. If a
review verdict flags one of these items, the response is to point to
this file rather than re-fix it. A new finding is something not yet
documented here.
