"""
FounderOS fix advisor — called by GitHub Actions when audit finds issues.
Reads /tmp/audit_findings.json, calls Claude API, writes /tmp/fix_recommendation.md.
"""
import json
import os
from pathlib import Path

import anthropic

# Per-check remediation playbook — keeps the prompt grounded without hallucinating steps.
FIX_PLAYBOOK: dict[str, str] = {
    "pii_names": (
        "CRITICAL — personal names or private event names in a public repo. "
        "Find every match, delete the line or replace with a generic placeholder. "
        "Check all .md and .json files. Run `git grep` to confirm zero hits before pushing."
    ),
    "internal_codenames": (
        "HIGH — internal codenames are leaking. Replace every occurrence of "
        "'paperclip' or 'founder-os-product' with 'FounderOS' (the public product name). "
        "Bulk-replace with: `grep -rl 'paperclip\\|founder-os-product' . | xargs sed -i 's/paperclip/FounderOS/g; s/founder-os-product/FounderOS/g'`"
    ),
    "internal_ids": (
        "CRITICAL — private Notion collection IDs or internal UUIDs are exposed. "
        "These can be used to access private workspaces. Remove the entire line for each match. "
        "Do not replace with a placeholder — omit entirely."
    ),
    "old_namespace": (
        "MEDIUM — deprecated '/personal-os:' command namespace is present. "
        "Replace all occurrences with '/founder-os:' to match the v1.1.0 public naming. "
        "Run: `grep -rl '/personal-os:' . | xargs sed -i 's|/personal-os:|/founder-os:|g'`"
    ),
    "stale_version": (
        "MEDIUM — stale references ('15 skills' or version '1.0.1') found. "
        "Update skill count by running `ls skills/ | wc -l` and replacing the number. "
        "Update version strings to match the current value in the VERSION file."
    ),
}

SYSTEM_PROMPT = """\
You are a senior engineer reviewing an automated integrity audit for FounderOS, \
a public open-source Claude Code plugin. Your job is to write a clear, actionable \
GitHub issue body in markdown so the repo owner knows exactly what to fix and how.

Rules:
- Severity order: CRITICAL (PII, private IDs) > HIGH (internal codenames) > MEDIUM (stale refs, namespaces)
- Name the exact files and line numbers from the findings — do not be vague
- Provide copy-paste shell commands wherever possible
- For high-impact path changes (LICENSE, README, .claude-plugin/), note what to verify, not what to delete
- End with a markdown checkbox checklist the author can tick off as they fix each item
- Total length: under 450 words
- No preamble — start directly with the severity breakdown"""


def build_user_prompt(findings: dict) -> str:
    lines = [
        f"Commit: `{findings['commit']}`",
        f"Actor: {findings['actor']}",
        f"Ref: {findings['ref']}",
        "",
        "## Leakage findings",
    ]

    for f in findings.get("leakage_findings", []):
        playbook = FIX_PLAYBOOK.get(f["check"], "Review and remove flagged content.")
        lines.append(f"\n### {f['check']} — {f['count']} match(es)")
        lines.append(f"Pattern: `{f['pattern']}`")
        lines.append("Sample matches (first 5):")
        for m in f["matches"][:5]:
            lines.append(f"  - `{m}`")
        lines.append(f"\nFix guidance: {playbook}")

    if findings.get("touched_high_impact"):
        lines.append("\n## High-impact path changes")
        lines.append("These paths were modified in this commit and require manual review:")
        for p in findings["touched_high_impact"]:
            lines.append(f"  - `{p}`")

    lines.append(
        "\nWrite the GitHub issue body with a severity breakdown, "
        "file-specific fix steps, and a checkbox checklist."
    )
    return "\n".join(lines)


def main() -> None:
    findings_path = Path("/tmp/audit_findings.json")
    if not findings_path.exists():
        print("No findings file — skipping fix advisor")
        return

    findings = json.loads(findings_path.read_text())

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY secret is not set")

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": build_user_prompt(findings)}],
    )

    recommendation = message.content[0].text
    short_sha = findings["commit"][:8]

    body = f"""\
## FounderOS Integrity Audit — Automated Flag

> Triggered by push `{short_sha}` · actor **{findings['actor']}** · ref `{findings['ref']}`
> Opened automatically by `.github/workflows/founderos-audit.yml`. Close when all fixes are merged.

---

{recommendation}

---
*Fix advisor powered by Claude (`claude-sonnet-4-6`). \
Audit script: `.github/scripts/audit.py`*
"""

    Path("/tmp/fix_recommendation.md").write_text(body)
    print(f"Fix recommendation written ({len(body)} chars)")
    print(f"Claude usage — input: {message.usage.input_tokens}, output: {message.usage.output_tokens}")


if __name__ == "__main__":
    main()
