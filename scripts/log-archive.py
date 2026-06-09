#!/usr/bin/env python3
"""Age the brain log: move old entries out of brain/log.md into monthly archives.

brain/log.md is the running log, capped (default 300 lines) so a long-lived install does
not carry months of history in the file every skill reads. When the log grows past the
cap, the oldest entries move to brain/archive/log-YYYY-MM.md and log.md keeps only the
most recent entries plus a one-line pointer to the archive. The pointer is the cache
summary: enough to know history exists and where it lives, without the full detail. This
is what keeps the install lean over months and stops a long session bloating on a file
every skill reads.

Deterministic, stdlib only, no LLM call, no network. Never splits an entry. Entries it
cannot date are kept in log.md (never archived to an unknown month). Safe to re-run: once
the log is under the cap it does nothing.

Usage:
    python scripts/log-archive.py             # archive brain/log.md past a 300-line cap
    python scripts/log-archive.py --cap 200   # use a different line cap
    python scripts/log-archive.py --dry-run   # report what would move, write nothing
    python scripts/log-archive.py --log <path># archive a log at a non-default path
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# Matches "### [YYYY-MM-DD] ..." and "### YYYY-MM-DD ..." (brackets optional).
ENTRY_RE = re.compile(r"^###\s+\[?(\d{4})-(\d{2})-(\d{2})\]?")
POINTER_MARK = "<!-- log-archive:pointer -->"


class Entry:
    __slots__ = ("month", "lines")

    def __init__(self, month: str | None, lines: list[str]):
        self.month = month
        self.lines = lines


def comment_mask(lines: list[str]) -> list[bool]:
    """For each line return True if it sits inside an HTML comment block.

    Keeps the example block in the log template from being read as real entries.
    """
    mask: list[bool] = []
    in_comment = False
    for ln in lines:
        if in_comment:
            mask.append(True)
            if "-->" in ln:
                in_comment = False
        else:
            mask.append(False)
            after = ln.split("<!--", 1)
            if len(after) == 2 and "-->" not in after[1]:
                in_comment = True
    return mask


def split_log(text: str) -> tuple[list[str], list[Entry], list[str]]:
    """Return (preamble_lines, entries, existing_pointer_lines).

    Entries are newest-first (the log keeps most-recent on top). The existing pointer
    footer, if any, is pulled out so re-runs update it instead of stacking duplicates.
    """
    lines = text.splitlines()
    mask = comment_mask(lines)

    # Pull off an existing pointer footer first (from POINTER_MARK to end).
    pointer: list[str] = []
    for i, ln in enumerate(lines):
        if ln.strip() == POINTER_MARK:
            pointer = lines[i:]
            lines = lines[:i]
            mask = mask[:i]
            break

    starts = [
        i for i, ln in enumerate(lines) if not mask[i] and ENTRY_RE.match(ln)
    ]
    if not starts:
        return lines, [], pointer

    preamble = lines[: starts[0]]
    entries: list[Entry] = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        block = lines[start:end]
        m = ENTRY_RE.match(block[0])
        month = f"{m.group(1)}-{m.group(2)}" if m else None
        entries.append(Entry(month, block))
    return preamble, entries, pointer


def plan(preamble: list[str], entries: list[Entry], cap: int) -> tuple[list[Entry], list[Entry]]:
    """Split entries into (kept_newest, archived_oldest). Never archives undated entries."""
    kept: list[Entry] = []
    archived: list[Entry] = []
    used = len(preamble)
    archiving = False
    for e in entries:
        if not archiving and (not kept or used + len(e.lines) <= cap):
            kept.append(e)
            used += len(e.lines)
        elif e.month is None:
            kept.append(e)  # cannot file an undated entry under a month - keep it
            used += len(e.lines)
        else:
            archiving = True
            archived.append(e)
    return kept, archived


def rstrip_blanks(lines: list[str]) -> list[str]:
    out = list(lines)
    while out and out[-1].strip() == "":
        out.pop()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Age brain/log.md into monthly archives.")
    ap.add_argument("--log", default="brain/log.md", help="path to the log file")
    ap.add_argument("--cap", type=int, default=300, help="line cap before archiving (default 300)")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    log_path = Path(args.log)
    today = date.today().isoformat()
    if not log_path.exists():
        print(f"LOG ARCHIVE - {today}")
        print(f"No log at {log_path}. Nothing to do.")
        return 0

    text = log_path.read_text(encoding="utf-8")
    total_lines = len(text.splitlines())
    preamble, entries, _pointer = split_log(text)

    if total_lines <= args.cap:
        print(f"LOG ARCHIVE - {today}")
        print(f"Log is {total_lines} lines (cap {args.cap}). Nothing to archive.")
        return 0

    kept, archived = plan(preamble, entries, args.cap)
    if not archived:
        print(f"LOG ARCHIVE - {today}")
        print(f"Log is {total_lines} lines but no older dated entry can be moved under the cap.")
        return 0

    # Group archived entries by month, newest-first within each month.
    by_month: dict[str, list[Entry]] = {}
    for e in archived:
        by_month.setdefault(e.month, []).append(e)

    archive_dir = log_path.parent / "archive"
    moved_report: list[str] = []
    for month in sorted(by_month, reverse=True):
        dest = archive_dir / f"log-{month}.md"
        new_block: list[str] = []
        for e in by_month[month]:
            new_block.extend(rstrip_blanks(e.lines))
            new_block.append("")
        if dest.exists():
            existing = dest.read_text(encoding="utf-8").splitlines()
            # insert new entries after the header block (first blank-separated section)
            head_end = 0
            for i, ln in enumerate(existing):
                if ENTRY_RE.match(ln):
                    head_end = i
                    break
            else:
                head_end = len(existing)
            merged = existing[:head_end] + new_block + existing[head_end:]
        else:
            header = [
                f"# Log archive {month}",
                "",
                "> Archived from brain/log.md by log-archive.py. Reference only - newest first.",
                "",
            ]
            merged = header + new_block
        if not args.dry_run:
            archive_dir.mkdir(parents=True, exist_ok=True)
            dest.write_text("\n".join(rstrip_blanks(merged)) + "\n", encoding="utf-8")
        moved_report.append(f"{dest.as_posix()} ({len(by_month[month])})")

    # Rebuild log.md: preamble + kept entries + refreshed pointer footer.
    months_on_file = sorted(
        {p.stem.replace("log-", "") for p in archive_dir.glob("log-*.md")}
    ) if archive_dir.exists() or not args.dry_run else sorted(by_month)
    if args.dry_run and not archive_dir.exists():
        months_on_file = sorted(by_month)

    body: list[str] = rstrip_blanks(preamble) + [""]
    for e in kept:
        body.extend(rstrip_blanks(e.lines))
        body.append("")
    pointer_block = [
        POINTER_MARK,
        f"*Older entries archived to brain/archive/. Months on file: {', '.join(months_on_file)}. "
        "Pull from there when historical context is needed.*",
    ]
    new_log = "\n".join(rstrip_blanks(body) + [""] + pointer_block) + "\n"

    if not args.dry_run:
        log_path.write_text(new_log, encoding="utf-8")

    new_count = len(new_log.splitlines())
    print(f"LOG ARCHIVE - {today}")
    print(f"Cap {args.cap} lines. Log was {total_lines} lines, {len(entries)} entries.")
    verb = "Would archive" if args.dry_run else "Archived"
    print(f"{verb} {len(archived)} entries to: {', '.join(moved_report)}")
    print(f"Log {'would be' if args.dry_run else 'now'} {new_count} lines, {len(kept)} entries. Pointer updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
