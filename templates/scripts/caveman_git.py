#!/usr/bin/env python3
"""Caveman's git: invisible version control for a non-technical founder.

Three plain verbs wrap git so the founder gets full version history, ownership,
and undo without typing a git command. Local by default. Never pushes. Never
rewrites history. Restore is fail-safe: it saves your current work FIRST and
ABORTS rather than risk losing anything.

Subcommands:
    save [--message MSG]
        Stage every changed file BY PATH (never `git add -A`) and commit with a
        plain-language, guard-clean message. If the privacy guard blocks the
        commit, the reason is surfaced and nothing is committed.

    history [--limit N] [--full]
        Render the commit log as readable dated events, newest first, grouped by
        day. Handles a fresh repo with zero user commits and a shallow clone
        gracefully ("nothing saved yet") instead of erroring.

    restore --to <committish> --safe-commit
        Phase 1 of undo: save the current state as a safety commit so nothing
        uncommitted is lost. If the safety commit is BLOCKED by the privacy
        guard, exit non-zero and DO NOT touch the working tree (the caller must
        abort). On success, print the set of files that a restore to <target>
        would change, so the caller can confirm with the user.

    restore --to <committish> --apply
        Phase 2 of undo: set the working tree to <target>'s state and record it
        as a NEW commit on top of history. History is never rewritten; every
        prior state stays reachable. Run only after --safe-commit succeeded and
        the user confirmed.

Design guarantees:
    - Explicit staging only. Never `git add -A` or `git add .`.
    - Restore never uses `git reset --hard` and never discards dirty files. It
      safety-commits first, then moves the tree with `git read-tree -u --reset`
      and records a new commit, so undo is itself undoable.
    - Local only. This script never runs `git push`.
    - Honors the privacy guard. If a commit is blocked, the block is reported in
      plain language and never bypassed.

Runtime: stdlib only. Operates on the git repo containing the current directory,
or the repo passed with --repo PATH.
"""

from __future__ import annotations

import argparse
import calendar
import re
import subprocess
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path


def _run(args: list[str], root: Path, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def repo_root(start: str | None) -> Path | None:
    base = Path(start).resolve() if start else Path.cwd()
    res = subprocess.run(
        ["git", "-C", str(base), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        return None
    top = res.stdout.strip()
    return Path(top) if top else None


def changed_paths(root: Path) -> list[str]:
    """Every modified, deleted, or untracked (non-ignored) path, from
    `git status --porcelain -z`. Renames return both old and new path.

    -z is what makes this honest: without it git quotes any path with a
    non-ASCII character ("clients/\\331\\205...md"), `git add` then fails on
    the escaped form, and save reported "Saved" while every Arabic, Hindi or
    accented file name was left behind."""
    res = _run(["status", "--porcelain", "-z", "--untracked-files=all"], root)
    paths: list[str] = []
    records = res.stdout.split("\0")
    i = 0
    while i < len(records):
        rec = records[i]
        i += 1
        if len(rec) < 4:
            continue
        status, path = rec[:2], rec[3:]
        paths.append(path)
        if "R" in status or "C" in status:
            # -z gives the rename source as the next record, unprefixed.
            if i < len(records) and records[i]:
                paths.append(records[i])
            i += 1
    # Stable de-dupe.
    seen: set[str] = set()
    out: list[str] = []
    for p in paths:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _today() -> str:
    return date.today().isoformat()


def _stage(root: Path, paths: list[str]) -> list[tuple[str, str]]:
    """Explicit staging, one path at a time. Never `git add -A` / `.`.
    Returns (path, git's reason) for every path git refused, so no caller can
    report a save that did not happen."""
    failed: list[tuple[str, str]] = []
    for p in paths:
        res = _run(["add", "--", p], root)
        if res.returncode != 0:
            reason = (res.stderr or res.stdout).strip().splitlines()
            failed.append((p, reason[-1] if reason else f"git add exit {res.returncode}"))
    return failed


def _report_unstaged(failed: list[tuple[str, str]]) -> None:
    print(f"{len(failed)} file(s) could not be saved:")
    for path, reason in failed:
        print(f"  {path}  ({reason})")


def _auto_message(n: int) -> str:
    """Plain-language, guard-clean commit message. No dashes, no names, no why we
    do not know."""
    noun = "file" if n == 1 else "files"
    return f"Save work in progress: {n} {noun} updated {_today()}"


def cmd_save(root: Path, message: str | None) -> int:
    paths = changed_paths(root)
    if not paths:
        print("Nothing to save. Your work is already saved.")
        return 0
    failed = _stage(root, paths)
    staged = len(paths) - len(failed)
    if staged == 0:
        print("Nothing was saved.")
        _report_unstaged(failed)
        return 1
    msg = message.strip() if message and message.strip() else _auto_message(staged)
    commit = _run(["commit", "-m", msg], root)
    if commit.returncode != 0:
        out = (commit.stdout + "\n" + commit.stderr).strip()
        print("Could not save. The privacy guard or a commit hook stopped this:")
        print(out)
        print(
            "\nNothing was saved. Fix what the guard flagged above (a private name, "
            "an AI-attribution line, or a secret), then say "
            '"save my work" again.'
        )
        return 1
    # Show what was saved, in plain terms.
    stat = _run(["show", "--stat", "--oneline", "HEAD"], root)
    if failed:
        print(f"Saved {staged} of {len(paths)} files. Here is what was saved:")
        print(stat.stdout.strip())
        _report_unstaged(failed)
        return 1
    print("Saved. Here is what changed:")
    print(stat.stdout.strip())
    return 0


def _has_any_commit(root: Path) -> bool:
    return _run(["rev-parse", "--verify", "HEAD"], root).returncode == 0


def cmd_history(root: Path, limit: int, full: bool) -> int:
    if not _has_any_commit(root):
        print("Nothing saved yet. Say \"save my work\" to record your first version.")
        return 0
    # Count user-reachable commits. A fresh clone may hold only the upstream
    # commit; a shallow clone may hold one. Either way, render what exists.
    fmt = "%h%x09%ad%x09%s"
    args = ["log", f"--pretty=format:{fmt}", "--date=format:%Y-%m-%d %H:%M"]
    if not full and limit > 0:
        args.append(f"-n{limit}")
    res = _run(args, root)
    lines = [l for l in res.stdout.splitlines() if l.strip()]
    if not lines:
        print("Nothing saved yet. Say \"save my work\" to record your first version.")
        return 0
    # Group by day, newest first.
    print(f"VERSION HISTORY ({len(lines)} saved version(s) shown, newest first)")
    current_day = None
    for line in lines:
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        short_sha, when, subject = parts[0], parts[1], parts[2]
        day, _, clock = when.partition(" ")
        if day != current_day:
            current_day = day
            print(f"\n{day}")
        print(f"  {clock}  {subject}")
    print(
        "\nTo undo to one of these, say something like "
        '"undo to before this morning" or name the day.'
    )
    return 0


_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
_MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December")


def _day_words(d: date) -> str:
    """'Friday 16 October', with the year only when it is not this year."""
    text = f"{_WEEKDAYS[d.weekday()].capitalize()} {d.day} {_MONTHS[d.month - 1]}"
    return text if d.year == date.today().year else f"{text} {d.year}"


def _months_back(when: datetime, n: int) -> datetime:
    y, m = divmod(when.year * 12 + when.month - 1 - n, 12)
    last_day = calendar.monthrange(y, m + 1)[1]
    return when.replace(year=y, month=m + 1, day=min(when.day, last_day))


def _date_point(ref: str, now: datetime) -> tuple[datetime, str] | None:
    """The moment a plain date phrase points at (local time), and that moment in
    plain words. None when the text is not one of these phrases.

    The rule is the founder's, not git's. A day named on its own means the end
    of that day: "yesterday" and "friday" are the last version saved that day
    or earlier. "today" and "this morning" mean the start of today, since there
    is nothing to go back to later today. "before" a day means its start. A
    weekday is the most recent one strictly before today. git's own date
    parser read "this morning" and "today" as now and "yesterday" as 24 hours
    ago, so "undo to before this morning" restored the newest save."""
    text = " ".join(ref.lower().split())
    before = text.startswith("before ")
    if before:
        text = text[len("before "):]
    today = now.date()
    if text in ("today", "this morning"):
        return datetime.combine(today, time.min), f"the start of today ({_day_words(today)})"
    if text == "last week":
        monday = today - timedelta(days=today.weekday())
        if before:
            start = monday - timedelta(days=7)
            return datetime.combine(start, time.min), f"the start of last week ({_day_words(start)})"
        sunday = monday - timedelta(days=1)
        return datetime.combine(monday, time.min), f"the end of last week ({_day_words(sunday)})"
    day = None
    if text in ("yesterday", "last night"):
        day = today - timedelta(days=1)
    elif re.fullmatch(r"(?:last )?(" + "|".join(_WEEKDAYS) + ")", text):
        wanted = _WEEKDAYS.index(text.split()[-1])
        day = today - timedelta(days=(today.weekday() - wanted) % 7 or 7)
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        try:
            day = date.fromisoformat(text)
        except ValueError:
            return None
    if day is not None:
        if before:
            return datetime.combine(day, time.min), f"the start of {_day_words(day)}"
        return (datetime.combine(day + timedelta(days=1), time.min),
                f"the end of {_day_words(day)}")
    m = re.fullmatch(r"(\d+|an?|one) (minute|hour|day|week|month)s? ago", text)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else 1
        unit = m.group(2)
        point = _months_back(now, n) if unit == "month" else now - timedelta(**{unit + "s": n})
        return point, f"{text} ({_day_words(point.date())}, {point:%H:%M})"
    return None


def _resolve(root: Path, ref: str) -> tuple[str | None, str | None]:
    """A commit, or a plain date phrase ("yesterday", "this morning", "friday",
    "2026-10-20", "2 days ago"), read as the last version saved before the
    moment `_date_point` gives.

    Returns (sha, words): words is that moment in plain words, None when `ref`
    was a commit. (None, words) means the phrase was understood and no save
    is that old. (None, None) means the text is neither."""
    res = _run(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], root)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip(), None
    point = _date_point(ref or "", datetime.now())
    if point is None:
        return None, None
    when, words = point
    # A naive datetime is local time. git's --before keeps a commit made at
    # that very second, so the cutoff is one second earlier: strictly before.
    cutoff = int(when.timestamp()) - 1
    res = _run(["rev-list", "-1", f"--before={cutoff}", "HEAD"], root)
    sha = res.stdout.strip()
    return (sha if res.returncode == 0 and sha else None), words


def _not_found(target: str, words: str | None) -> int:
    if words:
        print(f"Could not find a saved version from before {words}.")
    else:
        print(f"Could not find a saved version matching '{target}'.")
    print('Say "what changed" to see your saved versions, then name one.')
    return 2


def _restore_safe_commit(root: Path, target: str) -> int:
    sha, words = _resolve(root, target)
    if not sha:
        return _not_found(target, words)
    if words:
        print(f"Read '{target}' as: the last version saved before {words}.")
    # Echo the absolute SHA. The safety commit below moves HEAD, so the caller
    # MUST pass this resolved SHA (not a relative ref like HEAD~1) to --apply.
    print(f"Resolved target: {sha}")
    when = _run(["log", "-1", "--format=%ad  %s", "--date=format:%Y-%m-%d %H:%M", sha], root)
    if when.stdout.strip():
        print(f"That version: {when.stdout.strip()}")
    paths = changed_paths(root)
    if paths:
        failed = _stage(root, paths)
        if failed:
            print("UNDO ABORTED. Some of your current work could not be safety-saved first:")
            _report_unstaged(failed)
            print("\nNothing was changed and nothing was lost. The undo did NOT run.")
            return 1
        msg = f"Safety save before undo: {len(paths)} file(s) protected {_today()}"
        commit = _run(["commit", "-m", msg], root)
        if commit.returncode != 0:
            out = (commit.stdout + "\n" + commit.stderr).strip()
            print("UNDO ABORTED. Your current work could not be safety-saved first:")
            print(out)
            print(
                "\nNothing was changed and nothing was lost. The undo did NOT run. "
                "Fix what the guard flagged above, then try the undo again."
            )
            return 1
        print(f"Safety save done: {len(paths)} file(s) protected before undo.")
    else:
        print("Working tree is clean. No safety save needed.")
    # Show what an undo to target would change.
    diff = _run(["diff", "--stat", "HEAD", sha], root)
    changed = diff.stdout.strip()
    if not changed:
        print(f"\nYou are already at that state. Nothing to undo.")
        return 0
    print(f"\nUndo to {target} would change these files:")
    print(changed)
    print(
        '\nConfirm with the user, then run the apply phase to record the undo as a '
        "new version (your current state stays recoverable)."
    )
    return 0


def _restore_apply(root: Path, target: str) -> int:
    sha, words = _resolve(root, target)
    if not sha:
        return _not_found(target, words)
    # The working tree must be clean (safe-commit phase already ran). If it is
    # not, refuse rather than risk losing changes.
    if changed_paths(root):
        print(
            "UNDO ABORTED. There are unsaved changes. Run the safety-save phase "
            "first so nothing is lost."
        )
        return 1
    # Set index + working tree to the target tree (handles deletions correctly).
    # This does NOT move HEAD; the new state is recorded as a fresh commit below.
    rt = _run(["read-tree", "-u", "--reset", sha], root)
    if rt.returncode != 0:
        print("Could not stage the undo:")
        print((rt.stdout + "\n" + rt.stderr).strip())
        return 1
    staged = _run(["diff", "--cached", "--name-only"], root)
    if not staged.stdout.strip():
        print("You are already at that state. Nothing to undo.")
        return 0
    short = sha[:8]
    msg = f"Undo to earlier version ({short}) {_today()}"
    commit = _run(["commit", "-m", msg], root)
    if commit.returncode != 0:
        out = (commit.stdout + "\n" + commit.stderr).strip()
        print("The undo could not be recorded by a commit hook:")
        print(out)
        print(
            "\nYour working files are now at the earlier version, but it is not yet "
            "saved as a new version. Your prior state is still safe in history "
            '(say "what changed" to see it). Resolve the issue above, then say '
            '"save my work".'
        )
        return 1
    print(f"Undo complete. Your files are back to the earlier version ({short}).")
    print(
        "This was recorded as a new version, so your prior state stays recoverable. "
        'Say "what changed" to see it, or undo again to step back further.'
    )
    return 0


def cmd_restore(root: Path, target: str | None, safe_commit: bool, apply: bool, list_only: bool) -> int:
    if list_only or not target:
        return cmd_history(root, limit=15, full=False)
    if safe_commit:
        return _restore_safe_commit(root, target)
    if apply:
        return _restore_apply(root, target)
    print("Specify --safe-commit (phase 1) or --apply (phase 2).")
    return 2


def main() -> int:
    # A file name or message in Arabic on a cp1252 console must not crash the
    # report after the save already happened.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(prog="caveman_git", description="Invisible version control verbs.")
    parser.add_argument("--repo", help="Repo path (defaults to the repo containing the current dir).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Save your work as a new version.")
    p_save.add_argument("--message", help="Optional plain-language message.")

    p_hist = sub.add_parser("history", help="Show your saved versions.")
    p_hist.add_argument("--limit", type=int, default=20)
    p_hist.add_argument("--full", action="store_true")

    p_rest = sub.add_parser("restore", help="Undo to an earlier version (non-destructive).")
    p_rest.add_argument("--to", help="Target version: a commit, or a day like 'yesterday', "
                                     "'this morning', 'friday' or '2026-10-20', or '2 days ago' "
                                     "(the last version saved before then).")
    p_rest.add_argument("--safe-commit", action="store_true", help="Phase 1: safety-save current work.")
    p_rest.add_argument("--apply", action="store_true", help="Phase 2: record the undo.")
    p_rest.add_argument("--list", action="store_true", help="List candidate versions.")

    args = parser.parse_args()

    root = repo_root(args.repo)
    if root is None:
        print("This folder is not under version control yet, so there is nothing to "
              "save or undo. Run setup, or ask to turn on version control.")
        return 1

    if args.command == "save":
        return cmd_save(root, args.message)
    if args.command == "history":
        return cmd_history(root, args.limit, args.full)
    if args.command == "restore":
        return cmd_restore(root, args.to, args.safe_commit, args.apply, args.list)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
