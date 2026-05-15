#!/usr/bin/env python3
"""Pre-commit hook: scans staged diff or commit message for private-name patterns.

Two modes:
    --staged          Read `git diff --cached --no-color`, scan added lines
                      for pattern hits, exit 1 on any match.
    --message <path>  Read commit message file at <path>, scan, exit 1 on match.

Patterns are read from scripts/private-name-patterns.txt (one regex per line;
# comments and blank lines ignored). If the file does not exist, exit 0 silently
(operator-installed; contributors without the file get a no-op).

Test seam: set PRIVATE_NAME_PATTERNS_FILE env var to override the default path.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


def load_patterns(patterns_file: Path) -> list[re.Pattern[str]]:
    if not patterns_file.exists():
        return []
    patterns = []
    for line in patterns_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append(re.compile(line))
        except re.error:
            pass
    return patterns


def scan_text(text: str, patterns: list[re.Pattern[str]]) -> list[str]:
    offending: list[str] = []
    for line_num, line in enumerate(text.splitlines(), 1):
        for pat in patterns:
            if pat.search(line):
                offending.append(f"  line {line_num}: {line.rstrip()}")
                break
    return offending


def get_staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached", "--no-color"],
        text=True,
        capture_output=True,
    )
    return result.stdout


def resolve_patterns_file() -> Path:
    override = os.environ.get("PRIVATE_NAME_PATTERNS_FILE")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "private-name-patterns.txt"


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(
            "Usage: check-private-names.py --staged | --message <path>",
            file=sys.stderr,
        )
        return 1

    patterns_file = resolve_patterns_file()
    patterns = load_patterns(patterns_file)
    if not patterns:
        return 0

    if args[0] == "--staged":
        diff = get_staged_diff()
        added_lines = "\n".join(
            line[1:]
            for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        offending = scan_text(added_lines, patterns)
        if offending:
            print(
                "BLOCKED: private-name patterns detected in staged diff:",
                file=sys.stderr,
            )
            for line in offending:
                print(line, file=sys.stderr)
            return 1
        return 0

    if args[0] == "--message" and len(args) >= 2:
        msg_path = Path(args[1])
        try:
            text = msg_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Could not read commit message at {msg_path}: {exc}", file=sys.stderr)
            return 1
        offending = scan_text(text, patterns)
        if offending:
            print(
                "BLOCKED: private-name patterns detected in commit message:",
                file=sys.stderr,
            )
            for line in offending:
                print(line, file=sys.stderr)
            return 1
        return 0

    print(
        "Usage: check-private-names.py --staged | --message <path>",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
