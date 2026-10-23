#!/usr/bin/env python3
"""Connector helper for Founder OS: set up a tool the user asked to connect.

The `connect` skill drives this. It does the parts a skill cannot do safely on
its own:

  - Write a secret to a gitignored local file ONLY (mechanical enforcement, not
    writer-discipline): set-secret refuses any target that is not on the
    allowlist below and not proven ignored. Where a git repository exists, git
    itself is asked. Where none does - the ZIP install, which is advertised as
    needing no git - the shipped .gitignore is read directly and the name must
    match a line of it exactly. A token therefore never lands in a tracked file
    through this path, and the always-on secret pre-commit guard is the second
    line of defence if one ever does.
  - Run a real reachability check that the assistant cannot fake: telegram-test
    sends a live message through the Bot API and reports the API result. The
    skill still asks the human "did it arrive?" because a Bot API ok=true does
    not prove the user saw it.
  - Maintain a NO-SECRET status marker (connectors/status.md) the SessionStart
    brief reads, so a skipped or connected tool is visible day to day.

Standard library only. No pip install, no external service beyond the Telegram
Bot API the user opted into. Never echoes a secret value.

A real key never travels through a command or the chat. The founder types it
into .env with their own text editor: add-key makes the line with a
placeholder, and key-status proves it was filled in without showing it.

Subcommands:
    registry                 Print the connector registry (type + auth class).
    add-key NAME             Add a placeholder line (KEY=paste-your-key-here) to
                             .env for each key the connector NAME needs (or for
                             the single KEY named, e.g. GEMINI_API_KEY2). A key
                             already in the file is left exactly as it is, so
                             running this again never undoes a working key.
                             --target <file> overrides .env; must stay on the
                             gitignored allowlist.
    key-status NAME          Say whether each key of NAME is filled in, still the
                             placeholder, or missing. Never prints a value.
                             Exits 0 only when every required key is filled in.
    set-secret KEY VALUE     Write KEY=VALUE to .env. For values that are not
                             secrets (a chat id) and for scripts. Never use it
                             for a real key: that is add-key plus the founder's
                             own editor.
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
import re
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

# The value add-key writes. It is not a secret, so it may pass through a
# command and the chat. "paste-your-token-here" is the placeholder the 1.56.0
# connect skill wrote for Telegram, still read as a placeholder so an install
# that ran it is not told a key is filled in when it is not.
PLACEHOLDER = "paste-your-key-here"
PLACEHOLDERS = {PLACEHOLDER, "paste-your-token-here"}

# The connector registry, by auth class. This is the single source the skill
# routes off. No secret lives here - only how each connector authenticates.
REGISTRY: dict[str, dict[str, str]] = {
    # env-key: the OS can walk the steps and store the key locally in .env.
    # env_keys: the lines add-key writes and key-status checks. Telegram's chat
    # id is not a secret and telegram-test finds it by itself.
    "telegram": {
        "class": "env-key",
        "env_keys": "TELEGRAM_BOT_TOKEN",
        "secret_keys": "TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID",
        "setup": "Open @BotFather in Telegram, send /newbot, copy the token, then message your new bot once so it has a chat to reply to.",
        "revoke": "Send /revoke to @BotFather, or /deletebot to remove it.",
    },
    "elevenlabs": {
        "class": "env-key",
        "env_keys": "ELEVENLABS_API_KEY",
        "secret_keys": "ELEVENLABS_API_KEY",
        "setup": "Create an API key in your ElevenLabs profile settings.",
        "revoke": "Delete the key in the ElevenLabs dashboard.",
    },
    "gemini": {
        "class": "env-key",
        "env_keys": "GEMINI_API_KEY",
        "secret_keys": "GEMINI_API_KEY (add GEMINI_API_KEY2 for free-tier headroom)",
        "setup": "Tier-1 realtime voice (add-voice --realtime) uses this. Create a FREE key at https://aistudio.google.com/apikey. A free key carries a free daily quota on Flash models; heavy realtime use can move you onto paid per-token rates. Read skills/add-voice/references/voice-model-disclaimer.md before you commit. A second key (GEMINI_API_KEY2) is optional headroom the realtime front rotates to if the first hits its quota.",
        "revoke": "Delete or regenerate the key in Google AI Studio (aistudio.google.com/apikey).",
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

def _git_repo_present() -> bool:
    """True only when git runs AND the OS folder is inside a repository.

    Anything else is a plain False, not an error. A folder with no git is the
    normal, advertised state of a ZIP install, so the answer routes the proof
    below - it never refuses on its own."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=str(REPO),
            capture_output=True,
            timeout=10,
        )
    except Exception:
        return False
    return result.returncode == 0


def _is_git_ignored(target: Path) -> bool:
    """True only when git itself reports the path as ignored. Call only after
    _git_repo_present(): with no repository this can answer nothing but False,
    which is the wrong answer rather than the safe one."""
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


def _gitignore_lists(name: str) -> bool:
    """True when the shipped .gitignore names this file on a line of its own.

    The no-repository proof. There is no git to ask, and asking anyway was the
    bug: check-ignore raised, the exception read as "not ignored", and every
    connector was refused with a reason that was false. Reading the rule file
    is the honest substitute.

    Exact match only (`.env` or `/.env`), no glob interpretation. That is
    deliberately narrow: it can confirm nothing beyond the two literal names on
    SECRET_TARGET_ALLOWLIST, both of which ship as their own lines in the
    developer .gitignore and in templates/operator.gitignore. A pattern this
    cannot match is a pattern we are not certain enough about to trust with a
    token."""
    try:
        lines = (REPO / ".gitignore").read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return False
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        if line in (name, f"/{name}"):
            return True
    return False


def _refuse_if_shared(path: Path) -> str | None:
    """Refuse a target that is the same file as something else on disk.

    resolve() catches a symlink or a junction because both are paths that point
    elsewhere. A hard link is not a path - it is a second name for the same file
    object, so it resolves inside the folder and passes every containment check
    while a write through it lands in a file the founder never named. Returns
    the refusal text, or None when the target is safe to write.

    A file with one name is the only shape a secret target should ever have."""
    try:
        links = os.stat(path).st_nlink
    except OSError:
        return None    # not there yet, or unreadable - the write path handles it
    if links > 1:
        return (
            f"REFUSED: {path.name} is the same file as something else on this computer, "
            "so a secret written here would also be written there. Delete it and run this "
            "again to make a fresh one."
        )
    return None


def _create_user_only(path: Path) -> None:
    """Create the secret file readable by this user only, where the platform
    supports it. POSIX honours the mode; Windows ignores it and inherits the
    folder's ACL, so this is best effort and never reported as more than that.
    Existing files are left as they are - their permissions are the founder's."""
    if path.exists():
        return
    try:
        os.close(os.open(str(path), os.O_CREAT | os.O_WRONLY, 0o600))
    except Exception:
        pass


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


def _split_target(args: list[str]) -> tuple[str, list[str]]:
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
    return target_name, rest


def _secret_target(target_name: str) -> tuple[Path | None, str]:
    """Prove a file may hold a secret. Returns (path, confirmation line), or
    (None, "") after printing the refusal. Every writer goes through this."""
    name = Path(target_name).name

    # A target is a bare filename in the OS root, never a path. Reject anything
    # carrying folder parts outright instead of quietly using its last segment:
    # "../elsewhere/.env" would otherwise clear the allowlist on its basename,
    # and silently writing to .env instead of what was asked for is the kind of
    # false reassurance this whole path exists to avoid.
    if name != target_name:
        print(
            f"REFUSED: {target_name} names a folder path. A secret target is a filename in your "
            f"Founder OS folder. Allowed: {sorted(SECRET_TARGET_ALLOWLIST)}.",
            file=sys.stderr,
        )
        return None, ""

    if name not in SECRET_TARGET_ALLOWLIST:
        print(
            f"REFUSED: {target_name} is not a permitted secret target. "
            f"Allowed: {sorted(SECRET_TARGET_ALLOWLIST)}. Secrets go only to gitignored local files.",
            file=sys.stderr,
        )
        return None, ""

    # Belt and braces: Path().name splits on the running platform's separators,
    # so a Windows-shaped path handed to a POSIX interpreter survives the check
    # above. Prove containment against the resolved root as well.
    root = REPO.resolve()
    target = (root / name).resolve()
    if target.parent != root:
        print(
            f"REFUSED: {target_name} resolves outside your Founder OS folder. "
            "A secret is only ever written inside it.",
            file=sys.stderr,
        )
        return None, ""

    if _git_repo_present():
        proven = _is_git_ignored(target)
        refusal = (
            f"REFUSED: git is not ignoring {name} in this folder, so a secret written there could end up "
            f"in a commit. Add {name} to .gitignore, then run this again."
        )
        confirmation = f"Git is set to ignore {name}, so it will not be committed."
    else:
        proven = _gitignore_lists(name)
        refusal = (
            f"REFUSED: {name} is not on the ignore list this install ships with, so there is nothing "
            "proving a secret stays private there. Re-install Founder OS to restore the list, then run this again."
        )
        confirmation = (
            f"This install has no version history yet, and {name} is on the ignore list Founder OS ships with, "
            "so it stays out of history when you turn it on."
        )

    if not proven:
        print(refusal, file=sys.stderr)
        return None, ""

    shared = _refuse_if_shared(target)
    if shared:
        print(shared, file=sys.stderr)
        return None, ""

    return target, confirmation


# How to get a key in without the chat. Every message that tells the founder
# what to do next points here, never at a command argument.
NO_KEY_IN_CHAT = (
    "A key is never typed into the chat or a command. Say 'connect <tool>' "
    "(for example 'connect gemini') and Founder OS adds a line to your .env "
    "file for you to fill in yourself, in Notepad or TextEdit."
)


def cmd_set_secret(args: list[str]) -> int:
    target_name, rest = _split_target(args)
    if len(rest) < 2 or not rest[1].strip():
        print(f"set-secret needs a KEY and a VALUE. {NO_KEY_IN_CHAT}", file=sys.stderr)
        return 1
    key, value = rest[0], rest[1].strip()

    target, confirmation = _secret_target(target_name)
    if target is None:
        return 2

    # A placeholder never replaces a value already in the file. Running the
    # 1.56.0 connect steps a second time wrote the placeholder over a working
    # token; this keeps that from ever happening again, whoever calls it.
    if value in PLACEHOLDERS and key in _parse_env(target):
        print(f"{key} is already in {target.name}. Left it as it is.")
        return 0

    _create_user_only(target)
    _write_env_key(target, key, value)
    print(f"Stored {key} in {target.name} (value hidden). {confirmation}")
    return 0


def _is_placeholder(value: str) -> bool:
    v = value.strip().strip('"').strip("'")
    return v in PLACEHOLDERS or v.lower().startswith("your")


def _keys_for(name: str) -> tuple[list[str], str] | None:
    """The .env lines a connector needs, or the one KEY named. None when the
    name is neither an env-key connector nor a key name."""
    info = REGISTRY.get(name.lower())
    if info is not None:
        if info["class"] != "env-key":
            return None
        return [k.strip() for k in info.get("env_keys", "").split(",") if k.strip()], name.lower()
    if re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
        return [name], name
    return None


def _env_key_names() -> str:
    return ", ".join(n for n, i in REGISTRY.items() if i["class"] == "env-key")


def cmd_add_key(args: list[str]) -> int:
    target_name, rest = _split_target(args)
    if len(rest) != 1:
        print(f"add-key needs one name: a tool ({_env_key_names()}) or a key name like GEMINI_API_KEY2.",
              file=sys.stderr)
        return 1
    found = _keys_for(rest[0])
    if found is None:
        print(f"{rest[0]} is not a tool that keeps a key in .env. Tools that do: {_env_key_names()}.",
              file=sys.stderr)
        return 1
    keys, _ = found

    target, confirmation = _secret_target(target_name)
    if target is None:
        return 2

    present = _parse_env(target)
    for key in keys:
        if key not in present:
            _create_user_only(target)
            _write_env_key(target, key, PLACEHOLDER)
            print(f"Added the line {key}={PLACEHOLDER} to {target.name}. {confirmation}")
        elif _is_placeholder(present[key]):
            print(f"{key} is in {target.name} but still holds the placeholder. Left it for you to fill in.")
        else:
            print(f"{key} is already filled in, in {target.name}. Left it as it is (value hidden).")
    return 0


def cmd_key_status(args: list[str]) -> int:
    target_name, rest = _split_target(args)
    found = _keys_for(rest[0]) if len(rest) == 1 else None
    if found is None:
        print(f"key-status needs one tool ({_env_key_names()}) or a key name.", file=sys.stderr)
        return 1
    keys, _ = found
    name = Path(target_name).name
    if name not in SECRET_TARGET_ALLOWLIST or name != target_name:
        print(f"REFUSED: key-status reads only {sorted(SECRET_TARGET_ALLOWLIST)}.", file=sys.stderr)
        return 2
    present = _parse_env(REPO / name)
    all_filled = True
    for key in keys:
        if key not in present or not present[key].strip():
            print(f"{key}: missing from {name}. Say 'connect <tool>' to add the line.")
            all_filled = False
        elif _is_placeholder(present[key]):
            print(f"{key}: still the placeholder. Open {name}, replace {PLACEHOLDER} with your key, save.")
            all_filled = False
        else:
            print(f"{key}: filled in (value hidden).")
    return 0 if all_filled else 1


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
            "No TELEGRAM_BOT_TOKEN in .env. Say 'connect telegram' to add the line, then type "
            "the token from @BotFather into .env yourself.",
            file=sys.stderr,
        )
        return 1
    if _is_placeholder(token):
        print(
            "The TELEGRAM_BOT_TOKEN line in .env still holds the placeholder. Open .env, replace "
            f"{PLACEHOLDER} with the token from @BotFather, save, and run the test again.",
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
    except urllib.error.HTTPError as exc:
        # HTTPError is a URLError, so it must be caught first. Telegram answers
        # a wrong token with 401 (404 when the token is not even token-shaped)
        # and says why in a JSON body. That is a token problem, not a network one.
        try:
            detail = json.loads(exc.read().decode("utf-8", "replace")).get("description", "")
        except Exception:  # noqa: BLE001 - the body is a bonus, the code is enough
            detail = ""
        detail = detail or str(exc.reason or "")
        if exc.code in (401, 404):
            print(
                f"Telegram did not accept the token ({exc.code}: {detail}). Open .env and check the "
                "TELEGRAM_BOT_TOKEN line holds the whole token from @BotFather and nothing else.",
                file=sys.stderr,
            )
        else:
            print(f"Telegram answered with an error ({exc.code}: {detail}).", file=sys.stderr)
        return 1
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
    if cmd == "add-key":
        return cmd_add_key(rest)
    if cmd == "key-status":
        return cmd_key_status(rest)
    if cmd == "telegram-test":
        return cmd_telegram_test()
    if cmd == "status":
        return cmd_status(rest)
    print(f"Unknown subcommand: {cmd}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
