#!/usr/bin/env python3
"""Deterministic candidate gatherer for the what-to-change flagship routine.

The flagship answers "what should I change in my business now" with exactly
three ranked changes. The documented failure mode (carried over from the
private morning-brief work) is FALSE URGENCY: a parked or done item resurfacing
as fresh urgency. A behavioral instruction alone does not stop that, so this
script is the mechanical guard:

  - It returns ONLY dated signals from the last N days (the candidate gate). An
    item with no dated evidence in the window cannot become one of the three.
  - It EXCLUDES parked / paused / resolved flags and anything named in
    brain/decisions-parked.md. A parked item is never a candidate.
  - Every signal carries a resolvable [source: file#anchor] the reader can
    open. The anchor is built from a real heading or date in the file, so the
    resolve subcommand can confirm it.

The skill reasons over these signals to pick at most three. If the gatherer
returns fewer than three, the skill says so rather than padding - it has no
other candidate source.

Standard library only. Reads, never writes. Never invents a date or a source.

Subcommands:
    gather [--within N] [--repo PATH]   Print candidate signals as JSON.
    resolve FILE#ANCHOR [--repo PATH]   Exit 0 if the anchor resolves, 1 if not.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

DEFAULT_WITHIN_DAYS = 30
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.*\S)\s*$")
STATUS_RE = re.compile(r"(?i)\bStatus:\s*\**\s*([A-Za-z]+)")
DECAY_RE = re.compile(r"(?i)\bDecay after:\s*(\d+)\s*d\b")
BODY_DATE_RE = re.compile(r"(?i)\b(?:First observed|Date parked|Date)\s*:\s*(\d{4}-\d{2}-\d{2})")

# Flag states that represent a live thing to change. Everything else (PARKED,
# PAUSED, RESOLVED, DONE) is excluded.
LIVE_FLAG_STATES = {"OPEN", "ESCALATED"}


def slugify(text: str) -> str:
    """GitHub-style heading anchor: lowercase, drop punctuation, spaces to
    hyphens. Deterministic so resolve() can rebuild and match it."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _iter_entries(text: str) -> list[tuple[str, list[str]]]:
    """Split a markdown file into (heading, body-lines) entries on ##-#### heads."""
    entries: list[tuple[str, list[str]]] = []
    heading: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            if heading is not None:
                entries.append((heading, body))
            heading = m.group(2).strip()
            body = []
        elif heading is not None:
            body.append(line)
    if heading is not None:
        entries.append((heading, body))
    return entries


def _parked_titles(repo: Path) -> set[str]:
    """Normalized titles of every entry in decisions-parked.md. These are parked
    by definition and must never surface as urgent."""
    text = _read(repo / "brain" / "decisions-parked.md")
    if not text:
        return set()
    titles: set[str] = set()
    for heading, _body in _iter_entries(text):
        norm = slugify(heading)
        if norm and norm not in {"format", "example", "decisions-parked"}:
            titles.add(norm)
    return titles


def _entry_date(heading: str, body: list[str]) -> date | None:
    m = DATE_RE.search(heading)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    for line in body:
        m = BODY_DATE_RE.search(line)
        if m:
            try:
                return date.fromisoformat(m.group(1))
            except ValueError:
                continue
    return None


def gather_flags(repo: Path, today: date, within: int, parked: set[str]) -> list[dict]:
    text = _read(repo / "brain" / "flags.md")
    if not text:
        return []
    out: list[dict] = []
    for heading, body in _iter_entries(text):
        if slugify(heading) in {"lifecycle", "severity-ladder", "decay-convention", "two-flag-types", "flags"}:
            continue
        status_m = None
        for line in body:
            status_m = STATUS_RE.search(line)
            if status_m:
                break
        if not status_m:
            continue
        state = status_m.group(1).upper()
        if state not in LIVE_FLAG_STATES:
            continue  # PARKED / PAUSED / RESOLVED excluded
        if slugify(heading) in parked:
            continue  # cross-referenced as parked in decisions-parked.md
        d = _entry_date(heading, body)
        if d is None:
            continue  # no dated evidence: fails the candidate gate
        age = (today - d).days
        decay_passed = False
        for line in body:
            dm = DECAY_RE.search(line)
            if dm:
                from datetime import timedelta

                decay_passed = today > (d + timedelta(days=int(dm.group(1))))
                break
        if age > within and not decay_passed:
            continue
        out.append(
            {
                "source": "brain/flags.md",
                "anchor": slugify(heading),
                "title": heading,
                "date": d.isoformat(),
                "age_days": age,
                "kind": "flag",
                "state": state,
                "decay_passed": decay_passed,
            }
        )
    return out


def gather_log(repo: Path, today: date, within: int) -> list[dict]:
    text = _read(repo / "brain" / "log.md")
    if not text:
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for heading, body in _iter_entries(text):
        m = DATE_RE.search(heading)
        if not m:
            continue
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        age = (today - d).days
        if age > within or age < 0:
            continue
        first = next((b.strip(" -") for b in body if b.strip()), heading)
        key = m.group(1)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "source": "brain/log.md",
                "anchor": m.group(1),
                "title": first[:120],
                "date": d.isoformat(),
                "age_days": age,
                "kind": "activity",
            }
        )
    return out


def gather(repo: Path, today: date, within: int) -> dict:
    parked = _parked_titles(repo)
    signals = gather_flags(repo, today, within, parked) + gather_log(repo, today, within)
    signals.sort(key=lambda s: s["date"], reverse=True)
    return {
        "as_of": today.isoformat(),
        "within_days": within,
        "parked_excluded": sorted(parked),
        "count": len(signals),
        "signals": signals,
    }


def resolve(repo: Path, ref: str) -> bool:
    if "#" not in ref:
        return False
    rel, _, anchor = ref.partition("#")
    text = _read(repo / rel)
    if text is None:
        return False
    # A flag/log heading whose slug or date equals the anchor, OR a raw date
    # token present in the file (state files have no headings).
    for heading, _body in _iter_entries(text):
        if slugify(heading) == anchor:
            return True
        m = DATE_RE.search(heading)
        if m and m.group(1) == anchor:
            return True
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", anchor) and anchor in text:
        return True
    return False


def main() -> int:
    args = sys.argv[1:]
    repo = REPO_DEFAULT
    within = DEFAULT_WITHIN_DAYS
    today = date.today()

    rest: list[str] = []
    i = 0
    while i < len(args):
        if args[i] == "--repo" and i + 1 < len(args):
            repo = Path(args[i + 1]).resolve()
            i += 2
        elif args[i] == "--within" and i + 1 < len(args):
            try:
                within = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif args[i] == "--today" and i + 1 < len(args):
            try:
                today = date.fromisoformat(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            rest.append(args[i])
            i += 1

    if not rest:
        print(__doc__)
        return 0
    cmd = rest[0]
    if cmd == "gather":
        print(json.dumps(gather(repo, today, within), indent=2))
        return 0
    if cmd == "resolve" and len(rest) >= 2:
        ok = resolve(repo, rest[1])
        print("resolves" if ok else "does not resolve")
        return 0 if ok else 1
    print(f"Unknown subcommand: {cmd}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    return 1


REPO_DEFAULT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    raise SystemExit(main())
