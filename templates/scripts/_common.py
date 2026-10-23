"""
Canonical helpers shared across scripts: the wiki-layer scope (wiki-build.py
and query.py), the dated entry heading, the secret shapes and redactor (the
pre-commit scan, the observation log and the rant capture), and the seeded
example entry filter (brain-snapshot.py and what-to-change.py).

Both scripts must agree on which markdown files compose the wiki-layer
graph; before this module existed, they computed that set via two different
mechanisms (prefix-string startswith vs part-set intersection), coupled only
by manual "also update" comments that no test enforced. Drift between the
two produces silent disagreement between the on-disk graph (relations.yaml)
and the in-memory graph (query). Defining the scope here once eliminates
the drift class.

Pure stdlib. No new install dependency - the free-tier accessibility floor
stays intact. See plans/v1.27-f38-rglob-consolidation-2026-05-22.md.
"""

from __future__ import annotations

import re
from pathlib import Path

# The one regex for "a dated entry heading" across the OS. Three heading forms
# ship in three docs (### [YYYY-MM-DD] #tag, ### YYYY-MM-DD #tag,
# ### YYYY-MM-DD HH:MM - #tag) and flags use ## - a reader pinned to one form
# silently sees an empty log (the menu bug: DAILY_HEADER required H2 and
# end-of-line, matching none of them). Every reader matches THIS. The brief
# hook keeps a literal copy (it cannot import from scripts/) - a parity test
# asserts the copies stay identical. After the date comes a space, the end of
# the line, punctuation, or a time: "### 2026-10-20: call", "### 2026-10-20,
# call" and "### 2026-10-20T10:30" are entries, and the readers that moved onto
# this pattern counted them before the move. A letter or digit glued to the
# date ("### 2026-05-07x") is not a date.
ENTRY_DATE_HEADING_PATTERN = r"^#{2,3}\s+\[?(\d{4}-\d{2}-\d{2})\]?(?=[\s:,;.)]|$|T\d)"
ENTRY_DATE_HEADING = re.compile(ENTRY_DATE_HEADING_PATTERN)


WIKI_LAYER_PREFIXES: tuple[str, ...] = (
    "core",
    "context",
    "cadence",
    "brain",
    "network",
    "companies",
    "roles",
    "rules",
)

WIKI_LAYER_EXCLUDED_PARTS: frozenset[str] = frozenset({
    ".git",
    ".claude",
    "skills",
    "docs",
    "raw",
    "templates",
    "node_modules",
    "archive",
    "transcripts",
    "rants",
    "tests",
    "__pycache__",
    # The OS's own scratch: session snapshots, update backups and setup-reset
    # backups. Every file there is a stale copy of a founder file, so a search
    # that read it returned text the founder had since changed or deleted.
    "state",
})


def is_wiki_layer_path(
    rel_path: str, include_rants: bool = False, include_archive: bool = False
) -> bool:
    """True iff a forward-slash relative path is in the wiki-layer graph scope.

    The first segment must be one of WIKI_LAYER_PREFIXES, and no segment may
    appear in WIKI_LAYER_EXCLUDED_PARTS. When include_rants is True, "rants"
    is dropped from the excluded set so brain/rants/ files can pass. When
    include_archive is True, "archive" is dropped so brain/archive/ passes -
    log-archive.py writes exactly there, and a search scope that excludes it
    tells a six-month user "not found" about data on their own disk.

    Caller is responsible for forward-slash normalisation; a literal-backslash
    string like "brain\\log.md" is not normalised and returns False.
    """
    parts = rel_path.split("/")
    if not parts or parts[0] not in WIKI_LAYER_PREFIXES:
        return False
    excluded = set(WIKI_LAYER_EXCLUDED_PARTS)
    if include_rants:
        excluded.discard("rants")
    if include_archive:
        excluded.discard("archive")
    if any(p in excluded for p in parts):
        return False
    return True


def wiki_layer_files(
    root: Path, include_rants: bool = False, include_archive: bool = False
) -> list[Path]:
    """All wiki-layer .md files under root, deterministically sorted.

    Walks each prefix folder via rglob and filters with is_wiki_layer_path.
    Does NOT include CLAUDE.md or other DEFAULT_FILES - those are query-local
    score seeds, not graph edges. Does NOT include .yaml/.yml - only .md.
    """
    found: set[Path] = set()
    for prefix in WIKI_LAYER_PREFIXES:
        folder = root / prefix
        if not folder.exists():
            continue
        for path in folder.rglob("*.md"):
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                continue
            if is_wiki_layer_path(rel, include_rants=include_rants, include_archive=include_archive):
                found.add(path)
    return sorted(found)


# --------------------------------------------------------------------------- #
# Secret shapes and the one redactor                                            #
# --------------------------------------------------------------------------- #
# One list, three readers: the pre-commit secret scan (check-private-names.py),
# the opt-in observation log (hooks/dispatch.py) and the eager rant capture
# (user-prompt-capture.py). Before this lived here the hook kept its own keyword
# list, which drifted from the pre-commit list, and the rant capture had no
# filter at all, so a pasted connection string landed word for word in a
# tracked brain file. The regex sources below are written so that no literal in
# them forms a complete secret of its own shape, so this file never trips the
# scan that reads it.

# Unmistakable shapes. Any match is a secret, in every reader.
SECRET_SHAPE_PATTERNS = [
    # Telegram BotFather token: <8-10 digits>:<35+ url-safe chars>.
    ("telegram-bot-token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35,}")),
    # Anthropic / OpenAI keys. The ant-/proj- markers are rare literals, so a
    # hyphenated body is safe; plain sk- needs 40 contiguous alnum so hyphenated
    # slugs (sk-related-thing) cannot false-trip.
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai-proj-key", re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{40,}\b")),
    # Slack tokens (xoxb-, xoxp-, xoxa-, xoxr-, xoxs-).
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    # GitHub tokens.
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    # AWS access key id.
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    # Google API key.
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    # Stripe live / test keys.
    ("stripe-key", re.compile(r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    # ElevenLabs key: sk_ then hex. The speech add-on's own key.
    ("elevenlabs-key", re.compile(r"\bsk_[0-9a-f]{32,}\b")),
    # Incoming webhook URLs. Anyone holding one can post as the app.
    ("slack-webhook", re.compile(
        r"hooks\.slack\.com/services/T[A-Z0-9]{6,}/B[A-Z0-9]{6,}/[A-Za-z0-9]{16,}")),
    ("discord-webhook", re.compile(
        r"discord(?:app)?\.com/api/webhooks/\d{6,}/[A-Za-z0-9_-]{20,}")),
    # PEM private key header.
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
]

# Shapes that carry a secret in a named slot: a password inside a URL, a Bearer
# header, a signature in a query string. Each regex names the secret part `v`.
# The redactor hides a match (the structural ones always, the header-like ones
# when the value is not plain prose). The pre-commit scan flags a match only
# when `v` looks real (see find_secret), so documentation that writes
# `postgres://user:pass@host` or `?key=YOUR_KEY` is not refused.
CONTEXT_SECRET_PATTERNS = [
    # scheme://user:password@host - a database URL, a git remote with a token.
    # The scheme is bounded and may not start inside a longer run of scheme
    # characters: unbounded, a long dotted paste made this regex quadratic
    # (64K characters took 21 seconds inside a hook that runs on every prompt).
    ("url-credentials", re.compile(
        r"(?i)(?<![a-z0-9+.-])[a-z][a-z0-9+.-]{0,30}://[^\s/:@'\"<>]+:(?P<v>[^\s/@'\"<>]+)@")),
    # scheme://token@host - a token used as the whole user part.
    ("url-token", re.compile(
        r"(?i)(?<![a-z0-9+.-])[a-z][a-z0-9+.-]{0,30}://(?P<v>[^\s/:@'\"<>]{6,})@")),
    # Authorization headers, any scheme.
    ("bearer-token", re.compile(r"(?i)\bbearer\s+(?P<v>[A-Za-z0-9._~+/=-]{12,})")),
    ("authorization-header", re.compile(
        r"(?i)\bauthorization['\"]?\s*[:=]\s*['\"]?(?P<s>(?:basic|bearer|token|digest)\s+)?"
        r"(?P<v>[A-Za-z0-9._~+/=-]{8,})")),
    ("api-key-header", re.compile(
        r"(?i)\b(?:x-api-key|api-key|x-auth-token|x-access-token|private-token)"
        r"['\"]?\s*:\s*['\"]?(?P<v>[^\s'\"]{8,})")),
    # A JSON Web Token: three base64url parts, the first opening with eyJ.
    ("jwt", re.compile(r"\b(?P<v>eyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,})")),
    # A storage signature in a query string (an Azure SAS link, an S3 presigned
    # link): it grants read or write access to the files themselves.
    ("url-signature", re.compile(
        r"(?i)[?&;](?:sig|signature|x-amz-signature)=(?P<v>[^\s&'\"#<>]{8,})")),
    # Any other secret riding in a query string: API keys, tokens, passwords.
    ("url-query-token", re.compile(
        r"(?i)[?&;](?:token|access_token|id_token|refresh_token"
        r"|api_?key|apikey|key|secret|client_secret|password|passwd|pwd|auth)"
        r"=(?P<v>[^\s&'\"#<>]{8,})")),
    # A Telegram bot URL: /bot<digits>:<token>/.
    ("telegram-bot-url", re.compile(r"(?i)/bot(?P<v>\d{5,}:[A-Za-z0-9_-]{3,})")),
    # Provider keys shorter than the strict shapes above require.
    ("short-ai-key", re.compile(r"\b(?P<v>sk-(?:ant|proj)-[A-Za-z0-9_-]{8,})")),
    ("short-host-token", re.compile(
        r"\b(?P<v>(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{4,}|github_pat_[A-Za-z0-9_]{8,}"
        r"|glpat-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9-]{6,})")),
]
# Context shapes whose structure alone says "secret": the redactor hides them
# whatever the value looks like. The rest (headers, a token as a URL user) can
# collide with prose ("authorization: required"), so the redactor wants a value
# that is not a plain word.
_STRUCTURAL_KINDS = frozenset({
    "url-credentials", "url-signature", "url-query-token", "telegram-bot-url", "jwt",
    "short-ai-key", "short-host-token",
})

# Context shapes the pre-commit scan never refuses a save for. A token or
# password in a query string is how Zoom and Webex invites, unsubscribe links
# and password reset links are written, so refusing it refused a founder's
# meeting notes and made auto-save fail every session. The redactor still hides
# these. A storage signature (url-signature) is still refused.
_SAVE_CHECK_SKIPS = frozenset({"url-query-token"})

# Wider shapes the redactor hides and the save check does not refuse. Each one
# is common in a pasted command or a dictated note, and each can also appear in
# ordinary text, so refusing a save on it would refuse real work. Hiding one in
# a rant or a log line costs nothing. Group `v` is the part hidden.
REDACT_ONLY_PATTERNS = [
    # A whole PEM private key, header to footer, or to the end of the text when
    # the footer was not pasted. Covers the escaped-newline form inside JSON
    # (a cloud service-account file).
    ("private-key-body", re.compile(
        r"(?s)(?P<v>-----BEGIN [A-Z ]{0,20}PRIVATE KEY-----.*?"
        r"(?:-----END [A-Z ]{0,20}PRIVATE KEY-----|\Z))")),
    # curl -u user:pass, --user user:pass.
    ("cli-user-password", re.compile(
        r"(?:^|\s)(?:-u|--user)[=\s]+['\"]?[^\s:'\"]+:(?P<v>[^\s'\"]+)")),
    # mysql -pPassword, the password glued to -p.
    ("mysql-password", re.compile(r"\bmysql(?:dump|admin)?\b[^\n]*?\s-p(?P<v>[^\s'\"]+)")),
    # A password flag after a login command (sshpass -p, docker login -p).
    ("cli-password-flag", re.compile(
        r"\b(?:sshpass|login)\b[^\n]*?\s(?:-p|--password)[=\s]+['\"]?(?P<v>[^\s'\"]+)")),
    # user:password@host with no scheme, as scp and pasted connection strings
    # write it. Bounded for the same reason as url-credentials.
    ("bare-url-credentials", re.compile(
        r"(?<![\w./-])[\w.-]{1,64}:(?P<v>[^\s@/:'\"<>]{1,128})@[\w-]+(?:\.[\w-]+)+")),
    # PowerShell: $env:NAME = 'value' and SetEnvironmentVariable('NAME', 'value').
    ("powershell-env", re.compile(r"(?i)\$env:[A-Za-z_]\w*\s*=\s*['\"](?P<v>[^'\"]+)['\"]")),
    ("powershell-setenv", re.compile(
        r"(?i)SetEnvironmentVariable\(\s*['\"][^'\"]+['\"]\s*,\s*['\"](?P<v>[^'\"]+)['\"]")),
    # export NAME=value in a shell.
    ("shell-export", re.compile(r"\bexport\s+[A-Za-z_]\w*=['\"]?(?P<v>[^\s'\"]+)")),
    # A secret said in words: "the password is X", "my pin was X".
    ("spoken-secret", re.compile(
        r"(?i)\b(?:password|passcode|passwd|pwd|pin|secret|token|api\s+key|key)\s+(?:is|was)"
        r"\s+['\"]?(?P<v>[^\s'\".,;]+)")),
    # A long run of key characters with no prefix: an AWS secret access key, a
    # base64 blob, an encoded credential. Kept only when it mixes upper, lower
    # and digits, so a git hash (lowercase hex), a UUID and a long word pass. A
    # run that starts after a slash, a dot or a colon is part of a link.
    ("long-key-run", re.compile(
        r"(?<![A-Za-z0-9/+=.:])(?P<v>[A-Za-z0-9+/]{32,}={0,2})(?![A-Za-z0-9/+=])")),
]
# Redact-only shapes that also match ordinary words, so the value must not be
# a plain word ("the key is to listen" stays, "the pin is 4321" goes).
_REDACT_WORD_GATED = frozenset({"bare-url-credentials", "spoken-secret", "shell-export"})
_REDACT_MIX_GATED = frozenset({"long-key-run"})

# Secret-NAMED assignment: an API-KEY / TOKEN / SECRET / PASSWORD style name set
# to a value, in env, YAML or JSON form ("password": "..."). The pre-commit scan
# wants a long, high-entropy value so docs and example lines do not false-trip;
# the redactor hides a shorter one too. A bare suffix needs its underscore
# (DB_PASS, MYSQL_PWD, NOTION_TOKEN, ELEVENLABS_KEY), so "monkey" is not a name.
# A name inside a query string (?pwd=, &token=) is a link, not an assignment:
# url-query-token covers it for the redactor, and the save check leaves links be.
_SECRET_NAME = re.compile(
    r"(?i)(?<![?&;])\b[a-z0-9_]*(?:api[_-]?key|secret[_-]?key|access[_-]?key|access[_-]?token"
    r"|auth[_-]?token|bot[_-]?token|api[_-]?token|client[_-]?secret|private[_-]?key"
    r"|secret|passwd|password|token|pwd|_key|_pass)\b['\"]?\s*[:=]\s*"
)
_SECRET_VALUE = re.compile(r"['\"]?([^\s'\"#,;]{16,})")
_SECRET_VALUE_LOOSE = re.compile(r"['\"]?([^\s'\"#,;]{6,})")
_PLACEHOLDER = re.compile(
    r"(?i)(your|example|placeholder|change[_-]?me|xxx|<[^>]*>|\.\.\.|todo|redact"
    r"|fill|here|none|null|true|false|enabled|disabled|sample|dummy"
    r"|\$\{|\$\(|%[a-z_]+%)"
)
_TOKEN_PREFIX = re.compile(
    r"(?i)^(?:sk-|ghp_|gho_|ghu_|ghs_|ghr_|github_pat_|glpat-|xox[baprs]-|eyJ)")


def _looks_like_real_secret(value: str) -> bool:
    """A captured value is a likely real secret only when it mixes letters and
    digits (high entropy) and is not an obvious placeholder. Requiring both
    letters and digits keeps prose, paths, and bare URLs from false-tripping."""
    if _PLACEHOLDER.search(value):
        return False
    # Code, not a credential: `token = match.group(1).strip()`. No key or
    # password format uses brackets.
    if any(c in "()[]{}" for c in value):
        return False
    has_alpha = any(c.isalpha() for c in value)
    has_digit = any(c.isdigit() for c in value)
    return has_alpha and has_digit


def find_secret(line: str) -> str | None:
    """Return a short kind-label if the line carries a likely secret, else None.

    This is the strict reader the pre-commit scan uses: the unmistakable
    shapes always count, a context shape counts when its secret part looks
    real or carries a known token prefix, and a named assignment counts when
    its value is long and high-entropy."""
    for kind, pat in SECRET_SHAPE_PATTERNS:
        if pat.search(line):
            return kind
    for kind, pat in CONTEXT_SECRET_PATTERNS:
        if kind in _SAVE_CHECK_SKIPS:
            continue
        for m in pat.finditer(line):
            v = m.group("v")
            if kind == "jwt" or _TOKEN_PREFIX.match(v):
                return kind
            # "Authorization: DED-2026-11234" is a permit number, and
            # sftp://user2024@host is a login name. Without a header scheme, or
            # a token long enough to be one, neither is a secret.
            if kind == "authorization-header" and not m.group("s"):
                continue
            if kind == "url-token" and len(v) < 20:
                continue
            if _looks_like_real_secret(v):
                return kind
    m = _SECRET_NAME.search(line)
    if m:
        tail = line[m.end():]
        v = _SECRET_VALUE.match(tail)
        if v and _looks_like_real_secret(v.group(1)):
            return "named-secret-assignment"
    return None


REDACTION_MARK = "[hidden: looked like a password or key]"


def _not_a_word(value: str) -> bool:
    return (any(c.isdigit() for c in value) or len(value) >= 20
            or bool(_TOKEN_PREFIX.match(value)))


def _mixed(value: str) -> bool:
    return (any(c.isupper() for c in value) and any(c.islower() for c in value)
            and any(c.isdigit() for c in value))


def secret_spans(text: str) -> list[tuple[int, int]]:
    """Every span of text the redactor hides, merged and sorted. Wider than
    find_secret on purpose: hiding a harmless value in a rant or a log line
    costs nothing, keeping a real one costs a leak."""
    spans: list[tuple[int, int]] = []
    for _kind, pat in SECRET_SHAPE_PATTERNS:
        spans.extend(m.span() for m in pat.finditer(text))
    for kind, pat in CONTEXT_SECRET_PATTERNS:
        for m in pat.finditer(text):
            v = m.group("v")
            # "Authorization: FZ-2026-118 from the free zone" is a permit in a
            # founder's own notes. With no header scheme, only a token counts.
            if (kind == "authorization-header" and not m.group("s")
                    and not _TOKEN_PREFIX.match(v) and len(v) < 20):
                continue
            if kind in _STRUCTURAL_KINDS or _not_a_word(v):
                spans.append(m.span("v"))
    for kind, pat in REDACT_ONLY_PATTERNS:
        for m in pat.finditer(text):
            v = m.group("v")
            if kind in _REDACT_WORD_GATED and not _not_a_word(v):
                continue
            if kind in _REDACT_MIX_GATED and not _mixed(v):
                continue
            spans.append(m.span("v"))
    for m in _SECRET_NAME.finditer(text):
        v = _SECRET_VALUE_LOOSE.match(text, m.end())
        if v and not _PLACEHOLDER.search(v.group(1)) and _not_a_word(v.group(1)):
            spans.append(v.span(1))
    spans.sort()
    merged: list[tuple[int, int]] = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def has_secret(text: str) -> bool:
    """True when the redactor would hide anything in text."""
    return bool(text) and bool(secret_spans(text))


def redact_secrets(text: str, mark: str = REDACTION_MARK) -> str:
    """Text with every secret-shaped span replaced by `mark`. Ordinary prose
    passes through unchanged."""
    if not text:
        return text
    out: list[str] = []
    last = 0
    for start, end in secret_spans(text):
        out.append(text[last:start])
        out.append(mark)
        last = end
    out.append(text[last:])
    return "".join(out)


_ENV_FILE_IN_COMMAND = re.compile(r"(?:^|[\s'\"/\\=>(:])\.env[\w.-]*(?=$|[\s'\";|&)<>])")


def is_env_path(path: str) -> bool:
    """True for a .env-style secrets file: .env, .env.local, .envrc and kin."""
    name = (path or "").replace("\\", "/").rsplit("/", 1)[-1]
    return name.lower().startswith(".env")


def names_env_file(command: str) -> bool:
    """True when a shell command names a .env-style file anywhere. Such a command
    reads or writes secrets, so its text is never kept."""
    return bool(command) and bool(_ENV_FILE_IN_COMMAND.search(command))


# --------------------------------------------------------------------------- #
# The seeded example entry in the flags and patterns templates                  #
# --------------------------------------------------------------------------- #
EXAMPLE_SECTION = re.compile(r"^##\s+Example\s*(?:\(|$)", re.IGNORECASE)
# Setup labels each seed "(example entry - ...)". Only that label counts: a
# founder's own "(example from the call)" is a real entry.
EXAMPLE_TITLE = re.compile(r"[(\[]\s*example\s+entry\b", re.IGNORECASE)
EXAMPLE_SEED_DATE = "2024-01-01"
_EXAMPLE_ENTRY_HEADER = re.compile(r"^#{2,3}\s+\S")


def example_line_numbers(lines: list[str]) -> set[int]:
    """Header lines of a template's seeded worked example.

    The flags and patterns templates each ship one example dated 2024-01-01
    under an `## Example (...)` heading, and setup re-dates each seed and labels
    it "(example entry - ...)". In the 9 Oct live runs the seeded flag
    "Outreach has not started this week" reached the snapshot as an open flag,
    and the next-move proposal cited it as the founder's own state. A demo is
    not evidence, so every reader that presents flags as the founder's state
    leaves it out.

    Narrow on purpose, so a real entry is never hidden: an entry counts as the
    seed only when its title carries the example label, or when it sits in the
    Example section and still carries the template's 2024-01-01 date. A seed
    edited in place into a real entry (new date, no label) shows again.
    """
    out: set[int] = set()
    inside = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if EXAMPLE_SECTION.match(stripped):
            inside = True
            continue
        if inside and (stripped == "---" or stripped.startswith("<!--")):
            inside = False
        if not _EXAMPLE_ENTRY_HEADER.match(stripped):
            continue
        if EXAMPLE_TITLE.search(stripped):
            out.add(idx)
            continue
        if inside:
            entry = [stripped]
            for follow in lines[idx + 1: idx + 10]:
                if _EXAMPLE_ENTRY_HEADER.match(follow.strip()):
                    break
                entry.append(follow)
            if any(EXAMPLE_SEED_DATE in part for part in entry):
                out.add(idx)
    return out


def normalize_wikilink_target(target: str) -> str:
    """Canonicalise a wikilink target so [[file]] and [[file.md]] dedupe.

    Converts backslashes to forward slashes, strips a trailing .md from the
    path part (preserving any #anchor suffix). Does not lowercase: preserves
    the user's display intent. Bare slugs pass through unchanged.
    """
    target = target.replace("\\", "/").strip()
    if "#" in target:
        path, _, anchor = target.partition("#")
        if path.endswith(".md"):
            path = path[:-3]
        return f"{path}#{anchor}" if anchor else path
    if target.endswith(".md"):
        return target[:-3]
    return target
