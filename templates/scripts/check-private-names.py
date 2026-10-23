#!/usr/bin/env python3
"""Pre-commit / CI guard: scans content for private-name leaks, em/en dashes,
and AI-attribution trailers. One scanner, three front-ends so the local hooks
and CI cannot drift apart.

Modes:
    --staged              Scan `git diff --cached` added lines (L2 pre-commit hook).
    --message <path>      Scan a commit-message file (L2 commit-msg hook).
    --range <BASE..HEAD>  Scan every commit in a range (L3 CI). Exit 1 on any
                          violation so the check fails the build.
    --baseline            Scan every tracked file's full content for em/en dashes
                          (L3 CI). The diff and range scans only see ADDED lines, so
                          a dash that predates the range slips through; this full-tree
                          gate asserts the whole repo stays dash-clean and can never
                          silently regress. Dash check-set only: private-name, secret,
                          attribution, and remote-safety keep their own modes.

Check-sets:
    private-name  Regexes from scripts/private-name-patterns.txt (one per line;
                  # comments and blanks ignored). Operator-local and gitignored:
                  a contributor without the file (or with an empty one) gets NO
                  name check, only voice + attribution. Override the path with
                  PRIVATE_NAME_PATTERNS_FILE (CI loads it from the
                  *_PRIVATE_AUDIT_PATTERNS secret this way).
    emdash        Em-dash (U+2014) / en-dash (U+2013). Flagged in the commit
                  message AND in added product lines: this is a public product
                  repo whose house voice bans them. (The private OS scanner
                  exempts diff bodies because those carry captured transcripts;
                  a public product repo does not, so we scan them.) Escape
                  hatch: ALLOW_EMDASH=1. Product repo only: in an installed OS
                  (core/identity.md tracked) --staged and --message skip it, so
                  a founder who pastes a client email can still save. The same
                  goes for the line-ending and entry-form checks, which are the
                  product's own house rules, not rules for a founder's data.
    attribution   Co-Authored-By: Claude / Generated with Claude Code trailers.
                  Checked on every line, every mode. Line-start anchored so rule
                  documentation and regex literals do not self-trigger. NOT
                  bypassed by ALLOW_EMDASH.
    secret        Token-shaped strings (Telegram bot token, sk-/sk-ant- keys,
                  Slack/GitHub/AWS/Google/Stripe tokens, PEM private-key headers),
                  a password inside a URL, Bearer and API-key headers, JWTs, a
                  token in a query string (sig=, token=, key=), and API-KEY /
                  TOKEN / SECRET / PASSWORD style assignments set to a
                  high-entropy value. The shapes live in _common.py, shared with
                  the redactor. Always on, not gated on the patterns file,
                  NOT bypassed by ALLOW_EMDASH. The matched value is never echoed.
                  This is the out-of-the-box half of the guard: even with an empty
                  patterns file a stray secret in a tracked file is blocked.
    remote-safety (--staged only) Refuses to commit while the founder's personal
                  data is tracked (core/identity.md is in the index) AND any git
                  remote's push destination still points at the public FounderOS
                  repo (github.com/ARCASSystems). Every push destination is
                  checked - all pushurl values if any are set, otherwise all url
                  values, because git pushes to every one of them, so one safe
                  URL in the list must not hide a public one. In that state one
                  `git push` publishes their identity. Setup and own-your-history rename the
                  public remote to founderos-upstream and disable its push URL;
                  this check is the backstop for installs that missed that step.
                  Passes silently in the public dev repo (identity is not tracked
                  there), on CI (--range never runs it), and after the rename.
    line-ending   (--staged only) Refuses a staged text file carrying a lone CR
                  inside its content, or whose ending style flips against HEAD.
                  A lone CR turns off git's autocrlf normalization, so one stray
                  byte restyles a whole file: the real diff vanishes into churn and
                  the next machine appending to that file writes a mixed one.
                  `raw/` is exempt (write-once provenance). Override: ALLOW_EOL=1.
    entry-form    (--staged only) Validates ADDED lines in the files
                  rules/entry-conventions.md governs (brain/log.md, patterns,
                  flags, decisions-parked, needs-input, knowledge/, and their
                  templates/ mirrors) against the canonical form: field names
                  exact, dates and decay durations readable, entry ids on the
                  right channel with a 3-digit counter. Forward-only by
                  construction, since a diff has no old lines in it. Narrow on
                  purpose: the failure worth blocking is a field spelled
                  `Decay After:` that no scanner ever sees, so the entry never
                  surfaces and nothing says so. Override: ALLOW_ENTRY=1.

Graceful no-op: the .githooks wrappers exit 0 when Python is absent, so this
never breaks a user's `git commit`. With Python present but no patterns file,
only the name check is skipped (secret + em-dash + attribution still run, so the
guard does useful work out of the box). Exit 1 on any violation in every mode;
exit 0 when clean.
"""

from __future__ import annotations

import datetime as _dt
import os
import re
import subprocess
import sys
from pathlib import Path

# Built via chr() (not the literal chars) so this scanner's own source stays
# ASCII and never trips the em-dash check when it is committed.
EM_DASH = chr(0x2014)
EN_DASH = chr(0x2013)

# Attribution patterns anchored to line start (after an optional unified-diff
# marker + / - and whitespace). Real git trailers begin at column 0; rule docs
# and regex source literals do not, so the anchoring removes the
# self-trigger-on-our-own-docs false-positive class.
ATTRIBUTION_PATTERNS = [
    re.compile(r"^[+\- ]?\s*Co-Authored-By:\s*Claude", re.IGNORECASE),
    re.compile(r"^[+\- ]?\s*Co-Authored-By:.*(?:claude|anthropic)", re.IGNORECASE),
    re.compile(r"^[+\- ]?\s*Generated with.*Claude Code", re.IGNORECASE),
    re.compile(r"^[+\- ]?\s*Generated by Claude", re.IGNORECASE),
    re.compile(r"^[+\- ]?\s*\U0001F916\s*Generated", re.IGNORECASE),
]


def _force_utf8_streams() -> None:
    """Make stdout/stderr UTF-8 tolerant so printing a flagged em-dash line on a
    Windows cp1252 console degrades to '?' instead of crashing (a crash would
    exit non-1 and could let a bad commit through)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def load_patterns(patterns_file: Path) -> list[re.Pattern[str]]:
    if not patterns_file.exists():
        return []
    patterns = []
    for lineno, line in enumerate(patterns_file.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if any(ord(ch) < 32 for ch in line):
            # A shell echo -e turns a literal \b into a backspace byte and the
            # pattern silently matches nothing. A dead guard that looks loaded
            # is worse than no guard - name it and skip it.
            print(
                f"[private-name] WARNING: pattern on line {lineno} of "
                f"{patterns_file.name} contains control characters (a shell "
                f"echo mangled \\b?) - pattern ignored. Rewrite it with a "
                f"file editor, not a shell echo.",
                file=sys.stderr,
            )
            continue
        try:
            patterns.append(re.compile(line))
        except re.error as exc:
            print(
                f"[private-name] WARNING: pattern on line {lineno} of "
                f"{patterns_file.name} is not a valid regex ({exc}) - "
                f"pattern ignored.",
                file=sys.stderr,
            )
    return patterns


# A long unbroken base64 run (embedded font/image data URIs). A short name regex
# like \bSam\b can match inside base64 because +, / and = are non-word chars, so
# \b boundaries fire. Skip these lines for every check-set.
_BASE64_RUN = re.compile(r"[A-Za-z0-9+/]{200,}={0,2}")


def is_base64_blob(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 200:
        return False
    return _BASE64_RUN.search(stripped) is not None


# --- Secret detection (always on; not gated on the patterns file, not bypassable
# by ALLOW_EMDASH). A secret in a tracked file is the failure the privacy work
# exists to prevent, so the check ships active out of the box. The shapes live in
# _common.py because the observation log and the rant capture hide the same
# shapes before they write: one list, so the three readers cannot drift apart.
# It includes credentials inside a URL, Bearer and API-key headers, JWTs and
# tokens in a query string, each flagged only when the value looks real.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    CONTEXT_SECRET_PATTERNS,
    SECRET_SHAPE_PATTERNS,
    _looks_like_real_secret,
    find_secret,
)


def scan_text(
    text: str,
    patterns: list[re.Pattern[str]],
    *,
    allow_emdash: bool = False,
    check_dashes: bool = True,
    check_secrets: bool = True,
    check_attribution: bool = True,
    places: list[str] | None = None,
) -> list[str]:
    """Scan text line by line for all four check-sets. Returns rendered offending
    lines tagged with the kind. Secret values are never echoed back. `places`,
    when given, names each line's file and line number (see
    _added_lines_with_places); without it a line is named by its position."""
    offending: list[str] = []
    for line_num, raw in enumerate(text.splitlines(), 1):
        if is_base64_blob(raw):
            continue
        where = (places[line_num - 1] if places and line_num <= len(places)
                 else f"line {line_num}")
        # The secret check runs FIRST, and when it fires the raw line is never
        # shown by ANY finding on that line - a private-name or dash finding
        # that echoed the line would print the very secret the secret finding
        # hides. One line, one display decision.
        secret_kind = find_secret(raw) if check_secrets else None
        line = ("possible secret detected (line hidden)" if secret_kind
                else raw.rstrip())
        for pat in patterns:
            if pat.search(raw):
                offending.append(f"  [private-name] {where}: {line}")
                break
        if check_dashes and not allow_emdash and (EM_DASH in raw or EN_DASH in raw):
            offending.append(f"  [emdash] {where}: {line}")
        if check_attribution:
            for ap in ATTRIBUTION_PATTERNS:
                if ap.search(raw):
                    offending.append(f"  [attribution] {where}: {line}")
                    break
        if secret_kind:
            offending.append(
                f"  [secret:{secret_kind}] {where}: possible secret detected (value hidden)"
            )
    return offending


def get_staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached", "--no-color"],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        print(
            f"git diff --cached failed (exit {result.returncode}): {result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(1)
    return result.stdout


def _added_lines(diff: str) -> str:
    return "\n".join(
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def _added_lines_with_places(diff: str) -> tuple[str, list[str]]:
    """The added lines of a diff, and for each one its file and its line number
    in the new version. A refusal that said "line 210" counted across the whole
    staged diff and named no file, so a founder could not find the line."""
    lines: list[str] = []
    places: list[str] = []
    path, new_no = "?", 0
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            target = raw[4:]
            path = target[2:] if target.startswith("b/") else target
            continue
        if raw.startswith("@@"):
            m = _HUNK_RE.match(raw)
            new_no = int(m.group(1)) if m else 0
            continue
        if raw.startswith("+"):
            lines.append(raw[1:])
            places.append(f"{path} line {new_no}")
            new_no += 1
        elif raw.startswith(" "):
            new_no += 1
    return "\n".join(lines), places


def resolve_patterns_file() -> Path:
    override = os.environ.get("PRIVATE_NAME_PATTERNS_FILE")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "private-name-patterns.txt"


def _git_text(cmd: list[str], timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except Exception:
        return ""
    return result.stdout if result.returncode == 0 else ""


def _rev_parse(ref: str) -> str:
    return _git_text(["git", "rev-parse", ref], timeout=10).strip()


def _commit_message(sha: str) -> str:
    return _git_text(["git", "log", "-1", "--format=%B", sha], timeout=10)


def _commit_diff(sha: str) -> str:
    return _git_text(["git", "show", "--format=", sha], timeout=15)


def _resolves(ref: str) -> bool:
    return bool(_git_text(["git", "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"], timeout=10).strip())


def _commits_in_range(rng: str) -> list[str] | None:
    """Resolve a range to commit SHAs. Accepts BASE..HEAD, a single ref, or a
    GitHub all-zeros BASE (new branch push), scanned as just the tip.

    Returns None when an end of the range does not resolve (a typo, a base a
    force push removed, a shallow clone). That used to come back as an empty
    list, which scanned nothing and passed: a green check over zero commits."""
    if ".." in rng:
        base, _, head = rng.partition("..")
        base = base.rstrip(".")
        head = head or "HEAD"
        if base and set(base) <= {"0"}:
            sha = _rev_parse(head) if _resolves(head) else ""
            return [sha] if sha else None
        if not (_resolves(base) and _resolves(head)):
            return None
        out = _git_text(["git", "log", "--format=%H", f"{base}..{head}"])
        return out.strip().splitlines() if out else []
    if not _resolves(rng):
        return None
    sha = _rev_parse(rng)
    return [sha] if sha else None


def _report(header: str, offending: list[str]) -> None:
    print(header, file=sys.stderr)
    for line in offending:
        print(line, file=sys.stderr)
    print("", file=sys.stderr)
    if any("[secret:" in line for line in offending):
        print(
            "A line above looks like a password or key. Take it out of that file (a key "
            "belongs in .env, which is never saved), then save again.",
            file=sys.stderr,
        )
    # The dash override is offered only when a dash is what refused the save.
    # Printed under a secret or a name, it pointed at a switch that changes nothing.
    if any("[emdash]" in line for line in offending):
        print(
            "Escape hatch: ALLOW_EMDASH=1 bypasses em/en dash (not private-name, attribution, secret, or remote-safety).",
            file=sys.stderr,
        )


# Matches a push destination at the public FounderOS repo, https or ssh form.
_PUBLIC_REPO_URL = re.compile(
    r"github\.com[:/]ARCASSystems/FounderOS(?:\.git)?/?$", re.IGNORECASE)


def is_founder_install() -> bool:
    """True when this repo is a founder's installed OS, not the product repo.

    The signal is the one remote-safety has always used: the founder's identity
    file is in the index. The product repo never tracks it (its developer
    .gitignore keeps founder data out), and an install that owns its history
    always does. The house rules of the product (no em or en dashes, line-ending
    and entry-form discipline) gate the product repo only. Applied to a
    founder's data they refused ordinary saves: a pasted client email with an
    em dash stopped "save my work", and the only way past was an environment
    variable no founder can set."""
    return bool(_git_text(["git", "ls-files", "--", "core/identity.md"], timeout=10).strip())


def check_remote_safety() -> list[str]:
    """Return violations when personal data is tracked and a remote can still
    push to the public repo. See the remote-safety check-set in the module
    docstring. Any git error (not a repo, no remotes, no config matches) is a
    silent pass - this backstop must never break an ordinary commit."""
    if not is_founder_install():
        return []
    config = _git_text(["git", "config", "--get-regexp", r"^remote\."], timeout=10)
    if not config:
        return []
    remotes: dict[str, dict[str, list[str]]] = {}
    for line in config.splitlines():
        key, _, value = line.partition(" ")
        parts = key.split(".")
        if len(parts) < 3 or parts[-1] not in ("url", "pushurl"):
            continue
        name = ".".join(parts[1:-1])
        remotes.setdefault(name, {}).setdefault(parts[-1], []).append(value.strip())
    offending: list[str] = []
    for name, urls in sorted(remotes.items()):
        # git pushes to EVERY pushurl when any is set (else every url), so a
        # remote is unsafe if ANY of its push destinations is the public repo.
        push_targets = urls.get("pushurl") or urls.get("url") or []
        if any(_PUBLIC_REPO_URL.search(t) for t in push_targets):
            offending.append(
                f"  [remote-safety] remote '{name}' can push to the public FounderOS repo\n"
                f"    while your personal data (core/identity.md) is tracked. One git push\n"
                f"    would publish it. Fix (keeps updates flowing in, blocks anything out):\n"
                f"      git remote rename {name} founderos-upstream\n"
                f"      git remote set-url --push founderos-upstream DISABLED\n"
                f"    Or say 'own my history' and the OS does it for you."
            )
    return offending


# --- line-ending gate (--staged only) ---
# A lone carriage return inside a file's content turns off git's autocrlf
# normalization, so the whole file lands CRLF and every line reads as changed.
# The real diff disappears into the churn, and the next machine to append to that
# file writes the other ending into it. Public users are cross-platform by
# definition, which makes this corruption a founder cannot reasonably debug.
# Override for a deliberate normalization commit: ALLOW_EOL=1.
EOL_TEXT_SUFFIXES = (".md", ".py", ".txt", ".yaml", ".yml", ".json", ".jsonl",
                     ".html", ".css", ".js", ".toml", ".cfg")


def staged_files() -> list[str]:
    """Paths added, copied or modified in the index, forward slashes."""
    out = _git_text(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"])
    return [p.replace("\\", "/").strip() for p in out.splitlines() if p.strip()]


def _git_bytes(cmd: list[str], timeout: int = 15) -> bytes:
    """Raw stdout. _git_text passes text=True, which translates line endings and
    so cannot be used to inspect them."""
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except Exception:
        return b""
    return result.stdout if result.returncode == 0 else b""


def _eol_style(blob: bytes) -> str:
    crlf = blob.count(b"\r\n")
    lf = blob.count(b"\n") - crlf
    if crlf and lf:
        return "mixed"
    return "CRLF" if crlf else "LF" if lf else "none"


def _eol_exempt(rel: str) -> bool:
    """raw/ is a write-once provenance zone: a source document keeps whatever
    control bytes it arrived with, and a file nobody rewrites cannot produce the
    churn this gate exists to stop."""
    return rel.startswith("raw/") or "/raw/" in rel


def eol_defects(
    files_provider=None, staged_blob=None, head_blob=None,
) -> list[str]:
    """One line per staged text file whose line endings would land wrong."""
    files = (files_provider or staged_files)()
    get_staged = staged_blob or (lambda p: _git_bytes(["git", "show", f":{p}"]))
    get_head = head_blob or (lambda p: _git_bytes(["git", "show", f"HEAD:{p}"]))
    out: list[str] = []
    for rel in files:
        if not rel.endswith(EOL_TEXT_SUFFIXES) or _eol_exempt(rel):
            continue
        blob = get_staged(rel)
        if not blob or b"\x00" in blob:
            continue
        if blob.count(b"\r") > blob.count(b"\r\n"):
            out.append(f"{rel}: a stray carriage return sits inside the content "
                       f"rather than at a line end. git stores the whole file CRLF "
                       f"because a lone CR turns off autocrlf normalization")
            continue
        before = get_head(rel)
        if not before:
            continue  # new file: no previous style to flip away from
        was, now = _eol_style(before), _eol_style(blob)
        if was != now and "none" not in (was, now):
            out.append(f"{rel}: line endings flip {was} to {now}, so every line "
                       f"reads as changed and the next machine to append to this "
                       f"file produces a mixed one")
    return out


# --- staged entry-form gate (--staged only) ---
# The convention lives in rules/entry-conventions.md and the failure it guards is
# silence: a decay field spelled `Decay After:` is never seen by the scanner that
# reads it, so the entry simply never surfaces for review and nothing tells you.
# Deliberately narrow. It reads ADDED lines only, in the files the convention
# actually governs, and it checks form rather than judgment - a checker that
# manufactures findings teaches you to ignore the real ones.
# Override: ALLOW_ENTRY=1.
ENTRY_CHANNELS = {
    "brain/log.md": "log",
    "brain/patterns.md": "pattern",
    "brain/flags.md": "flag",
    "brain/decisions-parked.md": "parked",
    "brain/needs-input.md": "need",
}
ENTRY_CHANNEL_NAMES = ("log", "pattern", "flag", "parked", "need", "know")

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DURATION_RE = re.compile(r"^\d+d$")
_ID_RE = re.compile(r"\b([a-zA-Z]+)-(\d{4}-\d{2}-\d{2})-(\d+)\b")


def _real_date(value: str) -> bool:
    """Shape is not enough: 2026-99-99 matches the regex and can never fire.
    A decay date or entry id carrying an impossible date silently never
    surfaces, which is the exact failure this guard exists to catch."""
    try:
        _dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False
# A near-miss on a canonical field name: right words, wrong case or spacing.
_NEAR_MISS_RE = re.compile(
    r"^\s*[-*]?\s*(decay\s*after|decay\s*reason|superseded\s*by|invalidated\s*on|"
    r"replaces|first\s*observed|date\s*parked)\s*:",
    re.IGNORECASE)
_CANONICAL_FIELDS = ("Decay after:", "Decay reason:", "Superseded by:",
                     "Invalidated on:", "Replaces:", "First observed:",
                     "Date parked:")
# A dated field only counts as one when it OPENS the line, optionally as a list
# item and optionally bolded. Matching the words anywhere on the line turns every
# sentence that explains the convention into a finding, and a checker that
# manufactures findings teaches you to ignore the real ones.
_DATED_FIELD_RE = re.compile(
    r"^\s*(?:[-*]\s+)?\*{0,2}(Decay after|Invalidated on|First observed|Date parked)"
    r"\*{0,2}:\*{0,2}\s*(.*)$")


def _is_placeholder(value: str) -> bool:
    """An unfilled template slot is not a wrong value. `[YYYY-MM-DD]`,
    `<Nd, e.g. 90d>` and `{{TODAY}}` are the shipped forms."""
    return value.startswith(("[", "<", "{{")) or "{{" in value


def _entry_channel(rel: str) -> str | None:
    rel = rel.replace("templates/", "", 1) if rel.startswith("templates/") else rel
    if rel in ENTRY_CHANNELS:
        return ENTRY_CHANNELS[rel]
    if rel.startswith("brain/knowledge/") and rel.endswith(".md"):
        return "know"
    return None


def _added_lines_by_file(diff: str) -> dict[str, list[str]]:
    """{path: [added lines]} from a unified diff, so a check can be path-scoped."""
    out: dict[str, list[str]] = {}
    cur: str | None = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:].replace("\\", "/").strip()
            out.setdefault(cur, [])
        elif line.startswith("+++ ") or line.startswith("--- "):
            continue
        elif line.startswith("diff --git"):
            cur = None
        elif cur and line.startswith("+"):
            out[cur].append(line[1:])
    return out


def entry_defects(diff: str) -> list[str]:
    out: list[str] = []
    for rel, lines in _added_lines_by_file(diff).items():
        channel = _entry_channel(rel)
        if channel is None:
            continue
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            m = _NEAR_MISS_RE.match(line)
            if m and not any(f in line for f in _CANONICAL_FIELDS):
                seen = m.group(1)
                out.append(f"{rel}: `{seen}:` is not a field name anything reads. "
                           f"The convention is case-sensitive with one space after "
                           f"the colon, so this entry silently never surfaces. "
                           f"Canonical: {', '.join(_CANONICAL_FIELDS)}")
                continue

            fm = _DATED_FIELD_RE.match(line)
            if fm:
                field, value = fm.group(1), fm.group(2).strip()
                if value and not _is_placeholder(value):
                    if _DATE_RE.match(value):
                        ok = _real_date(value)
                    else:
                        ok = bool(_DURATION_RE.match(value)) if field == "Decay after" else False
                    if not ok:
                        want = ("a real YYYY-MM-DD date or a duration like 14d"
                                if field == "Decay after" else "a real YYYY-MM-DD date")
                        out.append(f"{rel}: `{field}: {value}` is not readable. "
                                   f"Expected {want}.")

            for idm in _ID_RE.finditer(stripped):
                chan, id_date, counter = idm.groups()
                if chan.lower() not in ENTRY_CHANNEL_NAMES:
                    continue  # not an entry id, just a dated slug
                if chan != channel:
                    out.append(f"{rel}: id `{idm.group(0)}` uses the `{chan}` "
                               f"channel in a `{channel}` file.")
                elif not _real_date(id_date):
                    out.append(f"{rel}: id `{idm.group(0)}` carries an impossible "
                               f"calendar date, so nothing date-driven will ever "
                               f"surface it.")
                elif len(counter) != 3:
                    out.append(f"{rel}: id `{idm.group(0)}` needs a 3-digit "
                               f"zero-padded counter, so 001 rather than {counter}.")
    return out


def run_staged(patterns: list[re.Pattern[str]], allow_emdash: bool) -> int:
    founder = is_founder_install()
    offending = check_remote_safety()
    diff = get_staged_diff()
    # Private names, secrets and AI attribution are checked everywhere. The
    # dash, line-ending and entry-form rules are the product repo's house
    # rules, so a founder's own data is never refused for them.
    added, places = _added_lines_with_places(diff)
    offending += scan_text(added, patterns, allow_emdash=allow_emdash,
                           check_dashes=not founder, places=places)
    if not founder and os.environ.get("ALLOW_EOL", "0") != "1":
        offending += [f"{d}  (deliberate normalization commit: ALLOW_EOL=1)"
                      for d in eol_defects()]
    if not founder and os.environ.get("ALLOW_ENTRY", "0") != "1":
        offending += [f"{d}  (override: ALLOW_ENTRY=1)"
                      for d in entry_defects(diff)]
    if offending:
        _report("BLOCKED: guard violations in staged diff:", offending)
        return 1
    return 0


def run_message(path: str, patterns: list[re.Pattern[str]], allow_emdash: bool) -> int:
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"Could not read commit message at {path}: {exc}", file=sys.stderr)
        return 1
    offending = scan_text(text, patterns, allow_emdash=allow_emdash,
                          check_dashes=not is_founder_install())
    if offending:
        _report("BLOCKED: guard violations in commit message:", offending)
        return 1
    return 0


def run_range(rng: str, patterns: list[re.Pattern[str]], allow_emdash: bool) -> int:
    shas = _commits_in_range(rng)
    if shas is None:
        print(f"BLOCKED: could not resolve the range {rng!r}, so nothing was scanned. "
              "Check both ends exist in this clone (a force push or a shallow fetch "
              "can remove the base).", file=sys.stderr)
        return 1
    if not shas:
        return 0
    total = 0
    dashes = False
    for sha in shas:
        offending = scan_text(_commit_message(sha), patterns, allow_emdash=allow_emdash)
        added, places = _added_lines_with_places(_commit_diff(sha))
        offending += scan_text(added, patterns, allow_emdash=allow_emdash, places=places)
        if offending:
            print(f"BLOCKED: guard violations in commit {sha[:8]}:", file=sys.stderr)
            for line in offending:
                print(line, file=sys.stderr)
            total += len(offending)
            dashes = dashes or any("[emdash]" in line for line in offending)
    if total:
        print("", file=sys.stderr)
        hatch = " Escape hatch (em/en dash only): ALLOW_EMDASH=1." if dashes else ""
        print(f"guard: {total} violation(s).{hatch}", file=sys.stderr)
        return 1
    return 0


def run_baseline(allow_emdash: bool) -> int:
    """Full-tree em/en dash gate. Reads every tracked file's whole content (not
    just added diff lines) so a dash that predates any commit range cannot hide.
    Dash check-set only - private-name, secret, and attribution stay on their own
    modes, and remote-safety (staged only) is untouched. Binary and unreadable
    files are skipped. Exit 1 on any dash, 0 when the tree is clean."""
    # -z: NUL-delimited, unquoted paths, so filenames with newlines or
    # non-ASCII characters enumerate correctly.
    listing = _git_text(["git", "ls-files", "-z"])
    total = 0
    for rel in listing.split("\0"):
        if not rel:
            continue
        path = Path(rel)
        try:
            if not path.is_file():
                continue
            data = path.read_bytes()
        except OSError:
            continue  # unreadable file: nothing to scan
        if b"\0" in data:
            continue  # binary regardless of UTF-8 validity (git's own heuristic)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue  # not UTF-8 text: nothing to scan
        offending = scan_text(
            text,
            [],
            allow_emdash=allow_emdash,
            check_secrets=False,
            check_attribution=False,
        )
        if offending:
            print(f"BLOCKED: em/en dash in {rel}:", file=sys.stderr)
            for line in offending:
                print(line, file=sys.stderr)
            total += len(offending)
    if total:
        print("", file=sys.stderr)
        print(
            f"baseline: {total} em/en dash(es) across the tree. The house voice "
            "bans them. Escape hatch: ALLOW_EMDASH=1.",
            file=sys.stderr,
        )
        return 1
    return 0


def main() -> int:
    _force_utf8_streams()
    args = sys.argv[1:]
    usage = "Usage: check-private-names.py --staged | --message <path> | --range <BASE..HEAD> | --baseline"
    if not args:
        print(usage, file=sys.stderr)
        return 1

    patterns_file = resolve_patterns_file()
    patterns = load_patterns(patterns_file)
    if not patterns and patterns_file.exists() and not is_founder_install():
        # Maintainer note only. In an installed OS an empty file is the
        # recommended default, so it says nothing on every save, and it never
        # asks anyone to type their own name in: a founder's name in that file
        # blocks every save of their own identity.
        print(
            f"Note: {patterns_file.name} holds no patterns, so the name check is off. "
            "The secret and attribution checks still run.",
            file=sys.stderr,
        )

    allow_emdash = os.environ.get("ALLOW_EMDASH", "0") == "1"

    if args[0] == "--staged":
        return run_staged(patterns, allow_emdash)
    if args[0] == "--message" and len(args) >= 2:
        return run_message(args[1], patterns, allow_emdash)
    if args[0] == "--range" and len(args) >= 2:
        return run_range(args[1], patterns, allow_emdash)
    if args[0] == "--baseline":
        return run_baseline(allow_emdash)

    print(usage, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
