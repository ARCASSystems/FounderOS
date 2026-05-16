"""
Formats audit_findings.json into a GitHub issue body.
No Claude. No API key. Plain markdown from raw grep results.
Piped into `gh issue create --body-file -` by the audit workflow.
"""
import json
import os
import tempfile
from pathlib import Path


def findings_path() -> Path:
    """Mirror of the helper in audit.py so both scripts agree on the path
    and so local Windows runs do not break on a hardcoded /tmp/."""
    configured = os.environ.get("AUDIT_FINDINGS_PATH")
    if configured:
        return Path(configured)
    if os.name == "nt":
        return Path(tempfile.gettempdir()) / "audit_findings.json"
    return Path("/tmp/audit_findings.json")

SEVERITY = {
    "pii_names": "CRITICAL",
    "internal_ids": "CRITICAL",
    "internal_codenames": "HIGH",
    "old_namespace": "MEDIUM",
    "stale_version": "MEDIUM",
}

HINT = {
    "pii_names": "Personal names / private event names in a public repo. Remove or replace with generic placeholders.",
    "internal_ids": "Private Notion collection IDs or internal UUIDs. Delete the line entirely - do not replace.",
    "internal_codenames": "Internal codenames leaking publicly. Replace with `FounderOS`.",
    "old_namespace": "Deprecated `/personal-os:` namespace. Replace with `/founder-os:`.",
    "stale_version": "Stale `1.0.1` version string or `15 skills` count. Update to match VERSION file.",
}


def main() -> None:
    findings = json.loads(findings_path().read_text())
    scan_window = findings.get("scan_window")

    lines = [
        f"## FounderOS Integrity Audit",
        f"",
    ]
    if scan_window:
        since = scan_window.get("since", "unknown window")
        commits = scan_window.get("commits_scanned", 0)
        lines.append(
            f"> Weekly digest · window: {since} · {commits} commit(s) scanned · ref `{findings['ref']}`"
        )
    else:
        short_sha = findings["commit"][:8]
        lines.append(
            f"> Commit `{short_sha}` · actor **{findings['actor']}** · ref `{findings['ref']}`"
        )
    lines += [
        f"> Opened automatically by `.github/workflows/founderos-audit.yml`.",
        f"> Maintainer fix procedure: `.github/scripts/fix-audit.md`.",
        f"",
    ]

    leakage = findings.get("leakage_findings", [])
    if leakage:
        sorted_findings = sorted(
            leakage,
            key=lambda f: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}.get(SEVERITY.get(f["check"], "MEDIUM"), 2),
        )
        lines.append("## Findings")
        for f in sorted_findings:
            sev = SEVERITY.get(f["check"], "MEDIUM")
            hint = HINT.get(f["check"], "Review and remove flagged content.")
            lines.append(f"")
            lines.append(f"### `{f['check']}` - {sev} · {f['count']} match(es)")
            lines.append(f"Pattern: `{f['pattern']}`")
            lines.append(f"What to do: {hint}")
            lines.append(f"")
            lines.append(f"```")
            for m in f["matches"][:8]:
                lines.append(m)
            lines.append(f"```")

    high_impact = findings.get("touched_high_impact", [])
    if high_impact:
        lines.append("")
        lines.append("## High-impact path changes")
        lines.append("These paths were modified - verify the change was intentional:")
        for p in high_impact:
            lines.append(f"- `{p}`")

    lines += [
        "",
        "---",
        "## Fix checklist",
    ]
    for f in leakage:
        lines.append(f"- [ ] Fix `{f['check']}` ({f['count']} match(es))")
    for p in high_impact:
        lines.append(f"- [ ] Verify `{p}` change is intentional")
    lines += [
        "- [ ] Re-run `python3 .github/scripts/audit.py` locally - confirm zero findings",
        "- [ ] Commit, push, close this issue",
        "",
        "*Detection by `.github/scripts/audit.py` · Maintainer fix procedure in `.github/scripts/fix-audit.md`*",
    ]

    print("\n".join(lines))


if __name__ == "__main__":
    main()
