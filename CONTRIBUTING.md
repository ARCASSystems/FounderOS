# Contributing to Founder OS

Founder OS is a derived product. The source-of-truth lives in a private repo and ports out to this public one. Issues and PRs are welcome but the bar is high.

## Release posture

FounderOS ships in deliberate increments. Each release closes a gap the previous one made visible. New features land when there is a real gap worth closing — not on a calendar. The upstream private repo holds the source of truth and ports out manually.

### Issues we will respond to

- **Install breakage** on macOS, Linux, or Windows
- **Hook breakage** (SessionStart, PostToolUse, Stop)
- **Security issues** (report per SECURITY.md, not as a public issue)
- **Documentation that contradicts the code**
- **Skill gaps** that affect general operators, not ARCAS-specific delivery

### Issues we will be slow on

- **Feature requests outside the ROADMAP scope.** See ROADMAP.md for the direction. If your idea fits, open an issue. If it does not, fork.
- **Vendor-specific integrations** beyond the existing MCP set.
- **Usage questions** that the README, docs/, or skill bodies already answer.

### Community forks are encouraged

If you build something on top of FounderOS, open a discussion thread linking your fork. We don't merge into this repo, but we'll point others to your work.

## What we accept

- **Bug reports (preferred):** open an issue with the reproduction steps and the install path you used (Path A, B, D, or E from `docs/install.md`).
- **Documentation fixes:** typo, broken link, unclear instruction. Open a PR.
- **Skill improvements that are general-purpose.** ARCAS-specific code stays in the private source.

## What we do not accept

- New skills or major architecture changes via PR. These get triaged in the upstream private repo first. Open an issue describing the gap and we will respond.
- Vendor-specific integrations beyond the existing MCP set. Open an issue and let us see if it fits the roadmap.
- AI-attributed commits. No `Co-authored-by: Claude` or generated-with footers. The operator owns the work product.

## Voice and writing rules

All written output (commit messages, README edits, skill docs, issue replies) follows `templates/rules/writing-style.md`. No em or en dashes. No banned words. Commit messages follow `rules/commit-naming.md` (subject states the user-visible change, not internal mechanics).

## Reporting

For security issues, see `SECURITY.md`.
For everything else, open an issue or email `solutions@arcassystems.com`.
