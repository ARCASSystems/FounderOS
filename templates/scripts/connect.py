#!/usr/bin/env python3
"""Connector helper for Founder OS: set up a tool the user asked to connect.

The `connect` skill drives this. It does the parts a skill cannot do safely on
its own:

  - Write a secret to a gitignored local file ONLY (mechanical enforcement, not
    writer-discipline): set-secret refuses any target that is not on the
    gitignored allowlist AND not actually ignored by git. A token can therefore
    never land in a tracked file through this path, and the always-on secret
    pre-commit guard is the second line of defence if one ever does.
  - Run a real reachability check that the assistant cannot fake: telegram-test
    sends a live message through the Bot API and reports the API result. The
    skill still asks the human "did it arrive?" because a Bot API ok=true does
    not prove the user saw it.
  - Maintain a NO-SECRET status marker (connectors/status.md) the SessionStart
    brief reads, so a skipped or connected tool is visible day to day.

Standard library only. No pip install, no external service beyond the Telegram
Bot API the user opted into. Never echoes a secret value.

Subcommands:
    registry                 Print the connector registry (type + auth class).
    set-secret KEY [VALUE]   Write KEY=VALUE to .env. VALUE may be passed on
                             stdin instead of argv (preferred: keeps it out of
                             shell history and the assistant transcript).
                             --target <file> overrides .env; must stay on the
                             gitignored allowlist.
    telegram-test            Read TELEGRAM_BOT_TOKEN (+ optional
                             TELEGRAM_CHAT_ID) from .env, resolve the chat id via
                             getUpdates if absent, send one test message.
    status set NAME STATE    Record a connector's state in connectors/status.md
                             (no secret value).
    status show              Print connectors/status.md.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Only these filenames may receive a secret. Both are gitignored in the shipped
# .gitignore. set-secret double-checks each target is actually ignored by git
# before writing, so renaming one of these without updating .gitignore fails
# closed instead of leaking.
SECRET_TARGET_ALLOWLIST = {".env", ".mcp.local.json"}

# The connector registry, by auth class. This is the single source the skill
# routes off. No secret lives here - only how each connector authenticates.
REGISTRY: dict[str, dict[str, str]] = {
    # env-key: the OS can walk the steps and store the key locally in .env.
    "telegram": {
        "class": "env-key",
        "secret_keys": "TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID",
        "setup": "Open @BotFather in Telegram, send /newbot, copy the token, then message your new bot once so it has a chat to reply to.",
        "revoke": "Send /revoke to @BotFather, or /deletebot to remove it.",
    },
    "elevenlabs": {
        "class": "env-key",
        "secret_keys": "ELEVENLABS_API_KEY",
        "setup": "Create an API key in your ElevenLabs profile settings.",
        "revoke": "Delete the key in the ElevenLabs dashboard.",
    },
    # mcp-class: account-level, outside this repo. The OS guides, it cannot
    # store the token or run the OAuth.
    "calendar": {
        "class": "guide-only",
        "secret_keys": "",
        "setup": "Add the calendar MCP at the Claude Code account level (see docs/tools-and-mcps.md). Founder OS does not store calendar credentials.",
        "revoke": "Remove the MCP in your Claude Code settings, or revoke access in your calendar provider's security page.",
    },
    "email": {
        "class": "guide-only",
        "secret_keys": "",
        "setup": "Add the email MCP at the Claude Code account level (see docs/tools-and-mcps.md). Founder OS does not store email credentials.",
        "revoke": "Remove the MCP in your Claude Code settings, or revoke access in your email provider's security page.",
    },
    # manual-link: store a reference URL the user pastes. Honest that it is a
    # bookmark, not a live integration.
    "docs": {
        "class": "manual-link",
        "secret_keys": "",
        "setup": "Paste the share link for the doc or folder you want the OS to reference.",
        "revoke": "Change the share setting on the document itself.",
    },
}


# --- gitignore-enforced secret writer ------------------------------------------

def _is_git_ignored(target: Path) -> bool:
    """True only when git itself reports the path as ignored. Fails closed: any
    error (no git, not a repo) returns False so we refuse rather than guess."""
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(target)],
            cwd=str(REPO),
            capture_output=True,
            timeout=10,
        )
    except Exception:
        return False
    return result.returncode == 0


def _parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def _write_env_key(path: Path, key: str, value: str) -> None:
    """Upsert KEY=VALUE in a dotenv-style file, preserving other lines."""
    lines: list[str] = []
    found = False
    if path.exists():
        for raw in path.read_text(encoding="utf-8").splitlines():
            stripped = raw.strip()
            if stripped and not stripped.startswith("#") and stripped.split("=", 1)[0].strip() == key:
                lines.append(f"{key}={value}")
                found = True
            else:
                lines.append(raw)
    if not found:
        lines.append(f"{key}={value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_set_secret(args: list[str]) -> int:
    target_name = ".env"
    rest: list[str] = []
    i = 0
    while i < len(args):
        if args[i] == "--target" and i + 1 < len(args):
            target_name = args[i + 1]
            i += 2
            continue
        rest.append(args[i])
        i += 1

    if not rest:
        print("set-secret needs a KEY (VALUE optional, may come on stdin).", file=sys.stderr)
        return 1
    key = rest[0]
    value = rest[1] if len(rest) > 1 else sys.stdin.read().strip()
    if not value:
        print("No secret value provided (pass as the second arg or on stdin).", file=sys.stderr)
        return 1

    if Path(target_name).name not in SECRET_TARGET_ALLOWLIST:
        print(
            f"REFUSED: {target_name} is not a permitted secret target. "
            f"Allowed: {sorted(SECRET_TARGET_ALLOWLIST)}. Secrets go only to gitignored local files.",
            file=sys.stderr,
        )
        return 2
    target = (REPO / target_name).resolve()
    if not _is_git_ignored(target):
        print(
            f"REFUSED: {target_name} is not gitignored. Writing a secret there would risk a commit. "
            "Add it to .gitignore first, or use .env.",
            file=sys.stderr,
        )
        return 2

    _write_env_key(target, key, value)
    print(f"Stored {key} in {target_name} (value hidden). {target_name} is gitignored - it will not be committed.")
    return 0


# --- Telegram reachability -----------------------------------------------------

def _api(token: str, method: str, payload: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_telegram_test() -> int:
    env_path = REPO / ".env"
    env = _parse_env(env_path)
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print(
            "No TELEGRAM_BOT_TOKEN in .env. Run set-secret TELEGRAM_BOT_TOKEN first "
            "(get the token from @BotFather).",
            file=sys.stderr,
        )
        return 1

    chat_id = env.get("TELEGRAM_CHAT_ID", "").strip()
    try:
        if not chat_id:
            updates = _api(token, "getUpdates")
            if not updates.get("ok"):
                print("Bot API rejected the token (getUpdates not ok). Check the token from @BotFather.", file=sys.stderr)
                return 1
            results = updates.get("result", [])
            for upd in reversed(results):
                msg = upd.get("message") or upd.get("edited_message") or {}
                cid = (msg.get("chat") or {}).get("id")
                if cid is not None:
                    chat_id = str(cid)
                    break
            if not chat_id:
                print(
                    "Token works but no chat found. Open your bot in Telegram and send it any message, "
                    "then run telegram-test again.",
                    file=sys.stderr,
                )
                return 1
            _write_env_key(env_path, "TELEGRAM_CHAT_ID", chat_id)

        sent = _api(
            token,
            "sendMessage",
            {"chat_id": chat_id, "text": "Founder OS connector test. If you can read this, Telegram is wired."},
        )
    except urllib.error.URLError as exc:
        print(f"Network error reaching the Telegram API: {exc}. Check your connection and retry.", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - report, never crash the skill
        print(f"Unexpected error during the Telegram test: {exc}", file=sys.stderr)
        return 1

    if sent.get("ok"):
        print(
            "Test message sent (Bot API ok=true). The API accepting it does NOT prove you saw it - "
            "check Telegram now and confirm the message arrived."
        )
        return 0
    print(f"Bot API did not accept the message: {sent.get('description', 'unknown error')}", file=sys.stderr)
    return 1


# --- status marker (no secrets) ------------------------------------------------

STATUS_PATH = REPO / "connectors" / "status.md"
STATUS_HEADER = "# Connector status\n\nNo secrets here. Secrets live only in gitignored .env / .mcp.local.json.\n"


def _read_status() -> dict[str, str]:
    states: dict[str, str] = {}
    if not STATUS_PATH.exists():
        return states
    for line in STATUS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- "):
            body = line[2:]
            name, _, state = body.partition(":")
            if state:
                states[name.strip()] = state.strip()
    return states


def cmd_status(args: list[str]) -> int:
    if not args:
        print("status needs 'set NAME STATE' or 'show'.", file=sys.stderr)
        return 1
    if args[0] == "show":
        if STATUS_PATH.exists():
            sys.stdout.write(STATUS_PATH.read_text(encoding="utf-8"))
        else:
            print("No connectors configured yet.")
        return 0
    if args[0] == "set" and len(args) >= 3:
        name = args[1]
        state = " ".join(args[2:])
        states = _read_status()
        states[name] = state
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        body = STATUS_HEADER + "\n" + "".join(f"- {n}: {s}\n" for n, s in sorted(states.items()))
        STATUS_PATH.write_text(body, encoding="utf-8")
        print(f"Recorded {name}: {state} in connectors/status.md")
        return 0
    print("status usage: status set NAME STATE | status show", file=sys.stderr)
    return 1


def cmd_registry() -> int:
    for name, info in REGISTRY.items():
        print(f"{name} [{info['class']}]")
        if info["secret_keys"]:
            print(f"  keys: {info['secret_keys']}")
        print(f"  setup: {info['setup']}")
        print(f"  revoke: {info['revoke']}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "registry":
        return cmd_registry()
    if cmd == "set-secret":
        return cmd_set_secret(rest)
    if cmd == "telegram-test":
        return cmd_telegram_test()
    if cmd == "status":
        return cmd_status(rest)
    print(f"Unknown subcommand: {cmd}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
