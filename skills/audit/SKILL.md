---
name: audit
description: Use when the founder asks for OS health, release readiness, or a full audit. Runs readiness, lint, wiki graph state, brain staleness, and voice completeness as one composite report.
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
mcp_requirements: []
---

# Audit

This skill returns one Founder OS health report. It composes five checks that can also run on their own.

## Pre-Flight

If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`

## Checks

Run all five checks. Use the Agent tool to dispatch them in parallel when the environment supports sub-agents: send a single message with multiple Agent tool calls, one per check. If sub-agents are not available (e.g. the platform does not expose the Agent tool), run them in sequence and mark the report `parallel: unavailable`.

1. `readiness-check` - score and next moves.
2. `lint` - broken links, orphans, stale content, provenance, contradictions.
3. `wiki-build` state - read graph counts by default. If the user approves a write, run `/founder-os:wiki-build` first.
4. Brain staleness - count entries past `Decay after`, flags older than Week 3, and rants older than 30 days.
5. Voice completeness - check whether `core/voice-profile.yml` and `core/brand-profile.yml` still look like templates.

## Wiki Write Gate

Audit is read-only by default. `wiki-build` writes to `brain/relations.yaml`, so ask before running it:

`Audit can refresh the wiki graph before scoring. This writes only to brain/relations.yaml. Run wiki-build first? yes / no`

If the user says no, read the existing graph and mark wiki freshness as not refreshed.

## Composite Output

Render only the composite report. Do not paste raw sub-check outputs.

```text
FOUNDER OS HEALTH - <YYYY-MM-DD>
---
Readiness: <score>/100 - <one-line headline>
Wiki: <links count>, <orphans count>, <broken refs count>
Brain: <decay-due count>, <Week 3+ flags>, <stale rants>
Voice: <state>
Parallel: available | unavailable
---
Top 3 actions to lift health:
1. <action>
2. <action>
3. <action>
```

## Brain Staleness Rules

- `Decay after:` date in the past counts as decay-due.
- Any flag marked Week 3, Week 3+, or older than 21 days counts as Week 3+.
- Any file in `brain/rants/` older than 30 days with `processed: false` counts as stale.

## Voice Completeness Rules

Voice is incomplete if:

- `core/voice-profile.yml` is missing.
- It still contains placeholder brackets or template examples.
- It has fewer than 2 writing samples referenced.

Brand is incomplete if:

- `core/brand-profile.yml` is missing.
- Colors, fonts, logo, or document style are still blank placeholders.

## Rules

- Read-only unless the user approves wiki-build.
- The composite report is the only output.
- No em dashes, no en dashes, no banned words.
