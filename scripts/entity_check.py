#!/usr/bin/env python3
"""entity_check.py - the entity-folder detector (rules/entity-folders.md).

Three jobs, all read-only:

1. PROMOTION CANDIDATES. A single-file entity that crossed a threshold (size,
   history-longer-than-read, or touch frequency) is proposed for promotion to a
   folder with the fixed anatomy profile.md / log.md / sources/. Proposal only -
   the operator approves. This script never creates a folder.
2. OVERDUE REVIEWS. An entity whose `reviewed:` date is 60+ days old AND has real
   dated touches since. An identity nobody confirmed is a stale assertion with a
   confident tone. An untouched dormant entity is NOT surfaced - going quiet is
   not debt.
3. ANATOMY DRIFT. A promoted folder missing profile.md or log.md, or a profile
   with no `reviewed:` field at all.

stdlib only. No network. Never writes.

Usage:
  python scripts/entity_check.py                    # human report
  python scripts/entity_check.py --json             # machine form (/housekeeping, retro)
  python scripts/entity_check.py --root PATH        # fixture root for tests
  python scripts/entity_check.py --review-days 90   # override the 60-day review window
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENTITY_DIR = "context/entities"

REVIEW_DAYS = 60
SIZE_LINES = 400
TOUCH_ENTRIES = 6

FRONT_FIELD = re.compile(r"(?im)^\s*(entity|type|status|reviewed)\s*:\s*(.+?)\s*$")
DATE_LINE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
HISTORY_HEAD = re.compile(r"(?im)^#{1,3}\s*(history|log|timeline|evidence)\b")


def _parse_front(text: str) -> dict:
    """Read YAML-ish front matter without a yaml dependency."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    return {m.group(1).lower(): m.group(2).strip() for m in FRONT_FIELD.finditer(block)}


def _to_date(value: str):
    m = DATE_LINE.search(value or "")
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _dated_touches(text: str) -> list[date]:
    out = []
    for m in DATE_LINE.finditer(text):
        try:
            out.append(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
        except ValueError:
            continue
    return out


def _history_ratio(text: str) -> float:
    """Fraction of the body that sits under a history/log heading."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if HISTORY_HEAD.match(ln):
            start = i
            break
    if start is None:
        return 0.0
    return (len(lines) - start) / max(1, len(lines))


def _promotion_reasons(text: str, today: date) -> list[str]:
    reasons = []
    n_lines = len(text.splitlines())
    if n_lines >= SIZE_LINES:
        reasons.append(f"size: {n_lines} lines (threshold {SIZE_LINES})")
    if _history_ratio(text) > 0.5:
        reasons.append("history section is longer than the current read")
    touches = sorted(set(_dated_touches(text)))
    if len(touches) >= TOUCH_ENTRIES:
        recent = [d for d in touches if (today - d).days <= 28]
        weeks = {((today - d).days // 7) for d in recent}
        detail = f"{len(touches)} dated entries"
        if len(weeks) >= 3:
            detail += f", touched in {len(weeks)} of the last 4 weeks"
        reasons.append(f"touch frequency: {detail}")
    return reasons


def scan(root: Path, today: date, review_days: int) -> dict:
    base = root / ENTITY_DIR
    result = {"promotion_candidates": [], "overdue_reviews": [], "anatomy_drift": [], "scanned": 0}
    if not base.is_dir():
        result["note"] = f"{ENTITY_DIR} does not exist yet - nothing to scan"
        return result

    # Stage 1: single-file entities.
    for f in sorted(base.glob("*.md")):
        if f.name.upper().startswith("README"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        front = _parse_front(text)
        rel = f"{ENTITY_DIR}/{f.name}"
        result["scanned"] += 1
        if front.get("status", "active").lower() == "archived":
            continue
        reasons = _promotion_reasons(text, today)
        if reasons:
            result["promotion_candidates"].append({"entity": rel, "reasons": reasons})
        _check_review(result, rel, front, text, today, review_days)

    # Stage 2: promoted folders.
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        rel = f"{ENTITY_DIR}/{d.name}"
        result["scanned"] += 1
        profile = d / "profile.md"
        log = d / "log.md"
        missing = [n for n, p in (("profile.md", profile), ("log.md", log)) if not p.is_file()]
        if missing:
            result["anatomy_drift"].append({"entity": rel, "detail": "missing " + ", ".join(missing)})
            continue
        text = profile.read_text(encoding="utf-8", errors="replace")
        front = _parse_front(text)
        if front.get("status", "active").lower() == "archived":
            continue
        log_text = log.read_text(encoding="utf-8", errors="replace")
        _check_review(result, rel, front, text + "\n" + log_text, today, review_days)

    return result


def _check_review(result: dict, rel: str, front: dict, body: str, today: date, review_days: int):
    reviewed = _to_date(front.get("reviewed", ""))
    if reviewed is None:
        result["anatomy_drift"].append({"entity": rel, "detail": "no `reviewed:` field in front matter"})
        return
    age = (today - reviewed).days
    if age < review_days:
        return
    # Only surface when real evidence landed AFTER the last review. A dormant
    # entity going quiet is not debt.
    touches_since = [d for d in _dated_touches(body) if d > reviewed and d <= today]
    if not touches_since:
        return
    result["overdue_reviews"].append({
        "entity": rel,
        "reviewed": reviewed.isoformat(),
        "days": age,
        "touches_since": len(touches_since),
        "latest_touch": max(touches_since).isoformat(),
    })


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    ap = argparse.ArgumentParser(description="Entity-folder detector (read-only, proposal only).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=str(REPO_ROOT))
    ap.add_argument("--review-days", type=int, default=REVIEW_DAYS)
    ap.add_argument("--today", default=None, help="YYYY-MM-DD, for tests")
    args = ap.parse_args()

    today = _to_date(args.today) if args.today else datetime.now().date()
    if today is None:
        print("bad --today value, expected YYYY-MM-DD", file=sys.stderr)
        return 2

    data = scan(Path(args.root), today, args.review_days)

    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    if data.get("note"):
        print(data["note"])
        return 0

    pc, orv, ad = data["promotion_candidates"], data["overdue_reviews"], data["anatomy_drift"]
    print(f"Entities scanned: {data['scanned']}")

    if pc:
        print(f"\nPromotion candidates ({len(pc)}) - propose the folder, the operator approves:")
        for x in pc:
            print(f"  {x['entity']}")
            for r in x["reasons"]:
                print(f"    - {r}")
        print("    anatomy: <slug>/profile.md (current read), log.md (append-only), sources/")
    if orv:
        print(f"\nOverdue identity reviews ({len(orv)}) - confirm, correct, or archive:")
        for x in orv:
            print(f"  {x['entity']}  reviewed {x['reviewed']} ({x['days']}d ago), "
                  f"{x['touches_since']} touches since, latest {x['latest_touch']}")
    if ad:
        print(f"\nAnatomy drift ({len(ad)}):")
        for x in ad:
            print(f"  {x['entity']}  {x['detail']}")

    if not (pc or orv or ad):
        print("\nNothing due. No promotions to propose, no reviews overdue, no drift.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
