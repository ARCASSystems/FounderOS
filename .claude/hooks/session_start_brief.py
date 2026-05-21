#!/usr/bin/env python3
"""Consolidated session-start brief helpers.

Previously the bash hook (session-start-brief.sh) shelled out to Python up to 8
times per session (date math, compliance scan, decay scan x3, tip rotation,
observations stale count). Each subprocess spawn costs ~250ms on Windows,
adding up to ~2s of session-start latency.

This script collapses all of that into a single Python process. The bash hook
invokes it once with the repo root, today's ISO date, and the observations
flag; the script emits a structured payload of named sections that bash parses
with simple awk/grep.

Output format: each section starts with a marker line
    @@SECTION:<name>
followed by zero or more content lines, terminated by:
    @@END
Sections are emitted only when there is something to report (matches the
original "quiet exit" behavior of the heredocs).

Sections emitted (when applicable):
    daily       -> single line: STALE|<date>|<today> or CURRENT|<date>
    weekly      -> single line: STALE|<date>|<age> or CURRENT|<date>
    compliance  -> OVERDUE|N then up to 3 "  YYYY-MM-DD - desc (overdue Nd)"
                   UPCOMING|N then up to 3 "  YYYY-MM-DD - desc (in Nd)"
    decay       -> "DECAY|<heading>|<age>" or "NOANCHOR|<heading>|0"
    tip         -> single line with the tip text
    observations-> single line: integer count of stale JSONL files

Bash parses these and prints the same human-readable lines it used to.
Output is identical to the pre-consolidation hook.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path


def emit(section: str, lines: list[str]) -> None:
    if not lines:
        return
    sys.stdout.write(f"@@SECTION:{section}\n")
    for line in lines:
        sys.stdout.write(line)
        if not line.endswith("\n"):
            sys.stdout.write("\n")
    sys.stdout.write("@@END\n")


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def section_daily(repo: Path, today: date) -> list[str]:
    p = repo / "cadence" / "daily-anchors.md"
    text = read_text(p)
    if text is None:
        return []
    m = re.search(r"^## Today: (\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    if not m:
        return []
    try:
        d = date.fromisoformat(m.group(1))
    except ValueError:
        return []
    if (today - d).days > 0:
        return [f"STALE|{m.group(1)}|{today.isoformat()}"]
    return [f"CURRENT|{m.group(1)}"]


def section_weekly(repo: Path, today: date) -> list[str]:
    p = repo / "cadence" / "weekly-commitments.md"
    text = read_text(p)
    if text is None:
        return []
    m = re.search(r"^## Week of (\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    if not m:
        return []
    try:
        d = date.fromisoformat(m.group(1))
    except ValueError:
        return []
    age = (today - d).days
    if age > 6:
        return [f"STALE|{m.group(1)}|{age}"]
    return [f"CURRENT|{m.group(1)}"]


def section_compliance(repo: Path, today: date) -> list[str]:
    p = repo / "context" / "compliance.md"
    text = read_text(p)
    if text is None:
        return []
    lines = text.splitlines()
    heading_re = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*[-:]\s*(.+?)\s*$")
    status_re = re.compile(r"^\s*-\s*Status:\s*(\w+)", re.IGNORECASE)
    overdue: list[tuple[date, str, int]] = []
    upcoming: list[tuple[date, str, int]] = []
    i = 0
    while i < len(lines):
        m = heading_re.match(lines[i])
        if not m:
            i += 1
            continue
        try:
            deadline = date.fromisoformat(m.group(1))
        except ValueError:
            i += 1
            continue
        desc = m.group(2)
        status = "OPEN"
        j = i + 1
        while j < len(lines) and not lines[j].startswith("## "):
            sm = status_re.match(lines[j])
            if sm:
                status = sm.group(1).upper()
                break
            j += 1
        if status == "DONE":
            i = j
            continue
        delta = (deadline - today).days
        if delta < 0:
            overdue.append((deadline, desc, abs(delta)))
        elif delta <= 30:
            upcoming.append((deadline, desc, delta))
        i = j
    out: list[str] = []
    if overdue:
        out.append(f"OVERDUE|{len(overdue)}")
        for d, desc, days_past in sorted(overdue)[:3]:
            out.append(f"  {d} - {desc} (overdue {days_past}d)")
    if upcoming:
        out.append(f"UPCOMING|{len(upcoming)}")
        for d, desc, days_to in sorted(upcoming)[:3]:
            out.append(f"  {d} - {desc} (in {days_to}d)")
    return out


def _scan_decay_file(path: Path, heading_re_str: str, today: date) -> list[str]:
    text = read_text(path)
    if text is None:
        return []
    lines = text.splitlines()
    hpat = re.compile(heading_re_str)
    file_name = path.name

    def anchor_date(entry: list[str]) -> date | None:
        h = entry[0]
        if file_name == "flags.md":
            m = re.search(r"(\d{4}-\d{2}-\d{2})", h)
            if m:
                try:
                    return date.fromisoformat(m.group(1))
                except ValueError:
                    pass
        for l in entry:
            m = re.match(r"\s*-?\s*Date parked:\s*(\d{4}-\d{2}-\d{2})", l)
            if m:
                try:
                    return date.fromisoformat(m.group(1))
                except ValueError:
                    pass
            m = re.match(r"\s*-?\s*First observed:\s*(\d{4}-\d{2}-\d{2})", l)
            if m:
                try:
                    return date.fromisoformat(m.group(1))
                except ValueError:
                    pass
        return None

    out: list[str] = []

    def process(entry: list[str]) -> None:
        if not entry:
            return
        head = entry[0].strip()
        decay: date | None = None
        missing_anchor = False
        for l in entry:
            m = re.match(r"\s*-?\s*Decay after:\s*(.+?)\s*$", l)
            if not m:
                continue
            val = m.group(1).strip()
            if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
                try:
                    decay = date.fromisoformat(val)
                except ValueError:
                    decay = None
            else:
                m2 = re.match(r"^(\d+)d$", val)
                if m2:
                    a = anchor_date(entry)
                    if a:
                        decay = a + timedelta(days=int(m2.group(1)))
                    else:
                        missing_anchor = True
            break
        if decay and decay < today:
            age = (today - decay).days
            out.append(f"DECAY|{head}|{age}")
        elif missing_anchor:
            out.append(f"NOANCHOR|{head}|0")

    entry: list[str] = []
    for ln in lines:
        if hpat.match(ln):
            process(entry)
            entry = [ln]
        else:
            entry.append(ln)
    process(entry)
    return out


def section_decay(repo: Path, today: date) -> list[str]:
    hits: list[str] = []
    hits.extend(_scan_decay_file(repo / "brain" / "flags.md", r"^##\s", today))
    hits.extend(_scan_decay_file(repo / "brain" / "patterns.md", r"^###\s", today))
    hits.extend(_scan_decay_file(repo / "brain" / "decisions-parked.md", r"^###\s", today))
    return hits


TIPS: list[tuple[str, str]] = [
    ("decision-framework", 'Try saying "help me decide" next time you\'re stuck on a choice - the decision-framework skill walks you through it.'),
    ("priority-triage", 'Say "what should I focus on next" when the open list grows past five - priority-triage cuts it down to one thing.'),
    ("forcing-questions", 'Try "force me to think this through" before starting something new - forcing-questions runs six tests on the idea before you commit.'),
    ("weekly-review", 'Say "run my weekly review" on Friday or Monday - weekly-review rolls the sprint and forces a verdict on every open flag.'),
    ("audit", 'Say "audit the OS" when things feel drifty - one composite report on health, voice, and wiki state.'),
    ("brain-pass", 'Try "ask the brain about <topic>" - brain-pass synthesises across log, knowledge, and decisions instead of one keyword match.'),
    ("knowledge-capture", 'Say "capture this" after a book or podcast worth keeping - knowledge-capture files it with a stable ID.'),
    ("ingest", 'Say "ingest this" on a URL or transcript - ingest preserves the source with provenance and proposes wiki updates.'),
    ("bottleneck-diagnostic", 'Try "what\'s blocking me" once a quarter - bottleneck-diagnostic scores founder dependency across five dimensions.'),
    ("strategic-analysis", 'Say "analyze this market" or "competitor map" - strategic-analysis grounds the scan in your knowledge notes.'),
]


def section_tip(repo: Path, today: date) -> list[str]:
    log = repo / "brain" / "log.md"
    text = read_text(log)
    if text is None:
        return []
    entry_re = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})")
    entry_dates: list[date] = []
    for ln in text.splitlines():
        m = entry_re.match(ln)
        if m:
            try:
                entry_dates.append(date.fromisoformat(m.group(1)))
            except ValueError:
                continue
    if len(entry_dates) < 10:
        return []
    earliest = min(entry_dates)
    if (today - earliest).days < 30:
        return []
    date_re = re.compile(r"^#{2,3}\s+(\d{4}-\d{2}-\d{2})")
    last_used: dict[str, date] = {}
    cur: date | None = None
    for ln in text.splitlines():
        m = date_re.match(ln)
        if m:
            try:
                cur = date.fromisoformat(m.group(1))
            except ValueError:
                cur = None
            continue
        if cur is None:
            continue
        for cap, _ in TIPS:
            if f"#used-{cap}" in ln or ("#acted" in ln and cap in ln):
                prev = last_used.get(cap)
                if prev is None or cur > prev:
                    last_used[cap] = cur
    eligible: list[tuple[str, str]] = []
    for cap, tip in TIPS:
        last = last_used.get(cap)
        if last is None or (today - last).days >= 14:
            eligible.append((cap, tip))
    if not eligible:
        return []
    week = today.isocalendar()[1]
    idx = week % len(eligible)
    return [eligible[idx][1]]


def section_observations(repo: Path, today: date) -> list[str]:
    obs_dir = repo / "brain" / "observations"
    if not obs_dir.is_dir():
        return []
    cut = today - timedelta(days=10)
    try:
        n = sum(
            1
            for f in obs_dir.glob("*.jsonl")
            if _safe_iso(f.stem) and date.fromisoformat(f.stem) < cut
        )
    except Exception:
        return ["0"]
    return [str(n)]


def _safe_iso(s: str) -> bool:
    try:
        date.fromisoformat(s)
        return True
    except ValueError:
        return False


def main() -> int:
    if len(sys.argv) < 3:
        return 0
    repo = Path(sys.argv[1])
    try:
        today = date.fromisoformat(sys.argv[2])
    except ValueError:
        return 0
    want_observations = os.environ.get("FOUNDER_OS_OBSERVATIONS") == "1"

    emit("daily", section_daily(repo, today))
    emit("weekly", section_weekly(repo, today))
    emit("compliance", section_compliance(repo, today))
    emit("decay", section_decay(repo, today))
    emit("tip", section_tip(repo, today))
    if want_observations:
        emit("observations", section_observations(repo, today))
    return 0


if __name__ == "__main__":
    sys.exit(main())
