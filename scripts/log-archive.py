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
the log is under the cap it does nothing. Each file is replaced in one step, the archive
before the log, so a run that stops part way leaves an entry in both files, never in
neither, and the next run does not copy it twice.

Usage:
    python scripts/log-archive.py             # archive brain/log.md past a 300-line cap
    python scripts/log-archive.py --cap 200   # use a different line cap
    python scripts/log-archive.py --dry-run   # report what would move, write nothing
    python scripts/log-archive.py --log <path># archive a log at a non-default path
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ENTRY_DATE_HEADING  # noqa: E402

# The one dated-entry heading the whole OS reads (_common.ENTRY_DATE_HEADING):
# "### [YYYY-MM-DD] ...", "### YYYY-MM-DD ...", "### YYYY-MM-DD HH:MM - ...".
ENTRY_RE = ENTRY_DATE_HEADING
POINTER_MARK = "<!-- log-archive:pointer -->"
POINTER_TEXT_PREFIX = "*Older entries archived to brain/archive/."


class Entry:
    __slots__ = ("day", "month", "lines")

    def __init__(self, day: str | None, lines: list[str]):
        self.day = day
        self.month = day[:7] if day else None
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

    Entries come back in file order. The existing pointer (the marker line and
    the one italic line this script writes under it) is pulled out so re-runs
    update it instead of stacking duplicates. Only those lines are pulled out:
    everything after them stays in the log. The pointer used to be read as
    "marker to end of file", so every entry a skill appended at the bottom
    after the first archive (skills/brain-log says "Append") was deleted on the
    next run - 160 of them in the review's reproduction.
    """
    lines = text.splitlines()
    mask = comment_mask(lines)

    pointer: list[str] = []
    for i, ln in enumerate(lines):
        if mask[i] or ln.strip() != POINTER_MARK:
            continue
        end = i + 1
        if end < len(lines) and lines[end].strip().startswith(POINTER_TEXT_PREFIX):
            end += 1
        pointer = lines[i:end]
        lines = lines[:i] + lines[end:]
        mask = mask[:i] + mask[end:]
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
        entries.append(Entry(m.group(1) if m else None, block))
    return preamble, entries, pointer


def plan(preamble: list[str], entries: list[Entry], cap: int) -> tuple[list[Entry], list[Entry]]:
    """Split entries into (kept, archived), each in file order.

    The newest entries by DATE stay, not the topmost ones: the template puts
    new entries on top but capture skills append at the bottom, so position
    says nothing reliable about age. Dated entries are ranked newest first
    (file order breaks a tie) and kept while they fit under the cap; from the
    first one that does not fit, every older one is archived. The newest one
    always stays. Undated entries are never archived (they cannot be filed
    under a month)."""
    used = len(preamble) + sum(len(e.lines) for e in entries if e.day is None)
    ranked = sorted(
        (i for i, e in enumerate(entries) if e.day is not None),
        key=lambda i: (entries[i].day, -i),
        reverse=True,
    )
    keep_idx = {i for i, e in enumerate(entries) if e.day is None}
    archived_idx: set[int] = set()
    kept_dated = False
    archiving = False
    for i in ranked:
        size = len(entries[i].lines)
        if not archiving and (not kept_dated or used + size <= cap):
            keep_idx.add(i)
            used += size
            kept_dated = True
        else:
            archiving = True
            archived_idx.add(i)
    kept = [e for i, e in enumerate(entries) if i in keep_idx]
    archived = [e for i, e in enumerate(entries) if i in archived_idx]
    return kept, archived


def rstrip_blanks(lines: list[str]) -> list[str]:
    out = list(lines)
    while out and out[-1].strip() == "":
        out.pop()
    return out


def write_whole(path: Path, text: str) -> None:
    """Replace a file in one step: write a temp file in the same folder, then
    swap it in. A crash mid-write leaves the old file as it was, never half of
    it. The archive is written before the log, so a crash between the two can
    leave an entry in both files but never in neither."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


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
    already = 0
    for month in sorted(by_month, reverse=True):
        dest = archive_dir / f"log-{month}.md"
        existing = dest.read_text(encoding="utf-8").splitlines() if dest.exists() else None
        # An entry already in this month's archive is not copied again. A run
        # that stopped after the archive write and before the log write leaves
        # it in both files, and the rerun must not archive it a second time.
        on_file = Counter(tuple(rstrip_blanks(e.lines))
                          for e in split_log("\n".join(existing or []))[1])
        new_block: list[str] = []
        fresh = 0
        for e in sorted(by_month[month], key=lambda x: x.day, reverse=True):
            block = tuple(rstrip_blanks(e.lines))
            if on_file[block]:
                on_file[block] -= 1
                already += 1
                continue
            new_block.extend(block)
            new_block.append("")
            fresh += 1
        if not fresh:
            continue
        if existing is not None:
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
            try:
                archive_dir.mkdir(parents=True, exist_ok=True)
                write_whole(dest, "\n".join(rstrip_blanks(merged)) + "\n")
            except OSError as exc:
                print(f"LOG ARCHIVE - {today}")
                print(f"Could not write {dest.as_posix()} ({exc.strerror or exc}). "
                      "Nothing was taken out of the log. Fix that, then run this again.")
                return 1
        moved_report.append(f"{dest.as_posix()} ({fresh})")

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
        try:
            write_whole(log_path, new_log)
        except OSError as exc:
            print(f"LOG ARCHIVE - {today}")
            print(f"Could not rewrite {log_path.as_posix()} ({exc.strerror or exc}). The archive "
                  "already holds the moved entries, so running this again is safe: they are not "
                  "copied twice.")
            return 1

    new_count = len(new_log.splitlines())
    print(f"LOG ARCHIVE - {today}")
    print(f"Cap {args.cap} lines. Log was {total_lines} lines, {len(entries)} entries.")
    verb = "Would archive" if args.dry_run else "Archived"
    print(f"{verb} {len(archived) - already} entries to: {', '.join(moved_report) or 'no new file'}")
    if already:
        print(f"{already} more were already in the archive from a run that stopped part way, "
              "so they were taken out of the log without being copied twice.")
    print(f"Log {'would be' if args.dry_run else 'now'} {new_count} lines, {len(kept)} entries. Pointer updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
