# Security Policy

## Reporting a Vulnerability

Email `solutions@arcassystems.com` with:

- A description of the issue
- Reproduction steps if you have them
- Whether the issue is in skills, hooks, the audit workflow, or the plugin manifest

We aim to acknowledge within 48 hours and patch within 7 days for high-severity issues.

## What is in scope

- Code in `skills/`, `.claude/`, `.github/scripts/`
- Plugin manifest files (`plugin.json`, `marketplace.json`)
- Hook scripts and the SessionStart brief

## What is out of scope

- Issues in user-generated content (your own `core/`, `context/`, `brain/` files)
- Issues in third-party MCP servers (report to the MCP authors directly)
- Cosmetic style violations (these are surfaced by the audit workflow, not security)

## Disclosure

We coordinate disclosure with the reporter. Default policy is a 14-day private window before any public fix lands, unless the reporter requests faster.
