#!/usr/bin/env python3
"""Brain-pass telemetry appender for Founder OS.

Records one JSONL line per brain-pass invocation so the user can
spot shallow synthesis, repeated questions, or low-confidence answers
before they become a problem.

Opt-in via the FOUNDER_OS_OBSERVATIONS=1 environment variable, matching
the v1.7 PostToolUse observation log convention. When the variable is
not set, this script exits 0 silently and writes nothing.

Output path: brain/observations/<YYYY-MM-DD>.jsonl
Pure Python stdlib. Fail-soft: write failures exit 0 so brain-pass
never blocks on telemetry.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

CONFIDENCE_VALUES = {"high", "medium", "low"}


def is_enabled() -> bool:
    return os.environ.get("FOUNDER_OS_OBSERVATIONS", "").strip() == "1"


def parse_ids(raw: str) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "y"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a brain-pass telemetry line.")
    parser.add_argument("--question", required=True, help="The brain-pass question (will be truncated to 280 chars).")
    parser.add_argument("--confidence", required=True, help="high | medium | low")
    parser.add_argument("--ids-cited", default="", help="Comma-separated stable IDs cited in Evidence.")
    parser.add_argument("--files-read", type=int, default=0, help="Count of files the pass read.")
    parser.add_argument("--has-gaps", default="no", help="yes | no - did the Gaps section flag missing context?")
    parser.add_argument("--root", default=".", help="Founder OS root.")
    parser.add_argument("--now", default=None, help="Override timestamp (ISO 8601). Test-only.")
    args = parser.parse_args()

    if not is_enabled():
        return 0

    confidence = args.confidence.strip().lower()
    if confidence not in CONFIDENCE_VALUES:
        print(f"--confidence must be one of {sorted(CONFIDENCE_VALUES)}, got: {args.confidence}", file=sys.stderr)
        return 2

    if args.now:
        try:
            ts = datetime.fromisoformat(args.now).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            print(f"--now must be ISO 8601, got: {args.now}", file=sys.stderr)
            return 2
    else:
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    payload = {
        "timestamp": ts,
        "type": "brain_pass",
        "question": args.question.strip()[:280],
        "files_read": max(0, args.files_read),
        "ids_cited": parse_ids(args.ids_cited),
        "confidence": confidence,
        "has_gaps": parse_bool(args.has_gaps),
    }

    root = Path(args.root).resolve()
    target_dir = root / "brain" / "observations"
    target = target_dir / f"{ts[:10]}.jsonl"
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
