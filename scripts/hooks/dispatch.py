#!/usr/bin/env python3
"""Founder OS hook dispatcher - one cross-platform entry per hook event.

Every Claude Code hook event routes through this single Python file instead of a
pair of registered .sh/.ps1 scripts. Two problems this fixes, both found in the
v1.41.2 review:

1. Interpreter-missing noise on single-shell machines. The old settings.json
   registered BOTH a bash and a PowerShell command for every event, so a
   Windows box without bash (or a Linux box without PowerShell) printed an
   interpreter-not-found error on every fire even though the correct-platform
   script ran fine. Python is already a hard prerequisite, so a Python
   dispatcher needs no shell at all: there is nothing to be missing.

2. Unguaranteed Stop ordering. Claude Code runs the hooks in an event array,
   but does not promise the order. Three Stop handlers are order-dependent: the
   revenue check and the change manifest must both read the working tree BEFORE
   the autosave commits it. This dispatcher runs Stop work in a fixed sequence:
   revenue-check -> changes-manifest -> autosave.

Design rules (they are why this file exists):
- Pure stdlib. No third-party imports, no network, no API key.
- Never blocks or slows a tool call or session event. Every handler is wrapped
  so a failure is logged to system/quarantine.md (visible) and the dispatcher
  still exits 0. A hook that crashes the session is worse than a hook that
  quietly failed - but a hook that fails SILENTLY is worst of all, so failures
  are made visible, not swallowed.
- ASCII-only stdout. Hook output must survive any Windows codepage.
- Delegates to the existing Python helpers where they already own the work
  (session_changes.py, session_start_brief.py, user-prompt-capture.py,
  caveman_git.py, memory-diff.py); the shell-only logic (revenue check,
  autosave guard, liveness, precompact prompt, observation append) is ported
  here so no .sh/.ps1 pair remains.

Usage: python scripts/hooks/dispatch.py <EventName>
  where <EventName> is one of the six wired events. settings.json passes the
  literal event name as the argument, one dispatcher entry per event.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path


# --------------------------------------------------------------------------- #
# Repo + interpreter resolution                                                 #
# --------------------------------------------------------------------------- #
def repo_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        try:
            return Path(env).resolve()
        except Exception:
            pass
    # scripts/hooks/dispatch.py -> repo root is two parents up.
    return Path(__file__).resolve().parents[2]


ROOT = repo_root()
QUARANTINE = ROOT / "system" / "quarantine.md"


def quarantine(source: str, trigger: str, err: str, context: str) -> None:
    """Make a handler failure visible instead of swallowing it. Never raises."""
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
        pass


def read_stdin_bytes() -> bytes:
    """Read the hook JSON payload once, as bytes, so it can be fed to any number
    of delegated sub-processes. Empty bytes when there is no stdin (or a TTY)."""
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return b""
        return sys.stdin.buffer.read() or b""
    except Exception:
        return b""


def parse_stdin(raw: bytes) -> dict:
    try:
        if not raw:
            return {}
        data = json.loads(raw.decode("utf-8", errors="replace"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def child_env() -> dict:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"  # survive Windows codepages in delegated helpers
    env.setdefault("CLAUDE_PROJECT_DIR", str(ROOT))
    return env


def run_helper(script_rel: str, args: list[str], stdin_bytes: bytes) -> None:
    """Run a bundled Python helper, feeding it the hook stdin, letting its
    stdout flow straight through to Claude Code. Missing helper = quiet skip
    (matches the old shell hooks, which tested for the file first)."""
    script = ROOT / script_rel
    if not script.is_file():
        return
    try:
        # Flush our own buffered prints first so the child's inherited stdout
        # cannot jump ahead of output this dispatcher already produced. Without
        # this, a Stop revenue warning (buffered) would print AFTER the change
        # manifest summary (written straight to the fd by the child).
        sys.stdout.flush()
        subprocess.run(
            [sys.executable, str(script), *args],
            input=stdin_bytes,
            env=child_env(),
            cwd=str(ROOT),
        )
    except Exception as exc:
        quarantine(
            f"scripts/hooks/dispatch.py -> {script_rel}",
            "delegated helper",
            f"{exc}",
            "Dispatcher could not run the helper; the session was not blocked.",
        )


def git(root: Path, *args: str) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout
    except Exception:
        return ""


def short_sid(session_id: str) -> str:
    """Match scripts/session_changes.py short_sid so the same session id resolves
    to the same .session-changes/<sid>.jsonl file."""
    sid = (session_id or "nosession").strip()
    safe = "".join(c for c in sid if c.isalnum() or c in "-_")
    return (safe or "nosession")[:16]


# --------------------------------------------------------------------------- #
# SessionStart : brief + liveness                                               #
# --------------------------------------------------------------------------- #
def h_session_start(stdin_bytes: bytes) -> None:
    today = date.today().isoformat()
    # --full renders the whole brief; without it the helper falls back to the
    # legacy @@SECTION payload for a retained pre-dispatcher shell hook.
    run_helper(".claude/hooks/session_start_brief.py", [str(ROOT), today, "--full"], b"")
    liveness()


def liveness() -> None:
    """One line about how long since /since-last-session. Read-only on the
    marker; never writes it. Ported from session-start-liveness.sh."""
    if not (ROOT / "core" / "identity.md").is_file():
        return
    marker = ROOT / "brain" / ".last-session"
    if not marker.is_file():
        print("No prior synthesis marker found. Run /since-last-session to initialize.")
        return
    try:
        raw = marker.read_text(encoding="utf-8").strip()
    except Exception:
        return
    malformed = "Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair."
    if not raw:
        print(malformed)
        return
    try:
        m = datetime.fromisoformat(raw)
    except ValueError:
        print(malformed)
        return
    if m.tzinfo is None:
        print(malformed)
        return
    now = datetime.now(timezone.utc)
    elapsed = (now - m).total_seconds()
    if elapsed < 0:
        print("Synthesis marker is in the future; ignoring. Run /since-last-session if you want to repair it.")
        return
    if elapsed < 3600:
        print("Less than an hour since you last ran /since-last-session.")
        return
    hours = int(elapsed // 3600)
    print(
        f"{hours} hours since you last ran /since-last-session. "
        "Run /since-last-session for the delta, or /strategic-read for a full state-of-OS report."
    )


# --------------------------------------------------------------------------- #
# PreToolUse : snapshot-before-write                                            #
# --------------------------------------------------------------------------- #
def h_pre_tool_use(stdin_bytes: bytes) -> None:
    run_helper("scripts/session_changes.py", ["--record"], stdin_bytes)


# --------------------------------------------------------------------------- #
# UserPromptSubmit : capture classifier                                         #
# --------------------------------------------------------------------------- #
def h_user_prompt_submit(stdin_bytes: bytes) -> None:
    run_helper("scripts/user-prompt-capture.py", [], stdin_bytes)


# --------------------------------------------------------------------------- #
# PreCompact : save-before-forget prompt injection                             #
# --------------------------------------------------------------------------- #
PRECOMPACT_TEXT = (
    "[founder-os pre-compact] Save before you forget. This session is being compacted.\n"
    "1. Preserve in the summary, verbatim where possible: every decision made, commitment given or received, "
    "client/prospect status change, deadline, number, and captured fact from this session that has NOT yet been "
    "written to a brain file.\n"
    "2. Immediately after compaction, before continuing the task: write those items to their homes - brain/log.md "
    "(dated entry), brain/flags.md (open loops), context/clients.md (status changes), brain/decisions-parked.md "
    "(deferred calls). Continuity lives in the files, not in the summary.\n"
    "3. If nothing in this session is unwritten, say nothing and carry on."
)


def h_pre_compact(stdin_bytes: bytes) -> None:
    if not (ROOT / "core" / "identity.md").is_file():
        return
    print(PRECOMPACT_TEXT)


# --------------------------------------------------------------------------- #
# PostToolUse : opt-in observation log                                          #
# --------------------------------------------------------------------------- #
def _clean(s: str, limit: int) -> str:
    s = re.sub(r"[\x00-\x1f\x7f]", " ", s or "")
    return s[:limit]


def h_post_tool_use(stdin_bytes: bytes) -> None:
    if os.environ.get("FOUNDER_OS_OBSERVATIONS") != "1":
        return
    data = parse_stdin(stdin_bytes)
    tool = str(data.get("tool_name", "") or "")
    session = str(data.get("session_id", "") or "")
    ti = data.get("tool_input") or {}
    if not isinstance(ti, dict):
        ti = {}

    def g(key: str) -> str:
        v = ti.get(key, "")
        return "" if v is None else str(v)

    file_path = g("file_path")
    if tool == "Read":
        intent = f"read {file_path}"
    elif tool in ("Edit", "Write"):
        snippet = g("new_string") or g("content")
        intent = f"edit {file_path} - {_clean(snippet, 80)}"
    elif tool == "Bash":
        intent = f"bash - {_clean(g('command'), 80)}"
    elif tool == "Grep":
        intent = f"grep {g('pattern')} in {g('path')}"
    elif tool == "Glob":
        intent = f"glob {g('pattern')}"
    elif tool == "":
        intent = "unknown"
    else:
        intent = tool
    intent = _clean(intent, 120)

    try:
        obs_dir = ROOT / "brain" / "observations"
        obs_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now().astimezone()
        ts = now.replace(microsecond=0).isoformat()
        obs_file = obs_dir / f"{now.date().isoformat()}.jsonl"
        record = {
            "ts": ts,
            "tool": tool,
            "file": file_path,
            "intent": intent,
            "session": session,
        }
        with obs_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")
    except Exception as exc:
        quarantine(
            "scripts/hooks/dispatch.py PostToolUse",
            "observation append",
            f"{exc}",
            "Opt-in observation log could not be written; tool call was not affected.",
        )


# --------------------------------------------------------------------------- #
# Stop : revenue-check -> changes-manifest -> autosave (deterministic order)     #
# --------------------------------------------------------------------------- #
OUTREACH_RE = re.compile(
    r"\b(sent|messaged|called|DM'?d|emailed|pitched|reached\s+out|spoke\s+with|"
    r"outreach|ping(ed)?|texted|whatsapp(ed)?)\b",
    re.IGNORECASE,
)
ACTED_S_RE = re.compile(r"#acted\s+\[S\]")
PIPELINE_PATHS = {"context/clients.md", "context/leads.md"}


def _session_change_paths(stdin_bytes: bytes) -> set[str] | None:
    """Repo-relative paths written this session, read from
    state/.session-changes/<sid>.jsonl (written by session_changes.py --record).
    None when no session log is found - the caller then stays silent, matching
    the old 'only nag when something changed this session' behaviour.

    This replaces the old `git status --porcelain` detection, which was silently
    broken: brain/log.md and context/clients.md are gitignored on a fresh
    install, so status was always empty and the check never fired (finding 6)."""
    log_dir = ROOT / "state" / ".session-changes"
    if not log_dir.is_dir():
        return None
    data = parse_stdin(stdin_bytes)
    sid = data.get("session_id")
    log_file = None
    if sid:
        cand = log_dir / f"{short_sid(str(sid))}.jsonl"
        if cand.is_file():
            log_file = cand
    if log_file is None:
        logs = sorted(log_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        log_file = logs[0] if logs else None
    if log_file is None:
        return None
    paths: set[str] = set()
    try:
        with log_file.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                p = rec.get("path")
                if p:
                    paths.add(p)
    except Exception:
        return None
    return paths


def revenue_check(stdin_bytes: bytes) -> None:
    log = ROOT / "brain" / "log.md"
    clients = ROOT / "context" / "clients.md"
    if not log.is_file() or not clients.is_file():
        return

    written = _session_change_paths(stdin_bytes)
    if written is None:
        return  # no session-changes record -> nothing changed this session to check
    if "brain/log.md" not in written:
        return  # the log was not touched this session; nothing to nag about

    try:
        with log.open("r", encoding="utf-8", errors="replace") as fh:
            recent = [next(fh, "") for _ in range(120)]
    except Exception:
        return

    outreach = [ln.rstrip("\n") for ln in recent if OUTREACH_RE.search(ln)][:5]
    acted = [ln.rstrip("\n") for ln in recent if ACTED_S_RE.search(ln)][:3]
    if not outreach and not acted:
        return  # no outreach signal in recent log

    if PIPELINE_PATHS & written:
        return  # a lead/client row WAS updated this session - loop is closed

    print("")
    print("=== REVENUE LOOP CHECK ===")
    print("Outreach signals detected in recent brain/log.md entries but context/clients.md")
    print("has NOT been modified in the current session.")
    print("")
    print("Every outreach action should update context/clients.md AND log to brain/log.md")
    print("with #acted [S] in the same session. This keeps your pipeline state honest.")
    print("")
    print("Sample signals matched:")
    for ln in outreach[:3]:
        print(f"  {ln}")
    print("")
    print("Action before closing: update context/clients.md with the outreach touches,")
    print("OR add a brain/log.md note explaining why no client row was needed.")
    print("")
    print("=== END CHECK ===")
    print("")


def changes_manifest(stdin_bytes: bytes) -> None:
    # session_changes.py --manifest computes numstat against HEAD, so it MUST run
    # before autosave commits the tree. The dispatcher order guarantees that.
    run_helper("scripts/session_changes.py", ["--manifest"], stdin_bytes)


def _guard_active() -> bool:
    hooks_path = git(ROOT, "config", "core.hooksPath").strip()
    patterns = ROOT / "scripts" / "private-name-patterns.txt"
    if hooks_path != ".githooks" or not patterns.is_file():
        return False
    try:
        with patterns.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if re.match(r"^\s*[^#\s]", line):
                    return True
    except Exception:
        return False
    return False


def autosave() -> None:
    if not (ROOT / "core" / "identity.md").is_file():
        return
    if not (ROOT / "scripts" / "caveman_git.py").is_file():
        return
    if not git(ROOT, "status", "--porcelain").strip():
        return  # nothing to save

    if _guard_active():
        print("")
        print("=== AUTO-SAVE ===")
        try:
            out = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "caveman_git.py"), "save"],
                capture_output=True, text=True, env=child_env(), cwd=str(ROOT),
            )
            if out.stdout:
                sys.stdout.write(out.stdout)
            if out.stderr:
                sys.stdout.write(out.stderr)
        except Exception as exc:
            quarantine(
                "scripts/hooks/dispatch.py autosave",
                "caveman_git save",
                f"{exc}",
                "Session-close autosave could not run; no version was recorded this session.",
            )
        print('(Local only. Say "undo to ..." to roll back, "what changed" to see versions.)')
        print("=== END AUTO-SAVE ===")
        print("")
    else:
        print("")
        print("=== AUTO-SAVE PAUSED ===")
        print("You have unsaved changes this session, but auto-save is paused because the")
        print("privacy name guard is not active yet (no patterns in")
        print("scripts/private-name-patterns.txt). The OS will not auto-commit content that")
        print("has not been name-scanned.")
        print("")
        print('Say "save my work" to save manually now, or add your name to')
        print("scripts/private-name-patterns.txt (then run scripts/install-git-hooks.sh) to")
        print("turn on auto-save.")
        print("=== END AUTO-SAVE ===")
        print("")


def h_stop(stdin_bytes: bytes) -> None:
    # Deterministic order: both readers run before the writer commits the tree.
    _wrap("Stop:revenue-check", revenue_check, stdin_bytes)
    _wrap("Stop:changes-manifest", changes_manifest, stdin_bytes)
    _wrap("Stop:autosave", lambda _b: autosave(), stdin_bytes)


# --------------------------------------------------------------------------- #
# Dispatch table + entrypoint                                                   #
# --------------------------------------------------------------------------- #
EVENTS = {
    "SessionStart": h_session_start,
    "PreToolUse": h_pre_tool_use,
    "UserPromptSubmit": h_user_prompt_submit,
    "PreCompact": h_pre_compact,
    "Stop": h_stop,
    "PostToolUse": h_post_tool_use,
}


def _wrap(label: str, fn, stdin_bytes: bytes) -> None:
    """Run one handler so a failure is visible but never blocks the session."""
    try:
        fn(stdin_bytes)
    except Exception as exc:
        quarantine(
            f"scripts/hooks/dispatch.py ({label})",
            "hook handler",
            f"{exc}",
            "A hook handler raised; the dispatcher continued and exited 0.",
        )


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    event = sys.argv[1]
    handler = EVENTS.get(event)
    if handler is None:
        return 0
    # Line-buffer our stdout so native prints and delegated-child output stay in
    # true chronological order (the Stop sequence prints from both).
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    stdin_bytes = read_stdin_bytes()
    if event == "Stop":
        # h_stop wraps each sub-handler itself for per-step isolation.
        h_stop(stdin_bytes)
    else:
        _wrap(event, handler, stdin_bytes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
