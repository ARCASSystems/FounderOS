"""Session changes tracker: snapshot-before-write + per-session manifest.

The pre-git undo floor. On an install with no git yet (the ZIP path before
"own my history"), "what did you change" and "put that file back" must still
have real answers. This script provides both, and it keeps running after git
arrives as a second net under the save/history/restore verbs.

Two mechanisms, one script, wired as Claude Code hooks:

- --record  (PreToolUse on Write|Edit|MultiEdit|NotebookEdit)
  Before the write lands, copy the file's current bytes into a session-scoped
  snapshot tree at state/.snapshots/<sid>/<repo-relative-path>, and append a
  one-line record to state/.session-changes/<sid>.jsonl. The snapshot is the
  exact pre-edit state, so anything broken this session is one copy away from
  recovery - independent of git, so it covers never-committed files too. Only
  the FIRST touch of a path per session is snapshotted (preserves the true
  session-start version across repeated edits).

- --manifest  (Stop)
  Read this session's change log, dedupe by path, compute +adds/-dels per
  file (git numstat when git exists, raw line count for new files), and render
  state/session-manifest.md - a scannable "here is exactly what changed"
  artifact with a recover command per file. Prints a one-line summary.

- --print  (the /changes command)
  Re-render and print the most recent session's manifest on demand.

- --restore <relpath> [--session <sid>]
  Copy a snapshot back over the working file. The one-command undo.

Design rules this script must honour (they are why the feature exists):
- It must never become invisible work itself. All file IO is explicit UTF-8.
  Every failure is written to system/quarantine.md (visible), never silently
  swallowed. --record ALWAYS exits 0 so it can never block or slow a write.
- Both the bash and PowerShell hook variants may fire on the same event on a
  machine that has both shells. --record dedupes a same-second duplicate and
  --manifest skips a just-rendered manifest, so dual-shell machines do not
  double-count.
- ASCII-only stdout (hook output must survive any Windows codepage).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MUTATING_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
SNAPSHOT_MAX_BYTES = 2 * 1024 * 1024  # skip snapshotting files larger than 2MB
KEEP_SESSIONS = 12  # prune snapshot/log dirs beyond this many recent sessions
DUP_WINDOW_SECONDS = 3  # dual-shell hook variants firing twice collapse to one


def repo_root() -> Path:
    import os

    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


ROOT = repo_root()
STATE = ROOT / "state"
SNAP_DIR = STATE / ".snapshots"
LOG_DIR = STATE / ".session-changes"
MANIFEST = STATE / "session-manifest.md"
QUARANTINE = ROOT / "system" / "quarantine.md"


def quarantine(source: str, trigger: str, err: str, context: str) -> None:
    """Make a failure visible instead of swallowing it (the whole point)."""
    try:
        QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        head = str(err).splitlines()[0] if str(err).strip() else "unknown error"
        entry = (
            f"\n## {ts} - {source} - {head}\n\n"
            f"**Source:** {source}\n"
            f"**Trigger:** {trigger}\n"
            f"**Error:** {err}\n"
            f"**Context:** {context}\n"
            f"**Status:** ACTIVE\n\n---\n"
        )
        with QUARANTINE.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except Exception:
        # Last resort: never raise out of the quarantine writer.
        pass


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def short_sid(session_id: str) -> str:
    sid = (session_id or "nosession").strip()
    # Keep filesystem-safe; sessions are uuids but be defensive.
    safe = "".join(c for c in sid if c.isalnum() or c in "-_")
    return (safe or "nosession")[:16]


def read_stdin_json() -> dict:
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return {}
        raw = sys.stdin.buffer.read()
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8", errors="replace"))
    except Exception:
        return {}


def _normalize_path(p: str) -> str:
    """Normalize an MSYS / Git-Bash style path (/c/foo) to native (c:/foo).

    Claude Code on Windows passes native paths, but tests and some shells pass
    the POSIX form; Python-on-Windows would resolve /c/foo against the current
    drive root and land outside the repo. Cheap to handle both.
    """
    if len(p) >= 3 and p[0] == "/" and p[1].isalpha() and p[2] == "/":
        return f"{p[1]}:/{p[3:]}"
    return p


def rel_path(p: str) -> str | None:
    """Repo-relative POSIX path, or None if outside the repo."""
    try:
        ap = Path(_normalize_path(p)).resolve()
        rp = ap.relative_to(ROOT)
        return rp.as_posix()
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# --record : PreToolUse                                                         #
# --------------------------------------------------------------------------- #
def _is_duplicate(log_file: Path, tool: str, path: str) -> bool:
    """True when the last record matches tool+path within DUP_WINDOW_SECONDS.

    Dual-shell machines run both the bash and PowerShell hook variants for the
    same tool call; the second arrival is a duplicate, not a second write.
    """
    try:
        if not log_file.is_file():
            return False
        with log_file.open("rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - 4096))
            tail = fh.read().decode("utf-8", errors="replace")
        lines = [ln for ln in tail.splitlines() if ln.strip()]
        if not lines:
            return False
        last = json.loads(lines[-1])
        if last.get("tool") != tool or last.get("path") != path:
            return False
        prev = datetime.fromisoformat(last.get("ts", ""))
        age = abs(time.time() - prev.timestamp())
        return age <= DUP_WINDOW_SECONDS
    except Exception:
        return False


def cmd_record() -> int:
    data = read_stdin_json()
    tool = str(data.get("tool_name", ""))
    if tool not in MUTATING_TOOLS:
        return 0

    ti = data.get("tool_input") or {}
    target = ti.get("file_path") or ti.get("notebook_path") or ""
    if not target:
        return 0

    sid = short_sid(str(data.get("session_id", "")))
    rel = rel_path(target)

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"{sid}.jsonl"

        log_path = rel if rel is not None else target
        if _is_duplicate(log_file, tool, log_path):
            return 0

        action = "modify"
        snapped = False
        src = Path(_normalize_path(target))
        exists = src.is_file()
        if not exists:
            action = "create"

        # Snapshot only the first touch per path this session, only if the file
        # exists (a "create" has nothing to snapshot). Mirror the repo tree so
        # restore is a plain copy and there are no filename collisions.
        if exists and rel is not None:
            snap_target = SNAP_DIR / sid / rel
            if not snap_target.exists():
                try:
                    size = src.stat().st_size
                    if size <= SNAPSHOT_MAX_BYTES:
                        snap_target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, snap_target)
                        snapped = True
                except Exception as exc:  # snapshot best-effort, never block
                    quarantine(
                        "scripts/session_changes.py --record",
                        "snapshot-before-write",
                        f"could not snapshot {rel}: {exc}",
                        "PreToolUse hook; the edit still proceeds, only the "
                        "recovery snapshot was skipped.",
                    )

        record = {
            "ts": now_iso(),
            "tool": tool,
            "path": log_path,
            "in_repo": rel is not None,
            "action": action,
            "snapshot": snapped,
        }
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")
    except Exception as exc:
        quarantine(
            "scripts/session_changes.py --record",
            "session-change record",
            f"{exc}",
            "PreToolUse hook failed to log a change. The edit itself was not "
            "affected (hook runs alongside, never blocks).",
        )
    return 0


# --------------------------------------------------------------------------- #
# manifest rendering                                                            #
# --------------------------------------------------------------------------- #
def latest_log() -> Path | None:
    if not LOG_DIR.is_dir():
        return None
    logs = sorted(LOG_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def git_numstat(rel: str) -> tuple[int | None, int | None]:
    """(adds, dels) from working tree vs HEAD; None if not derivable.

    On a git-less install (the ZIP path) this simply returns (None, None) and
    the manifest falls back to write counts - the tracker never requires git.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "diff", "--numstat", "--", rel],
            capture_output=True, text=True, timeout=10,
        )
        line = out.stdout.strip().splitlines()
        if not line:
            return (None, None)
        parts = line[0].split("\t")
        if len(parts) >= 2:
            a = None if parts[0] == "-" else int(parts[0])
            d = None if parts[1] == "-" else int(parts[1])
            return (a, d)
    except Exception:
        pass
    return (None, None)


def count_lines(rel: str) -> int | None:
    try:
        p = ROOT / rel
        if p.is_file():
            with p.open("r", encoding="utf-8", errors="replace") as fh:
                return sum(1 for _ in fh)
    except Exception:
        pass
    return None


def aggregate(log_file: Path) -> tuple[str, dict]:
    """Return (sid, {path: {action, writes, last_ts, in_repo}})."""
    sid = log_file.stem
    agg: dict = {}
    try:
        with log_file.open("r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                except Exception:
                    continue
                path = rec.get("path", "")
                if not path:
                    continue
                cur = agg.get(path)
                if cur is None:
                    agg[path] = {
                        "action": rec.get("action", "modify"),
                        "writes": 1,
                        "last_ts": rec.get("ts", ""),
                        "in_repo": rec.get("in_repo", True),
                    }
                else:
                    cur["writes"] += 1
                    cur["last_ts"] = rec.get("ts", cur["last_ts"])
                    # First-seen action wins (create beats later modify).
    except Exception as exc:
        quarantine(
            "scripts/session_changes.py manifest",
            "aggregate change log",
            f"{exc}",
            f"Could not read {log_file}.",
        )
    return sid, agg


def render_manifest(log_file: Path) -> str:
    sid, agg = aggregate(log_file)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    n = len(agg)

    lines = []
    lines.append("# Session changes manifest")
    lines.append("")
    lines.append(f"Rendered: {ts} | Session: `{sid}` | Files changed: {n}")
    lines.append("")
    lines.append(
        "Every file this session wrote to, with the change size and a one-command "
        "recover. Snapshots of the pre-edit version live under "
        "`state/.snapshots/" + sid + "/`."
    )
    lines.append("")

    if n == 0:
        lines.append("No file writes recorded for this session.")
        lines.append("")
        return "\n".join(lines)

    # Sort: created first, then by path.
    def sort_key(item):
        path, meta = item
        return (0 if meta["action"] == "create" else 1, path)

    lines.append("| File | Action | +add | -del | writes | recover |")
    lines.append("|---|---|---|---|---|---|")
    for path, meta in sorted(agg.items(), key=sort_key):
        if not meta.get("in_repo", True):
            adds = dels = None
            recover = "outside the OS folder - not snapshotted"
        elif meta["action"] == "create":
            adds = count_lines(path)
            dels = 0
            recover = "new file (delete to undo)"
        else:
            adds, dels = git_numstat(path)
            recover = f"python scripts/session_changes.py --restore {path} --session {sid}"
        a = "-" if adds is None else str(adds)
        d = "-" if dels is None else str(dels)
        lines.append(f"| `{path}` | {meta['action']} | {a} | {d} | {meta['writes']} | {recover} |")

    lines.append("")
    lines.append("Restore any modified file to its pre-session state:")
    lines.append("")
    lines.append("```")
    lines.append(f"python scripts/session_changes.py --restore <path> --session {sid}")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def prune_old() -> None:
    """Keep only the most recent KEEP_SESSIONS snapshot dirs and logs."""
    try:
        if LOG_DIR.is_dir():
            logs = sorted(LOG_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
            for old in logs[KEEP_SESSIONS:]:
                try:
                    old.unlink()
                except Exception:
                    pass
        if SNAP_DIR.is_dir():
            snaps = sorted(
                [p for p in SNAP_DIR.iterdir() if p.is_dir()],
                key=lambda p: p.stat().st_mtime, reverse=True,
            )
            for old in snaps[KEEP_SESSIONS:]:
                try:
                    shutil.rmtree(old, ignore_errors=True)
                except Exception:
                    pass
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# --manifest : Stop hook                                                        #
# --------------------------------------------------------------------------- #
def cmd_manifest(session_arg: str | None) -> int:
    try:
        # Dual-shell machines run both hook variants; a manifest rendered
        # seconds ago by the sibling variant does not need a second render.
        try:
            if MANIFEST.is_file() and (time.time() - MANIFEST.stat().st_mtime) <= 5:
                return 0
        except Exception:
            pass

        log_file = None
        if session_arg:
            cand = LOG_DIR / f"{short_sid(session_arg)}.jsonl"
            if cand.is_file():
                log_file = cand
        if log_file is None:
            data = read_stdin_json()
            sid = data.get("session_id")
            if sid:
                cand = LOG_DIR / f"{short_sid(str(sid))}.jsonl"
                if cand.is_file():
                    log_file = cand
        if log_file is None:
            log_file = latest_log()

        if log_file is None:
            return 0  # nothing changed, nothing to render

        md = render_manifest(log_file)
        STATE.mkdir(parents=True, exist_ok=True)
        with MANIFEST.open("w", encoding="utf-8") as fh:
            fh.write(md)

        prune_old()

        _, agg = aggregate(log_file)
        n = len(agg)
        if n:
            created = sum(1 for m in agg.values() if m["action"] == "create")
            modified = n - created
            print(
                f"session-changes: {n} file(s) this session "
                f"({created} created, {modified} modified) - see state/session-manifest.md"
            )
    except Exception as exc:
        quarantine(
            "scripts/session_changes.py --manifest",
            "Stop hook manifest render",
            f"{exc}",
            "Session-end manifest could not be rendered.",
        )
    return 0


def cmd_print() -> int:
    log_file = latest_log()
    if log_file is None:
        print("No session changes recorded yet.")
        return 0
    print(render_manifest(log_file))
    return 0


def cmd_restore(relpath: str, session_arg: str | None) -> int:
    try:
        if session_arg:
            sid = short_sid(session_arg)
        else:
            lf = latest_log()
            sid = lf.stem if lf else None
        if not sid:
            print("No session to restore from.")
            return 1
        snap = SNAP_DIR / sid / relpath
        if not snap.is_file():
            print(f"No snapshot for {relpath} in session {sid}. "
                  "It may have been created this session (delete to undo) or is outside the OS folder.")
            return 1
        target = ROOT / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(snap, target)
        print(f"Restored {relpath} from session {sid} snapshot.")
    except Exception as exc:
        print(f"Restore failed: {exc}")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Session changes tracker")
    ap.add_argument("--record", action="store_true", help="PreToolUse: snapshot + log a change")
    ap.add_argument("--manifest", action="store_true", help="Stop: render the session manifest")
    ap.add_argument("--print", action="store_true", dest="do_print", help="Print the latest manifest")
    ap.add_argument("--restore", metavar="PATH", help="Restore a file from its session snapshot")
    ap.add_argument("--session", metavar="SID", help="Session id for manifest/restore")
    args = ap.parse_args()

    if args.record:
        return cmd_record()
    if args.manifest:
        return cmd_manifest(args.session)
    if args.do_print:
        return cmd_print()
    if args.restore:
        return cmd_restore(args.restore, args.session)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
