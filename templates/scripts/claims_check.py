#!/usr/bin/env python3
"""claims_check.py - the research-integrity second pass (rules/research-integrity.md).

The problem it exists for: AI-drafted research documents invent precise-looking
claims, and a precise-looking claim is the one that survives review, because it
reads as though somebody already checked it. A verification pass over a real
seven-document research pack found about 40 suspect claims in four repeating
classes: unsourced precise statistics, verbatim quotes with no retrievable
source, universal negatives ("no tool does X"), and arithmetic that does not
reconcile - one cost row off by 11% in a table whose other nine rows were right.

This detector scans a finished document for those classes. A claim line is
COVERED when it carries a tier tag ([MEASURED], [SOURCED], [ESTIMATE]) or a
source URL; everything else with a numeral, percentage, currency amount,
superlative, universal negative, or long verbatim quote is reported. Inline
arithmetic (a x b = c, a + b = c, n% of a = b) is re-run and mismatches are
flagged whether tagged or not.

Warn-first, never blocks: exit code is always 0 on a successful scan. It never
edits your document. The reviewer must not be the writer - run this as a second
pass over the finished document, not while drafting. stdlib only. No network,
no API key, no pip install.

Usage:
  python scripts/claims_check.py <file.md> [more files...]
  python scripts/claims_check.py <file.md> --json      # machine form
  python scripts/claims_check.py <file.md> --min-quote-words 8
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TIER_TAG = re.compile(r"\[(MEASURED|SOURCED|ESTIMATE)\b", re.IGNORECASE)
URL = re.compile(r"https?://\S+")

# --- claim candidates ---------------------------------------------------------

PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s?%")
CURRENCY = re.compile(
    r"(?:[$€£₹]\s?\d[\d,]*(?:\.\d+)?"
    r"|\b(?:AED|USD|EUR|GBP|INR|SAR)\s?\d[\d,]*(?:\.\d+)?)"
    r"(?:\s?(?:k|K|m|M|bn|million|billion|lakh|crore))?"
)
# Comma-grouped, decimal, 4+ digit, or multiplier numbers. Bare years and other
# non-claims are filtered by NOT_A_CLAIM below.
NUMBER = re.compile(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+\.\d+\b|\b\d{4,}\b|\b\d+(?:\.\d+)?x\b")

NOT_A_CLAIM = [
    re.compile(r"^\d{4}-\d{2}-\d{2}$"),          # ISO date
    re.compile(r"^(?:19|20)\d{2}$"),             # bare year
    re.compile(r"^\d{1,2}:\d{2}$"),              # time
    re.compile(r"^v?\d+\.\d+(?:\.\d+)?$"),       # version string
]
DATEISH_CONTEXT = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}|v\d+\.\d+")

UNIVERSAL_NEGATIVE = re.compile(
    r"\b(?:no (?:one|body|tool|platform|product|competitor|vendor|company|app)s?\b"
    r"|nobody\b|nothing (?:on the market|else|comparable)"
    r"|none of the (?:tools|platforms|competitors|products)"
    r"|the only (?:tool|platform|product|player|company|one)"
    r"|zero competitors)",
    re.IGNORECASE,
)
BOUNDED_SEARCH = re.compile(r"\b(?:checked|searched|reviewed|compared|tested)\b", re.IGNORECASE)

SUPERLATIVE = re.compile(
    r"\b(?:largest|biggest|fastest[- ]growing|best[- ]in[- ]class|market[- ]leading"
    r"|world'?s (?:first|best|largest)|industry[- ]leading|#1|number one)\b",
    re.IGNORECASE,
)

QUOTE = re.compile(r'["“]([^"”]{10,400})["”]')

ARITH = re.compile(
    r"(\d[\d,]*(?:\.\d+)?)\s*([x×*+/-])\s*"
    r"[$€£]?\s?(\d[\d,]*(?:\.\d+)?)\s*=\s*"
    r"[$€£]?\s?(\d[\d,]*(?:\.\d+)?)"
)
PERCENT_OF = re.compile(
    r"(\d+(?:\.\d+)?)\s?%\s+of\s+[$€£]?\s?(\d[\d,]*(?:\.\d+)?)"
    r"\s*(?:=|is|comes to)\s*[$€£]?\s?(\d[\d,]*(?:\.\d+)?)"
)


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def _is_claim_number(token: str) -> bool:
    return not any(p.match(token) for p in NOT_A_CLAIM)


def _iter_content_lines(text: str):
    """Yield (lineno, line), skipping fenced code blocks and YAML front matter."""
    lines = text.splitlines()
    in_fence = False
    in_front = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if i == 1 and stripped == "---":
            in_front = True
            continue
        if in_front:
            if stripped == "---":
                in_front = False
            continue
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield i, line


def scan_file(path: Path, min_quote_words: int) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")

    for lineno, line in _iter_content_lines(text):
        covered = bool(TIER_TAG.search(line) or URL.search(line))
        snippet = line.strip()[:120]

        # Arithmetic reconciliation runs regardless of coverage.
        for m in ARITH.finditer(line):
            a, op, b, stated = _num(m.group(1)), m.group(2), _num(m.group(3)), _num(m.group(4))
            if op in ("x", "×", "*"):
                actual = a * b
            elif op == "+":
                actual = a + b
            elif op == "-":
                actual = a - b
            else:
                if b == 0:
                    continue
                actual = a / b
            if actual and abs(actual - stated) > max(1.0, abs(actual) * 0.015):
                findings.append({
                    "line": lineno, "class": "arithmetic-mismatch",
                    "detail": f"{m.group(0)} -> re-computed {actual:,.2f}", "snippet": snippet,
                })
        for m in PERCENT_OF.finditer(line):
            pct, base, stated = _num(m.group(1)), _num(m.group(2)), _num(m.group(3))
            actual = pct / 100.0 * base
            if actual and abs(actual - stated) > max(1.0, abs(actual) * 0.015):
                findings.append({
                    "line": lineno, "class": "arithmetic-mismatch",
                    "detail": f"{m.group(0)} -> re-computed {actual:,.2f}", "snippet": snippet,
                })

        # Universal negatives need a bounded search even when tagged.
        if UNIVERSAL_NEGATIVE.search(line) and not BOUNDED_SEARCH.search(line):
            findings.append({
                "line": lineno, "class": "universal-negative",
                "detail": UNIVERSAL_NEGATIVE.search(line).group(0),
                "snippet": snippet,
            })

        if covered:
            continue

        # Long verbatim quotes without a retrievable source.
        for m in QUOTE.finditer(line):
            if len(m.group(1).split()) >= min_quote_words:
                findings.append({
                    "line": lineno, "class": "unsourced-quote",
                    "detail": m.group(1)[:80], "snippet": snippet,
                })

        # Numbers, percentages, currency, superlatives without a tier tag.
        tokens = []
        tokens += [m.group(0) for m in PERCENT.finditer(line)]
        tokens += [m.group(0) for m in CURRENCY.finditer(line)]
        if not DATEISH_CONTEXT.search(line):
            tokens += [t for t in (m.group(0) for m in NUMBER.finditer(line)) if _is_claim_number(t)]
        seen = set()
        tokens = [t for t in tokens if not (t in seen or seen.add(t))]
        if tokens:
            findings.append({
                "line": lineno, "class": "untagged-number",
                "detail": ", ".join(tokens[:6]), "snippet": snippet,
            })
        if SUPERLATIVE.search(line):
            findings.append({
                "line": lineno, "class": "untagged-superlative",
                "detail": SUPERLATIVE.search(line).group(0), "snippet": snippet,
            })

    return findings


CLASS_ORDER = [
    "arithmetic-mismatch", "unsourced-quote", "universal-negative",
    "untagged-number", "untagged-superlative",
]
CLASS_HINT = {
    "arithmetic-mismatch": "both operands are on the line and the stated result does not reconcile",
    "unsourced-quote": "verbatim quote with no retrievable URL on the line - source it or delete it",
    "universal-negative": "rewrite as a bounded search: 'checked A, B, C on <date>, found none'",
    "untagged-number": "needs [MEASURED: artifact+command], [SOURCED: url+date], or [ESTIMATE: assumption]",
    "untagged-superlative": "superlative with no source - tag it or soften it",
}


def main() -> int:
    # Windows consoles default to cp1252; source documents carry arrows and
    # smart quotes. Never let an encoding error kill a warn-first check.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    ap = argparse.ArgumentParser(description="Research-claims coverage check (warn-first, never blocks).")
    ap.add_argument("files", nargs="+", help="markdown/text documents to scan")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--min-quote-words", type=int, default=6,
                    help="minimum words for a quote to count as verbatim (default 6)")
    args = ap.parse_args()

    report = {}
    missing = []
    for f in args.files:
        p = Path(f)
        if not p.is_file():
            missing.append(f)
            continue
        report[f] = scan_file(p, args.min_quote_words)

    if args.json:
        print(json.dumps({"files": report, "missing": missing}, indent=2))
        return 0 if not missing else 2

    total = 0
    for f, findings in report.items():
        print(f"\n== {f} ==")
        if not findings:
            print("  covered: no uncovered claims found")
            continue
        for cls in CLASS_ORDER:
            group = [x for x in findings if x["class"] == cls]
            if not group:
                continue
            print(f"\n  {cls} ({len(group)}) - {CLASS_HINT[cls]}")
            for x in group:
                print(f"    L{x['line']:>4}  {x['detail']}")
                print(f"           | {x['snippet']}")
        total += len(findings)
    for f in missing:
        print(f"\n== {f} ==\n  ERROR: file not found", file=sys.stderr)

    print(f"\n{total} uncovered claim(s) across {len(report)} file(s). "
          "Warn-first: this check never blocks. Fix or tag before the claim reaches a deck.")
    return 0 if not missing else 2


if __name__ == "__main__":
    sys.exit(main())
