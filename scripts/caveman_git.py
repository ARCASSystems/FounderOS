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
import subprocess
import sys
from datetime import datetime, date
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


def _dequote(path: str) -> str:
    """git quotes paths with special chars in double quotes. Strip them for the
    common case; ordinary OS markdown paths are never quoted."""
    path = path.strip()
    if len(path) >= 2 and path[0] == '"' and path[-1] == '"':
        return path[1:-1]
    return path


def changed_paths(root: Path) -> list[str]:
    """Every modified, deleted, or untracked (non-ignored) path, from
    `git status --porcelain`. Renames return both old and new path."""
    res = _run(["status", "--porcelain"], root)
    paths: list[str] = []
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        body = line[3:] if len(line) > 3 else line
        if " -> " in body:  # rename: "old -> new"
            old, _, new = body.partition(" -> ")
            paths.append(_dequote(old))
            paths.append(_dequote(new))
        else:
            paths.append(_dequote(body))
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


def _stage(root: Path, paths: list[str]) -> None:
    # Explicit staging, one path at a time. Never `git add -A` / `.`.
    for p in paths:
        _run(["add", "--", p], root)


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
    _stage(root, paths)
    msg = message.strip() if message and message.strip() else _auto_message(len(paths))
    commit = _run(["commit", "-m", msg], root)
    if commit.returncode != 0:
        out = (commit.stdout + "\n" + commit.stderr).strip()
        print("Could not save. The privacy guard or a commit hook stopped this:")
        print(out)
        print(
            "\nNothing was saved. Fix what the guard flagged above (a private name, "
            "an em or en dash, an AI-attribution line, or a secret), then say "
            '"save my work" again.'
        )
        return 1
    # Show what was saved, in plain terms.
    stat = _run(["show", "--stat", "--oneline", "HEAD"], root)
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


def _resolve(root: Path, ref: str) -> str | None:
    res = _run(["rev-parse", "--verify", f"{ref}^{{commit}}"], root)
    if res.returncode != 0:
        return None
    return res.stdout.strip()


def _restore_safe_commit(root: Path, target: str) -> int:
    sha = _resolve(root, target)
    if not sha:
        print(f"Could not find a saved version matching '{target}'.")
        print('Say "what changed" to see your saved versions, then name one.')
        return 2
    # Echo the absolute SHA. The safety commit below moves HEAD, so the caller
    # MUST pass this resolved SHA (not a relative ref like HEAD~1) to --apply.
    print(f"Resolved target: {sha}")
    paths = changed_paths(root)
    if paths:
        _stage(root, paths)
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
    sha = _resolve(root, target)
    if not sha:
        print(f"Could not find a saved version matching '{target}'.")
        return 2
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
    parser = argparse.ArgumentParser(prog="caveman_git", description="Invisible version control verbs.")
    parser.add_argument("--repo", help="Repo path (defaults to the repo containing the current dir).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Save your work as a new version.")
    p_save.add_argument("--message", help="Optional plain-language message.")

    p_hist = sub.add_parser("history", help="Show your saved versions.")
    p_hist.add_argument("--limit", type=int, default=20)
    p_hist.add_argument("--full", action="store_true")

    p_rest = sub.add_parser("restore", help="Undo to an earlier version (non-destructive).")
    p_rest.add_argument("--to", help="Target version (a commit, or a git date like 'yesterday').")
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
