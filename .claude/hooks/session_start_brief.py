#!/usr/bin/env python3
"""Session-start brief renderer (the whole brief, in one Python process).

The SessionStart hook used to be a bash/PowerShell pair that did half the work
in shell (awk/grep over queue, flags, decisions, [FILL], connectors, rants,
quarantine) and shelled out to this file for the date-math half (staleness,
decay, tip, founder-move). With the v1.42 hook dispatcher, the shell pair is
retired and this file renders the ENTIRE brief so there is one implementation
instead of two that could drift.

Called by scripts/hooks/dispatch.py on SessionStart:
    python .claude/hooks/session_start_brief.py <repo-root> <today-iso>

It reads the operating files and prints the human-readable brief to stdout. A
fresh pre-setup install (no core/identity.md) prints the welcome banner and
nothing else. FOUNDER_OS_OBSERVATIONS=1 adds the observation lines.

Pure stdlib. ASCII-safe stdout (survives any Windows codepage). Never blocks
session start: every read is guarded and any failure degrades to a quiet skip.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def emit(section: str, lines: list[str]) -> None:
    """Legacy @@SECTION output. Kept so a founder who updates to the dispatcher
    release but has not yet accepted the settings.json migration - and whose
    retained session-start-brief.sh still calls this file with no --full flag -
    gets the exact section payload that shell hook expects. New callers (the
    dispatcher) pass --full and get the whole brief instead."""
    if not lines:
        return
    sys.stdout.write(f"@@SECTION:{section}\n")
    for line in lines:
        sys.stdout.write(line)
        if not line.endswith("\n"):
            sys.stdout.write("\n")
    sys.stdout.write("@@END\n")


# --------------------------------------------------------------------------- #
# Date-math sections (were the @@SECTION payload consumed by the old bash hook) #
# --------------------------------------------------------------------------- #
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


FOUNDER_FIELD_RE = re.compile(
    r"^\*\*(Venture|Customer|Stage \(seed\)|Biggest blocker):\*\*\s*(.*?)\s*$"
)
H2_RE = re.compile(r"^##\s+(.+?)\s*$")


def section_founder_move(repo: Path, today: date) -> list[str]:
    """Read core/identity.md ## Founder Snapshot and report whether the brain
    is functional enough to propose. Emits READY, THIN|<gap>, or nothing."""
    text = read_text(repo / "core" / "identity.md")
    if text is None:
        return []
    in_section = False
    fields: dict[str, str] = {}
    for line in text.splitlines():
        h = H2_RE.match(line)
        if h:
            in_section = h.group(1).strip().lower() == "founder snapshot"
            continue
        if not in_section:
            continue
        m = FOUNDER_FIELD_RE.match(line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    if not fields:
        return []

    def is_set(label: str) -> bool:
        v = fields.get(label, "").strip()
        if not v or v.startswith("{{"):
            return False
        if v.startswith("[") and v.endswith("]"):
            return False
        return True

    customer = is_set("Customer")
    stage = is_set("Stage (seed)")
    blocker = is_set("Biggest blocker")
    if customer and (stage or blocker):
        return ["READY"]
    missing: list[str] = []
    if not customer:
        missing.append("customer")
    if not stage and not blocker:
        missing.append("biggest blocker")
    return [f"THIN|{' and '.join(missing)}"]


def _safe_iso(s: str) -> bool:
    try:
        date.fromisoformat(s)
        return True
    except ValueError:
        return False


def section_observations(repo: Path, today: date) -> int:
    obs_dir = repo / "brain" / "observations"
    if not obs_dir.is_dir():
        return 0
    cut = today - timedelta(days=10)
    try:
        return sum(
            1
            for f in obs_dir.glob("*.jsonl")
            if _safe_iso(f.stem) and date.fromisoformat(f.stem) < cut
        )
    except Exception:
        return 0


# --------------------------------------------------------------------------- #
# File-scan sections (were bash awk/grep in the retired shell hook)             #
# --------------------------------------------------------------------------- #
def render_queue(repo: Path) -> list[str]:
    empty = 'Active: 0/3 (queue empty - say "add to queue: <thing>" to start)'
    p = repo / "cadence" / "queue.md"
    text = read_text(p)
    if text is None:
        return [empty]
    active: list[str] = []
    in_section = False
    for raw in text.splitlines():
        if raw.startswith("## ACTIVE"):
            in_section = True
            continue
        if raw.startswith("## "):
            if in_section:
                break
            continue
        if in_section and raw.startswith("(none yet)"):
            continue
        if in_section and raw.startswith("["):
            active.append(raw)
    if not active:
        return [empty]
    out = [f"Active: {len(active)}/3"]
    for line in active[:3]:
        out.append(f"  - {line}")
    return out


OPEN_RE = re.compile(r"Status:\s*\**OPEN")
WEEK3_RE = re.compile(r"Severity.*Week ([3-9]|[1-9][0-9]+)")
HEADER_RE = re.compile(r"^##+\s")


def render_flags(repo: Path) -> list[str]:
    p = repo / "brain" / "flags.md"
    text = read_text(p)
    if text is None:
        return []
    lines = text.splitlines()
    open_count = sum(1 for ln in lines if OPEN_RE.search(ln))
    week3_count = sum(1 for ln in lines if WEEK3_RE.search(ln))
    out = [f"Flags: {open_count} OPEN, {week3_count} Week 3+"]
    last_header = ""
    n = 0
    for ln in lines:
        if HEADER_RE.match(ln):
            last_header = ln
        if OPEN_RE.search(ln) and last_header:
            out.append(f"  - {last_header}")
            last_header = ""
            n += 1
            if n >= 3:
                break
    return out


def render_daily(section: list[str], today: date) -> list[str]:
    if not section:
        return []
    parts = section[0].split("|")
    if parts[0] == "STALE":
        return [f"Daily: STALE (anchor dated {parts[1]}, today is {today.isoformat()}) - refresh before planning"]
    if parts[0] == "CURRENT":
        return [f"Daily: current ({parts[1]})"]
    return []


def render_weekly(section: list[str]) -> list[str]:
    if not section:
        return []
    parts = section[0].split("|")
    if parts[0] == "STALE":
        return [f"Weekly: STALE (week of {parts[1]}, {parts[2]} days old) - run retro before planning"]
    if parts[0] == "CURRENT":
        return [f"Weekly: current (week of {parts[1]})"]
    return []


def render_decisions(repo: Path) -> list[str]:
    p = repo / "context" / "decisions.md"
    text = read_text(p)
    if text is None:
        return []
    count = 0
    in_pending = False
    for ln in text.splitlines():
        if ln.startswith("## Pending"):
            in_pending = True
            continue
        if ln.startswith("## "):
            if in_pending:
                break
            continue
        if in_pending and ln.startswith("### "):
            count += 1
    return [f"Decisions: {count} pending"]


def render_fill(repo: Path) -> list[str]:
    p = repo / "context" / "clients.md"
    text = read_text(p)
    if text is None:
        return []
    # grep -c counts matching LINES, not occurrences - match that exactly.
    fill = sum(1 for ln in text.splitlines() if "[FILL]" in ln)
    if fill > 0:
        return [f"Clients: {fill} [FILL] rows awaiting data"]
    return []


def render_connectors(repo: Path) -> list[str]:
    p = repo / "connectors" / "status.md"
    text = read_text(p)
    if text is None:
        return []
    not_connected = [ln for ln in text.splitlines() if re.match(r"^- .*:\s*not connected", ln)]
    if not not_connected:
        return []
    out = ["", "Connectors not set up:"]
    for ln in not_connected[:5]:
        m = re.match(r"^- ([^:]+):", ln)
        if m:
            name = m.group(1)
            out.append(f'  - {name} - say "connect {name}"')
    return out


def render_rants(repo: Path) -> list[str]:
    rants_dir = repo / "brain" / "rants"
    if not rants_dir.is_dir():
        return []
    unproc = 0
    for f in rants_dir.glob("*.md"):
        text = read_text(f)
        if text is None:
            continue
        unproc += sum(1 for ln in text.splitlines() if re.match(r"^processed:\s*false", ln))
    if unproc <= 0:
        return []
    if unproc >= 3:
        return [f"Unprocessed rants: {unproc} - say \"process my rants\" or run /founder-os:dream. They go stale at 30 days."]
    return [f'Unprocessed rants: {unproc} (say "process my rants" or run /founder-os:dream to distil them)']


def render_compliance(section: list[str]) -> list[str]:
    if not section:
        return []
    out = [""]
    overdue_idx = next((i for i, s in enumerate(section) if s.startswith("OVERDUE|")), None)
    upcoming_idx = next((i for i, s in enumerate(section) if s.startswith("UPCOMING|")), None)
    if overdue_idx is not None:
        count = section[overdue_idx].split("|")[1]
        out.append(f"Compliance: {count} OVERDUE deadline(s) - file or escalate today")
        j = overdue_idx + 1
        while j < len(section) and not section[j].startswith(("OVERDUE|", "UPCOMING|")):
            out.append(section[j])
            j += 1
    if upcoming_idx is not None:
        count = section[upcoming_idx].split("|")[1]
        out.append(f"Compliance: {count} deadline(s) within 30 days")
        j = upcoming_idx + 1
        while j < len(section) and not section[j].startswith(("OVERDUE|", "UPCOMING|")):
            out.append(section[j])
            j += 1
    return out


def render_quarantine(repo: Path) -> list[str]:
    p = repo / "system" / "quarantine.md"
    text = read_text(p)
    if text is None:
        return []
    lines = text.splitlines()
    fence = False
    active = 0
    latest = ""
    for ln in lines:
        if re.match(r"^\s*```", ln):
            fence = not fence
            continue
        if fence:
            continue
        if re.match(r"^\*\*Status:\*\*\s*ACTIVE", ln):
            active += 1
    if active <= 0:
        return []
    fence = False
    for ln in lines:
        if re.match(r"^\s*```", ln):
            fence = not fence
            continue
        if fence:
            continue
        if re.match(r"^## \d{4}-\d{2}-\d{2}", ln):
            latest = ln
            break
    out = ["", f"Quarantine: {active} ACTIVE failure(s) - check system/quarantine.md"]
    if latest:
        out.append(f"  most recent: {latest}")
    return out


def render_decay(section: list[str]) -> list[str]:
    if not section:
        return []
    decay = [s for s in section if s.startswith("DECAY|")]
    noanchor = [s for s in section if s.startswith("NOANCHOR|")]
    out: list[str] = []
    if decay:
        out.append("")
        out.append(f"Review Due ({len(decay)} past decay):")
        for s in decay[:5]:
            _, head, age = s.split("|", 2)
            out.append(f"  - {head} (decayed {age}d ago)")
    if noanchor:
        out.append("")
        out.append(
            f"Decay anchor missing ({len(noanchor)} entries with relative Decay after "
            "but no First observed / Date parked):"
        )
        for s in noanchor[:5]:
            _, head, _age = s.split("|", 2)
            out.append(f"  - {head}")
    return out


def render_memory_diff(repo: Path) -> list[str]:
    script = repo / "scripts" / "memory-diff.py"
    if not script.is_file():
        return []
    try:
        env = dict(os.environ)
        env["PYTHONUTF8"] = "1"
        out = subprocess.run(
            [sys.executable, str(script), str(repo)],
            capture_output=True, text=True, env=env, cwd=str(repo), timeout=15,
        )
        return [ln for ln in out.stdout.splitlines()]
    except Exception:
        return []


def render_founder_move(section: list[str]) -> list[str]:
    if not section:
        return []
    parts = section[0].split("|")
    if parts[0] == "READY":
        return ["", 'Your brain is ready - say "what should I focus on next?" for your move toward a paying customer.']
    if parts[0] == "THIN":
        missing = parts[1] if len(parts) > 1 else "biggest blocker"
        return ["", f"Almost ready to propose - tell me your {missing} in one line and I can name your next move."]
    return []


def render_tip(section: list[str]) -> list[str]:
    if not section:
        return []
    return ["", f"Tip: {section[0]}"]


def render_observations(repo: Path, today: date, want: bool) -> list[str]:
    if not want:
        return ["Observations: disabled (set FOUNDER_OS_OBSERVATIONS=1 to enable)"]
    out = ["Observations: enabled (writing to brain/observations/<date>.jsonl)"]
    rollup_dir = repo / "brain" / "observations" / "_rollups"
    rollup_count = len(list(rollup_dir.glob("*.md"))) if rollup_dir.is_dir() else 0
    out.append(f"  Rollups: {rollup_count} weekly summaries in brain/observations/_rollups/")
    stale = section_observations(repo, today)
    if stale > 0:
        out.append(f"  {stale} JSONL files older than 10 days - say 'roll up observations' to compress old logs.")
    return out


def welcome_banner(repo: Path) -> list[str] | None:
    """When core/identity.md is missing but other markers exist, the install has
    not run setup yet. Return the welcome banner. None means 'not a fresh
    pre-setup install' - either a set-up install or not Founder OS at all."""
    if (repo / "core" / "identity.md").is_file():
        return None
    markers = (
        (repo / "templates" / "bootloader-claude-md.md").is_file()
        or (repo / ".claude" / "settings.json").is_file()
        or (repo / "CLAUDE.md").is_file()
    )
    if not markers:
        return None
    return [
        "Welcome to Founder OS. Say any of these to begin:",
        '  - "set up Founder OS"',
        '  - "help me set up my second brain"',
        '  - "help me onboard" or "what do I do"',
        "",
        "Your personal brain - your files, queryable by you. Not team-shared. Not always-on.",
        "(15-20 minutes. The wizard asks who you are, what you run, and what is slowing you down.)",
    ]


def emit_sections(repo: Path, today: date, want_observations: bool) -> None:
    """Legacy path: emit only the date-math sections as @@SECTION blocks, the
    way the retired session-start-brief.sh consumed them. Preserved for the
    update migration window (see emit())."""
    emit("daily", section_daily(repo, today))
    emit("weekly", section_weekly(repo, today))
    emit("compliance", section_compliance(repo, today))
    emit("decay", section_decay(repo, today))
    emit("founder_move", section_founder_move(repo, today))
    emit("tip", section_tip(repo, today))
    if want_observations:
        emit("observations", [str(section_observations(repo, today))])


def render_full_brief(repo: Path, today: date, want_observations: bool) -> None:
    banner = welcome_banner(repo)
    if banner is not None:
        print("\n".join(banner))
        return

    # A set-up install has core/identity.md; if it is missing and there was no
    # banner, this is not Founder OS - stay silent (matches the old hook).
    if not (repo / "core" / "identity.md").is_file():
        return

    out: list[str] = [f"=== Session brief ({today.isoformat()}) ==="]
    out += render_queue(repo)
    out += render_flags(repo)
    out += render_daily(section_daily(repo, today), today)
    out += render_weekly(section_weekly(repo, today))
    out += render_decisions(repo)
    out += render_fill(repo)
    out += render_connectors(repo)
    out += render_rants(repo)
    out += render_compliance(section_compliance(repo, today))
    out += render_quarantine(repo)
    out += render_decay(section_decay(repo, today))
    out += render_memory_diff(repo)
    out += render_founder_move(section_founder_move(repo, today))
    out += render_tip(section_tip(repo, today))
    out += render_observations(repo, today, want_observations)
    out.append("=== end brief ===")

    print("\n".join(out))


def main() -> int:
    if len(sys.argv) < 3:
        return 0
    repo = Path(sys.argv[1])
    try:
        today = date.fromisoformat(sys.argv[2])
    except ValueError:
        return 0
    want_observations = os.environ.get("FOUNDER_OS_OBSERVATIONS") == "1"

    # --full: render the whole brief (the v1.42 dispatcher path). Without it,
    # fall back to the legacy @@SECTION payload so a retained session-start-brief.sh
    # from a pre-dispatcher install still works during the update migration window.
    if "--full" in sys.argv[3:]:
        render_full_brief(repo, today, want_observations)
    else:
        emit_sections(repo, today, want_observations)
    return 0


if __name__ == "__main__":
    sys.exit(main())
