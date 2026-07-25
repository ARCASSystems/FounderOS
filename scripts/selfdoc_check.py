#!/usr/bin/env python3
"""selfdoc_check.py - the self-documentation checker behind rules/os-as-harness.md.

The problem it exists for: a harness only works if a fresh session (or a fresh
human) can open a file and know why it exists and how it is invoked WITHOUT
being told. Two surfaces carry that contract and go stale silently when it
lapses:

  1. Doctrine markdown (rules/, system/, skills/*/SKILL.md) that never states the
     problem it solves. The next session cannot tell load-bearing doctrine from a
     scratch note, so it either ignores the file or misapplies it. The why-first
     convention (rules/entry-conventions.md) fixes this with a one-line `why:` at
     the top. This checker is the half that names the files still missing it.

  2. Substantial scripts whose module docstring does not state the problem, the
     invariants, and how to run it. A 300-line script with a one-line docstring
     is a trap: the next person re-derives its rules from the code instead of
     reading the contract.

Neither surface is validated at write time. This checker reads what is there and
names the gaps. It never edits. It is deliberately forward-only and low-noise: it
exempts thin wrapper scripts (a 10-line helper needs no essay) and caps its
report with honest totals.

It holds itself to its own bar - this docstring is why this file passes the
`code` check.

Invariants: read-only (writes nothing, anywhere), standard library only,
ASCII-safe output, always exits 0. A missing docstring is a readability problem,
never a broken machine, so this reports and never fails a build.

Two subcommands:
  why  : doctrine markdown missing a `why:` field or a why-marker near the top.
         Fix home: add the one-line `why:` (rules/entry-conventions.md).
  code : substantial scripts/*.py whose module docstring misses the bar
         (present, long enough to be a contract, carries a usage or invariant marker).

Usage:
  python scripts/selfdoc_check.py why                 # human report (doctrine md)
  python scripts/selfdoc_check.py code                # human report (scripts)
  python scripts/selfdoc_check.py why --json          # machine form, for /lint
  python scripts/selfdoc_check.py code --json         # machine form, for /verify
  python scripts/selfdoc_check.py both                # both reports, one pass
  python scripts/selfdoc_check.py why --scope all     # add skills/*/SKILL.md
  python scripts/selfdoc_check.py why --root PATH     # alternate root (tests)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ----- why-first (doctrine markdown) -----

# rules/ and system/ carry load-bearing doctrine, so a missing why there is a real
# signal and they are the default scope. skills/*/SKILL.md already carries a
# `description:` (what it does + when it fires), so a why is an enhancement there
# rather than a gap - which is why --scope all is opt-in. The convention is
# forward-only: older files adopt it on next touch, so the default report stays a
# short actionable list instead of a permanent wall of every file ever written.
WHY_MD_GLOBS_CORE = ("rules/*.md", "system/*.md")
WHY_MD_GLOBS_ALL = ("rules/*.md", "system/*.md", "skills/*/SKILL.md")

# Exempt: indexes and READMEs whose entire body IS the why.
WHY_EXEMPT_NAMES = {"index.md", "README.md", "readme.md"}

# A file declares its why with a frontmatter `why:` key OR a marker near the top
# of the body naming the problem. Kept tight so false positives stay rare.
WHY_MARKER = re.compile(
    r"(?im)^\s*(#{1,4}\s*why\b"
    r"|why (this|it) (file )?exists"
    r"|the problem it exists for"
    r"|one page (deciding|that)"
    r"|this (file|skill|rule|doctrine) exists)"
)
FRONTMATTER_WHY = re.compile(r"(?m)^why\s*:\s*\S")
HEAD_LINES = 45  # only the head counts - a why buried at line 200 is not first


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter, body). Frontmatter is a leading --- ... --- block."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            nl = text.find("\n", end + 1)
            return text[3:end], text[nl + 1:] if nl != -1 else ""
    return "", text


def _declares_why(text: str) -> bool:
    fm, body = _split_frontmatter(text)
    if FRONTMATTER_WHY.search(fm):
        return True
    head = "\n".join(body.splitlines()[:HEAD_LINES])
    return bool(WHY_MARKER.search(head))


def check_why(root: Path, scope: str = "core") -> list[dict]:
    findings: list[dict] = []
    seen: set[Path] = set()
    globs = WHY_MD_GLOBS_ALL if scope == "all" else WHY_MD_GLOBS_CORE
    for glob in globs:
        for p in sorted(root.glob(glob)):
            if p in seen or not p.is_file():
                continue
            seen.add(p)
            rel = p.relative_to(root).as_posix()
            if p.name in WHY_EXEMPT_NAMES:
                continue
            if _declares_why(_read(p)):
                continue
            findings.append({
                "kind": "missing-why", "who": rel,
                "evidence": "no `why:` frontmatter and no why-marker in the first "
                            f"{HEAD_LINES} lines",
                "fix_home": "add a one-line `why:` (rules/entry-conventions.md convention)",
            })
    return findings


# ----- self-documenting code (scripts) -----

# A script owes a full contract at or above this many code lines. Below it, a
# one-line docstring is correct - thin wrappers are not traps.
SUBSTANTIVE_CODE_LINES = 40
MIN_DOCSTRING_CHARS = 200
# The markers that separate a contract from a label.
USAGE_MARKER = re.compile(
    r"(?im)(^\s*usage\s*:|^\s*cli\b|python scripts/|>>> |one-writer|single writer"
    r"|single-writer|read-only|invariant|stdlib only|standard library only)"
)
CODE_EXCLUDE_DIRS = {"archive", "__pycache__"}


def _code_line_count(tree: ast.Module, source: str) -> int:
    """Non-blank, non-comment lines that are not the module docstring."""
    doc = ast.get_docstring(tree, clean=False)
    doc_lines = set()
    if doc and tree.body and isinstance(tree.body[0], ast.Expr):
        node = tree.body[0]
        doc_lines = set(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    count = 0
    for i, line in enumerate(source.splitlines(), start=1):
        if i in doc_lines:
            continue
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        count += 1
    return count


def check_code(root: Path) -> list[dict]:
    findings: list[dict] = []
    scripts_dir = root / "scripts"
    if not scripts_dir.is_dir():
        return findings
    for p in sorted(scripts_dir.rglob("*.py")):
        parts = p.relative_to(scripts_dir).parts
        if any(part in CODE_EXCLUDE_DIRS for part in parts):
            continue
        # Tests are graded by the suite that runs them, not by an invocation contract.
        if p.name.startswith("test_") or "tests" in parts:
            continue
        source = _read(p)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue  # a script that will not parse is the verify skill's job, not this
        rel = p.relative_to(root).as_posix()
        code_lines = _code_line_count(tree, source)
        if code_lines < SUBSTANTIVE_CODE_LINES:
            continue  # thin wrapper - exempt by design
        doc = ast.get_docstring(tree) or ""
        reasons = []
        if not doc.strip():
            reasons.append("no module docstring")
        elif len(doc) < MIN_DOCSTRING_CHARS:
            reasons.append(f"docstring {len(doc)} chars (bar {MIN_DOCSTRING_CHARS})")
        if doc.strip() and not USAGE_MARKER.search(doc):
            reasons.append("no usage or invariant marker")
        if not reasons:
            continue
        findings.append({
            "kind": "thin-contract", "who": rel,
            "evidence": f"{code_lines} code lines, " + "; ".join(reasons),
            "fix_home": "raise the module docstring to the bar: the problem it solves, "
                        "the invariants it holds, and a usage block",
        })
    return findings


# ----- entry -----

def _print_human(label: str, findings: list[dict], cap: int) -> None:
    if not findings:
        print(f"selfdoc {label}: 0 gaps. Every checked surface documents itself.")
        return
    print(f"selfdoc {label}: {len(findings)} surface(s) missing a self-documenting contract "
          f"(showing {min(cap, len(findings))}).\n")
    for f in findings[:cap]:
        print(f"[{f['kind']}] {f['who']}")
        print(f"    {f['evidence']}")
        print(f"    -> fix home: {f['fix_home']}\n")
    if len(findings) > cap:
        print(f"... and {len(findings) - cap} more (run with --json for the full list).")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Self-documentation checker: doctrine markdown without a why, and "
                    "substantial scripts without a self-documenting contract. Read-only.")
    p.add_argument("mode", choices=["why", "code", "both"], help="which surface to check")
    p.add_argument("--json", action="store_true", help="machine form (for lint and verify)")
    p.add_argument("--cap", type=int, default=15, help="max findings shown in human mode (default 15)")
    p.add_argument("--scope", choices=["core", "all"], default="core",
                   help="why scope: 'core' = rules/ + system/ (default); 'all' adds skills/*/SKILL.md")
    p.add_argument("--root", default=None, help="OS root override (for tests)")
    args = p.parse_args(argv)

    root = Path(args.root).resolve() if args.root else REPO_ROOT
    why = check_why(root, args.scope) if args.mode in ("why", "both") else []
    code = check_code(root) if args.mode in ("code", "both") else []

    if args.json:
        out = {"root": str(root)}
        if args.mode in ("why", "both"):
            out["why"] = {"count": len(why), "findings": why}
        if args.mode in ("code", "both"):
            out["code"] = {"count": len(code), "findings": code}
        print(json.dumps(out, ensure_ascii=False))
        return 0

    if args.mode in ("why", "both"):
        _print_human("why", why, args.cap)
    if args.mode == "both":
        print()
    if args.mode in ("code", "both"):
        _print_human("code", code, args.cap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
