# -*- coding: utf-8 -*-
"""
tune.py - read the local voice telemetry and propose the next fast handler. Propose-only.

The voice skills (add-voice) log every turn locally to the gitignored voice/ folder:
  - runtime-log.jsonl      (Tier 0)  {ts, route, latency_ms, ok, chars_in, chars_out, ...}
  - live-telemetry.jsonl   (realtime) {ts, tools, heard, said, reply_ms, tokens_total, ...}

This reads whatever is present, aggregates the user's real usage, and prints a short report
plus a propose-only list: the one or two requests they make often that are NOT yet instant
handlers, so a future session can wire one and stop them being slow.

It changes nothing. It reads and proposes. Python standard library only, no network call.

Usage:
    python skills/tune/tune.py
    python skills/tune/tune.py --days 14
    python skills/tune/tune.py --top 5
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent


def find_repo_root(start):
    cur = start
    for _ in range(8):
        if (cur / "skills").is_dir() and (cur / "CLAUDE.md").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return SKILL_DIR.parent.parent


# Requests already answered instantly (handlers / tools the voice loop ships). A recurring
# intent that maps to one of these needs no new handler; one that does not is a candidate.
COVERED = {
    "today", "agenda", "schedule",          # show_today
    "week", "weekly", "this week",          # show_this_week
    "save", "note", "log",                  # save_to_brain
    "change", "changes",                    # what-to-change
    "brain", "query", "find", "recall",     # query_brain
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "for", "with", "my", "me",
    "i", "you", "is", "are", "was", "what", "whats", "can", "could", "would", "do", "does",
    "did", "please", "show", "tell", "give", "get", "let", "have", "has", "it", "this", "that",
    "about", "how", "now", "today", "ok", "okay", "hey", "hi", "hello", "thanks", "thank",
    "your", "os", "going", "want", "need", "like", "just", "some", "any", "all", "up", "out",
}


def parse_ts(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def read_jsonl(path):
    rows = []
    if not path.exists():
        return rows
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        pass
    return rows


def within(rows, days):
    if not days:
        return rows
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out = []
    for r in rows:
        ts = parse_ts(r.get("ts"))
        if ts is None or ts.tzinfo is None:
            out.append(r)  # keep undated rows rather than silently dropping usage
        elif ts >= cutoff:
            out.append(r)
    return out


def keywords(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z'-]+", (text or "").lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def main():
    ap = argparse.ArgumentParser(description="Propose the next fast voice handler from telemetry.")
    ap.add_argument("--days", type=int, default=0, help="only look at the last N days")
    ap.add_argument("--top", type=int, default=3, help="how many candidates to propose")
    args = ap.parse_args()

    root = find_repo_root(SKILL_DIR)
    voice = root / "voice"
    tier0 = within(read_jsonl(voice / "runtime-log.jsonl"), args.days)
    tier1 = within(read_jsonl(voice / "live-telemetry.jsonl"), args.days)
    total = len(tier0) + len(tier1)

    print("Tune - reading your local voice telemetry (propose-only, nothing is changed)")
    print("-" * 58)

    if total == 0:
        print("No voice telemetry found in " + str(voice) + ".")
        print("Run the voice loop first (the add-voice skill); there is nothing to tune yet.")
        return 0

    span = "" if not args.days else " in the last " + str(args.days) + " days"
    print("Read " + str(total) + " turns" + span + " (" + str(len(tier0)) + " Tier 0, " + str(len(tier1)) + " realtime).")
    if args.days:
        print("(Turns with no timestamp are always included, so the window is a floor, not exact.)")

    # Latency: which turns were slow.
    lat = [r.get("latency_ms") for r in tier0 if isinstance(r.get("latency_ms"), (int, float))]
    lat += [r.get("reply_ms") for r in tier1 if isinstance(r.get("reply_ms"), (int, float))]
    if lat:
        avg = round(sum(lat) / len(lat))
        slow = round(max(lat))
        print("Reply latency: avg " + str(avg) + "ms, slowest " + str(slow) + "ms.")

    # Tier 0 route frequency.
    routes = Counter(r.get("route") for r in tier0 if r.get("route"))
    if routes:
        top_routes = ", ".join(name + " x" + str(n) for name, n in routes.most_common(5))
        print("Routes used: " + top_routes + ".")

    # Tier 1 tools already used (these are already instant).
    tools = Counter()
    for r in tier1:
        for t in (r.get("tools") or []):
            tools[t] += 1
    if tools:
        print("Instant tools already firing: " + ", ".join(name + " x" + str(n) for name, n in tools.most_common(5)) + ".")

    # Intent keywords from what was actually said (realtime only - Tier 0 stores no text).
    heard = " ".join(str(r.get("heard") or "") for r in tier1)
    kw = Counter(keywords(heard))
    # Drop terms already covered by an instant handler.
    candidates = [(w, n) for w, n in kw.most_common(30) if w not in COVERED and n >= 2]

    print("")
    print("Proposal (propose-only - wire nothing without the owner's yes):")
    if not tier1:
        print("  - The realtime tier stores what you say; Tier 0 does not (it logs routes only).")
        print("    Run the realtime voice tier for a few sessions and tune again for intent-level")
        print("    suggestions. For now: if a route above is both frequent and slow, that route is")
        print("    the one to pre-program as an instant handler.")
        return 0
    if not candidates:
        print("  - Nothing recurs often enough yet to justify a new handler. The instant tools")
        print("    above are covering what you ask. Tune again after more use.")
        return 0
    print("  Requests you make often that are NOT yet instant handlers:")
    for w, n in candidates[: args.top]:
        print("  - \"" + w + "\" came up " + str(n) + " times. Consider a fast handler for it so it")
        print("    answers instantly instead of going through the reasoning brain.")
    print("")
    print("These are suggestions. Wiring a handler is a separate, deliberate change you confirm.")
    print("tune does not edit anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
