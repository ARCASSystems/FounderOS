"""
FounderOS integrity audit — runs on every push via GitHub Actions.
Scans for leakage patterns and high-impact path drift.
Writes /tmp/audit_findings.json and sets the has_findings GHA output.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

LEAKAGE_PATTERNS = [
    (
        "pii_names",
        r"Aqsa|Afsha|Bilal|Ashrith|Teja|Surandar|Pupilar|XFest|IKEA|Festival City",
    ),
    ("internal_codenames", r"paperclip|founder-os-product"),
    (
        "internal_ids",
        r"collection://|2c327c182a0f|33127c182a0f|33b27c182a0f|046a7ad8676",
    ),
    ("old_namespace", r"/personal-os:"),
    ("stale_version", r"15 skills|1\.0\.1"),
]

HIGH_IMPACT_PATHS = [".claude-plugin/", "LICENSE", "README.md"]

INCLUDE_GLOBS = ["*.md", "*.json", "*.sh", "*.yaml", "*.yml", "*.txt"]

# Empty-tree SHA — used when HEAD has no parent (first commit)
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def grep_pattern(label: str, pattern: str) -> dict | None:
    cmd = [
        "grep", "-rn",
        "--exclude-dir=.git",
        "--exclude-dir=.github",
    ]
    for glob in INCLUDE_GLOBS:
        cmd += [f"--include={glob}"]
    cmd += ["-E", pattern, "."]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        matches = result.stdout.strip().splitlines()
        return {
            "check": label,
            "pattern": pattern,
            "matches": matches[:10],
            "count": len(matches),
        }
    return None


def get_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        return [f for f in result.stdout.strip().splitlines() if f]

    # First commit — diff against empty tree
    result = subprocess.run(
        ["git", "diff", "--name-only", EMPTY_TREE, "HEAD"],
        capture_output=True, text=True,
    )
    return [f for f in result.stdout.strip().splitlines() if f] if result.returncode == 0 else []


def set_gha_output(key: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as fh:
            fh.write(f"{key}={value}\n")
    else:
        print(f"OUTPUT: {key}={value}")


def main() -> None:
    leakage_findings = []
    for label, pattern in LEAKAGE_PATTERNS:
        result = grep_pattern(label, pattern)
        if result:
            leakage_findings.append(result)

    changed_files = get_changed_files()
    touched_high_impact = [
        p for p in HIGH_IMPACT_PATHS
        if any(f == p or f.startswith(p) for f in changed_files)
    ]

    has_findings = bool(leakage_findings or touched_high_impact)

    output = {
        "commit": os.environ.get("GITHUB_SHA", "unknown"),
        "actor": os.environ.get("GITHUB_ACTOR", "unknown"),
        "ref": os.environ.get("GITHUB_REF", "unknown"),
        "changed_files": changed_files,
        "touched_high_impact": touched_high_impact,
        "leakage_findings": leakage_findings,
        "has_findings": has_findings,
    }

    Path("/tmp/audit_findings.json").write_text(json.dumps(output, indent=2))
    set_gha_output("has_findings", "true" if has_findings else "false")

    if has_findings:
        print(
            f"::warning::Audit flagged {len(leakage_findings)} leakage pattern(s) "
            f"and {len(touched_high_impact)} high-impact path change(s)"
        )
        for f in leakage_findings:
            print(f"  - {f['check']}: {f['count']} match(es)")
        for p in touched_high_impact:
            print(f"  - High-impact path modified: {p}")
    else:
        print("Audit passed. No findings.")


if __name__ == "__main__":
    main()
