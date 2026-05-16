"""
FounderOS integrity audit.

Two run modes:
- Default: scan HEAD~1..HEAD diff. Used by local `python3 audit.py` runs
  (per `.github/scripts/fix-audit.md`) and as a fallback.
- `--since <git-date>`: scan all commits in the given window. Used by the
  weekly digest cron job in `.github/workflows/founderos-audit.yml`.

Always runs the leakage-pattern scan against the current working tree.
Writes findings JSON and sets the has_findings GHA output.
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

LEAKAGE_PATTERNS = [
    ("old_namespace", r"/personal-os:"),
    ("stale_version", r"15 skills|1\.0\.1"),
]

HIGH_IMPACT_PATHS = [".claude-plugin/", "LICENSE", "README.md"]

INCLUDE_GLOBS = ["*.md", "*.json", "*.sh", "*.yaml", "*.yml", "*.txt"]
EXCLUDED_DIRS = {".git", ".github"}

# Empty-tree SHA - used when HEAD has no parent (first commit)
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def load_private_patterns() -> list[tuple[str, str]]:
    """Load private leakage patterns without committing the sensitive tokens."""
    raw = os.environ.get("FOUNDEROS_PRIVATE_AUDIT_PATTERNS", "").strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("FOUNDEROS_PRIVATE_AUDIT_PATTERNS must be valid JSON") from exc

    patterns: list[tuple[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each private audit pattern must be an object")
        label = str(item.get("label", "")).strip()
        pattern = str(item.get("pattern", "")).strip()
        if not label or not pattern:
            raise ValueError("Each private audit pattern needs label and pattern")
        patterns.append((label, pattern))
    return patterns


def should_scan(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    return any(path.match(glob) for glob in INCLUDE_GLOBS)


def repo_root() -> Path:
    """Resolve the repo root via git so local subdirectory runs scan the right
    tree. Falls back to the current working directory in CI where the checkout
    root is already CWD."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode == 0:
            top = result.stdout.strip()
            if top:
                return Path(top)
    except FileNotFoundError:
        pass
    return Path(".").resolve()


def scan_pattern(label: str, pattern: str, root: Path) -> dict | None:
    regex = re.compile(pattern)
    matches: list[str] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file() or not should_scan(path.relative_to(root) if path.is_absolute() else path):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_no, line in enumerate(lines, start=1):
            if regex.search(line):
                try:
                    display_rel = path.relative_to(root).as_posix()
                except ValueError:
                    display_rel = path.as_posix()
                display_path = "./" + display_rel
                matches.append(f"{display_path}:{line_no}:{line}")

    if matches:
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

    # First commit - diff against empty tree
    result = subprocess.run(
        ["git", "diff", "--name-only", EMPTY_TREE, "HEAD"],
        capture_output=True, text=True,
    )
    return [f for f in result.stdout.strip().splitlines() if f] if result.returncode == 0 else []


def get_changed_files_since(since: str) -> tuple[list[str], int]:
    """Return (unique changed file paths, commit count) in the window."""
    result = subprocess.run(
        ["git", "log", f"--since={since}", "--name-only", "--pretty=format:%H"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return [], 0
    lines = [line for line in result.stdout.splitlines() if line]
    commits = [line for line in lines if re.fullmatch(r"[0-9a-f]{40}", line)]
    files = sorted({line for line in lines if line and not re.fullmatch(r"[0-9a-f]{40}", line)})
    return files, len(commits)


def set_gha_output(key: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as fh:
            fh.write(f"{key}={value}\n")
    else:
        print(f"OUTPUT: {key}={value}")


def findings_path() -> Path:
    configured = os.environ.get("AUDIT_FINDINGS_PATH")
    if configured:
        return Path(configured)
    if os.name == "nt":
        return Path(tempfile.gettempdir()) / "audit_findings.json"
    return Path("/tmp/audit_findings.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="FounderOS integrity audit.")
    parser.add_argument(
        "--since",
        default=None,
        help=(
            "git-date window (e.g. '7 days ago'). Scans all commits in the "
            "window for high-impact path changes. Without this flag, scans "
            "HEAD~1..HEAD only."
        ),
    )
    args = parser.parse_args()

    root = repo_root()
    leakage_findings = []
    for label, pattern in [*LEAKAGE_PATTERNS, *load_private_patterns()]:
        result = scan_pattern(label, pattern, root)
        if result:
            leakage_findings.append(result)

    if args.since:
        changed_files, commit_count = get_changed_files_since(args.since)
        scan_window = {"since": args.since, "commits_scanned": commit_count}
    else:
        changed_files = get_changed_files()
        scan_window = None

    touched_high_impact = [
        p for p in HIGH_IMPACT_PATHS
        if any(f == p or f.startswith(p) for f in changed_files)
    ]

    has_findings = bool(leakage_findings or touched_high_impact)

    output = {
        "commit": os.environ.get("GITHUB_SHA", "unknown"),
        "actor": os.environ.get("GITHUB_ACTOR", "unknown"),
        "ref": os.environ.get("GITHUB_REF", "unknown"),
        "scan_window": scan_window,
        "changed_files": changed_files,
        "touched_high_impact": touched_high_impact,
        "leakage_findings": leakage_findings,
        "has_findings": has_findings,
    }

    output_path = findings_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2))
    set_gha_output("has_findings", "true" if has_findings else "false")

    if has_findings:
        window_note = f" (window: {args.since})" if args.since else ""
        print(
            f"::warning::Audit flagged {len(leakage_findings)} leakage pattern(s) "
            f"and {len(touched_high_impact)} high-impact path change(s){window_note}"
        )
        for f in leakage_findings:
            print(f"  - {f['check']}: {f['count']} match(es)")
        for p in touched_high_impact:
            print(f"  - High-impact path modified: {p}")
    else:
        print("Audit passed. No findings.")


if __name__ == "__main__":
    main()
