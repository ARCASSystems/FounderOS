#!/usr/bin/env python3
"""deliverable_gate.py - the deterministic floor under the ship-deliverable gate.

The problem it exists for: a pre-ship check that is entirely a reading task gets
skipped when you are in a hurry, and the things it catches are exactly the things
that embarrass you in front of a client. A leftover [FILL], last month's date, a
tool credited as the author. None of those need judgment - a grep sees them. So
they belong in a script that runs the same way every time and costs nothing,
which leaves the reading pass free to spend its attention on whether the content
is actually true and whether the thing looks right.

Each verb prints one line per check and exits 0 (nothing failed) or 2 (something
did). SKIP is a first-class result: it names what a text scan cannot judge (a
binary layout, a compressed PDF) so those go to the reading pass honestly labelled
instead of being silently guessed at here.

Verbs (all read-only - the deliverable is never modified):
  template <path>      structural fit: title/header, prepared-for line, date line,
                       and the brand font when os-config.yaml declares one
  placeholders <path>  [FILL] / [GAP] / [TODO] / TBD / lorem / unreplaced {{tokens}}
  date <path>          at least one date within 48h of --asof (your prep stamp)
  attribution <path>   AI-attribution strings, plus document author metadata
  evidence <path>      a blind-spot pass actually happened for this file
  all <path>           every verb above, one report, one exit code

Brand specifics are yours, not ours: the font and the document author name are
read from os-config.yaml when it exists. With no os-config those two checks SKIP
rather than inventing a default, because a wrong brand assumption is worse than
an honest gap.

Invariants: read-only, standard library only, ASCII-safe output, no network, no
API key. Exit 0 = no failures, 2 = at least one failure, 1 = no such file.

Usage:
  python scripts/deliverable_gate.py all path/to/deliverable.html
  python scripts/deliverable_gate.py placeholders drafts/proposal.md
  python scripts/deliverable_gate.py date report.docx --asof 2026-07-25
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTS = {".html", ".htm", ".md", ".txt"}
OFFICE_EXTS = {".docx", ".pptx", ".xlsx"}

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
_ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_LONG_DATE_RE = re.compile(
    r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{4})\b|"
    r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2}),?\s+(\d{4})\b", re.IGNORECASE)

# Attribution-shaped strings only. A bare mention of an AI tool can be legitimate
# CONTENT (you may write about the tools you use). What must never ship is
# authorship credit to a tool, or a document whose metadata names the library
# that generated it.
_ATTRIBUTION_RES = [
    re.compile(r"(?i)co-authored-by:?\s*(claude|codex|copilot|gpt)"),
    re.compile(r"(?i)generated (?:with|by) (?:claude|ai|chatgpt|copilot|gemini)"),
    re.compile(r"(?i)noreply@anthropic\.com"),
    re.compile(r"(?i)\bpython-docx\b"),
    re.compile(r"(?i)\bpython-pptx\b"),
    re.compile(r"(?i)\bopenpyxl\b"),
    re.compile(r"(?i)\bas an ai\b"),
]

_PLACEHOLDER_RES = [
    ("[FILL]", re.compile(r"\[FILL[^\]]*\]")),
    ("[GAP]", re.compile(r"\[GAP\]")),
    ("[TODO]", re.compile(r"\[TODO[^\]]*\]")),
    ("TBD", re.compile(r"\bTBD\b")),
    ("XXX", re.compile(r"\bXXX\b")),
    ("lorem ipsum", re.compile(r"(?i)lorem ipsum")),
    ("{{token}}", re.compile(r"\{\{[^}]+\}\}")),
]


class Check:
    __slots__ = ("verb", "name", "status", "detail")

    def __init__(self, verb: str, name: str, status: str, detail: str):
        self.verb, self.name, self.status, self.detail = verb, name, status, detail

    def line(self) -> str:
        return f"{self.verb}.{self.name}: {self.status} - {self.detail}"


def read_os_config(root: Path) -> dict:
    """Read the handful of flat `key: value` lines this gate needs from
    os-config.yaml. Deliberately minimal: it reads two nested keys under a
    `brand:` block and ignores everything else, so it cannot break when the
    config grows. Missing file returns {} and every brand check SKIPs."""
    cfg_path = root / "os-config.yaml"
    if not cfg_path.is_file():
        return {}
    out: dict[str, str] = {}
    section = ""
    try:
        text = cfg_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if indent == 0:
            section = key
            if value:
                out[key] = value
            continue
        if section and value:
            out[f"{section}.{key}"] = value
    return out


def _read_text(path: Path) -> str | None:
    """Scannable text: raw for text types, concatenated XML for office zips,
    best-effort bytes for PDF. None means the format cannot be scanned."""
    ext = path.suffix.lower()
    if ext in TEXT_EXTS:
        return path.read_text(encoding="utf-8", errors="replace")
    if ext in OFFICE_EXTS:
        try:
            with zipfile.ZipFile(path) as z:
                return "\n".join(
                    z.read(n).decode("utf-8", errors="replace")
                    for n in z.namelist() if n.endswith(".xml"))
        except (zipfile.BadZipFile, OSError):
            return None
    if ext == ".pdf":
        try:
            return path.read_bytes().decode("latin-1", errors="replace")
        except OSError:
            return None
    return None


# ---------------------------------------------------------------- template --

def check_template(path: Path, cfg: dict) -> list[Check]:
    ext = path.suffix.lower()
    font = cfg.get("brand.font")
    out: list[Check] = []

    def font_check(text: str, where: str) -> Check:
        if not font:
            return Check("template", "font", "SKIP",
                         "no brand.font in os-config.yaml - set one to check this")
        ok = font in text
        return Check("template", "font", "PASS" if ok else "FAIL",
                     f"brand font '{font}' present in {where}" if ok
                     else f"brand font '{font}' not found in {where}")

    if ext in (".html", ".htm"):
        text = path.read_text(encoding="utf-8", errors="replace")
        out.append(font_check(text, "the markup"))
        foot_ok = bool(re.search(r'(?i)<footer|class="[^"]*foot', text))
        out.append(Check("template", "footer", "PASS" if foot_ok else "FAIL",
                         "footer block found" if foot_ok else "no footer block found"))
        prep_ok = bool(re.search(r"(?i)prepared\s+(for|by)", text))
        out.append(Check("template", "prepared-by", "PASS" if prep_ok else "FAIL",
                         "prepared for/by line found" if prep_ok else "no prepared for/by line"))
    elif ext == ".md":
        text = path.read_text(encoding="utf-8", errors="replace")
        head = "\n".join(text.splitlines()[:30])
        title_ok = bool(re.search(r"(?m)^# \S", head))
        out.append(Check("template", "header", "PASS" if title_ok else "FAIL",
                         "title header found" if title_ok else "no # title in first 30 lines"))
        prep_ok = bool(re.search(r"(?i)prepared\s+(for|by)", text))
        out.append(Check("template", "prepared-by", "PASS" if prep_ok else "FAIL",
                         "prepared for/by line found" if prep_ok else "no prepared for/by line"))
        date_ok = bool(_ISO_DATE_RE.search(head) or _LONG_DATE_RE.search(head))
        out.append(Check("template", "date-line", "PASS" if date_ok else "FAIL",
                         "date present near the top" if date_ok else "no date in first 30 lines"))
    elif ext in OFFICE_EXTS:
        out.append(font_check(_read_text(path) or "", "the document styles"))
        out.append(Check("template", "layout", "SKIP",
                         "binary layout (logo, footer, signature) - the reading pass judges this"))
    elif ext == ".pdf":
        out.append(Check("template", "layout", "SKIP",
                         "PDF internals are compressed - the reading pass judges template fit"))
    else:
        out.append(Check("template", "type", "SKIP",
                         f"no deterministic template rules for {ext or 'no extension'}"))
    return out


# ------------------------------------------------------------ placeholders --

def check_placeholders(path: Path) -> list[Check]:
    text = _read_text(path)
    if text is None:
        return [Check("placeholders", "scan", "SKIP", "unscannable format - the reading pass judges")]
    hits: list[str] = []
    for label, rx in _PLACEHOLDER_RES:
        found = rx.findall(text)
        if found:
            first_line = next((i + 1 for i, l in enumerate(text.splitlines()) if rx.search(l)), 0)
            hits.append(f"{label} x{len(found)} (first at line {first_line})")
    if hits:
        return [Check("placeholders", "scan", "FAIL", "; ".join(hits))]
    return [Check("placeholders", "scan", "PASS", "no placeholder or unresolved markers")]


# -------------------------------------------------------------------- date --

def _found_dates(text: str) -> list[_dt.date]:
    out = []
    for y, m, d in _ISO_DATE_RE.findall(text):
        try:
            out.append(_dt.date(int(y), int(m), int(d)))
        except ValueError:
            pass
    for g in _LONG_DATE_RE.findall(text):
        try:
            if g[0]:
                out.append(_dt.date(int(g[2]), MONTHS.index(g[1].capitalize()) + 1, int(g[0])))
            else:
                out.append(_dt.date(int(g[5]), MONTHS.index(g[3].capitalize()) + 1, int(g[4])))
        except ValueError:
            pass
    return out


def check_date(path: Path, asof: _dt.date) -> list[Check]:
    """A current deliverable carries at least one date within 48h of sending: its
    prep stamp. Future dates (a payment schedule, a milestone) are legitimate
    content and must not fail this, so the rule is ANY date near asof, never the
    newest date in the file."""
    text = _read_text(path) or ""
    dates = _found_dates(path.name) + _found_dates(text)
    if not dates:
        return [Check("date", "within-48h", "FAIL", "no date found in filename or content")]
    nearest = min(dates, key=lambda d: abs((asof - d).days))
    delta = abs((asof - nearest).days)
    if delta <= 2:
        return [Check("date", "within-48h", "PASS",
                      f"date {nearest.isoformat()} is {delta}d from {asof.isoformat()}")]
    return [Check("date", "within-48h", "FAIL",
                  f"nearest date {nearest.isoformat()} is {delta}d from {asof.isoformat()} - "
                  f"no prep-stamp date within 48h, so this is stale or misdated")]


# ------------------------------------------------------------- attribution --

def check_attribution(path: Path, cfg: dict) -> list[Check]:
    out: list[Check] = []
    text = _read_text(path)
    if text is None:
        out.append(Check("attribution", "strings", "SKIP", "unscannable format"))
    else:
        hits = sorted({rx.pattern for rx in _ATTRIBUTION_RES if rx.search(text)})
        if hits:
            out.append(Check("attribution", "strings", "FAIL",
                             f"attribution-shaped strings: {len(hits)} pattern(s) hit"))
        else:
            out.append(Check("attribution", "strings", "PASS", "no AI-attribution strings"))
    if path.suffix.lower() in OFFICE_EXTS:
        expected = cfg.get("brand.document_author")
        if not expected:
            out.append(Check("attribution", "author", "SKIP",
                             "no brand.document_author in os-config.yaml - set one to check this"))
            return out
        creator = last_mod = ""
        try:
            with zipfile.ZipFile(path) as z:
                core = z.read("docProps/core.xml").decode("utf-8", errors="replace")
            m = re.search(r"<dc:creator>([^<]*)</dc:creator>", core)
            creator = (m.group(1) if m else "").strip()
            m = re.search(r"<cp:lastModifiedBy>([^<]*)</cp:lastModifiedBy>", core)
            last_mod = (m.group(1) if m else "").strip()
        except (KeyError, zipfile.BadZipFile, OSError):
            out.append(Check("attribution", "author", "SKIP", "no readable docProps/core.xml"))
            return out
        if creator == expected:
            out.append(Check("attribution", "author", "PASS", f"author metadata is {expected}"))
        else:
            out.append(Check("attribution", "author", "FAIL",
                             f"author is '{creator or 'empty'}' (last modified by "
                             f"'{last_mod or 'empty'}') - it should be {expected}"))
    return out


# ---------------------------------------------------------------- evidence --

def check_evidence(path: Path, root: Path, log_tail_lines: int = 100) -> list[Check]:
    """Did a blind-spot pass actually happen for THIS file? Two forms of proof:
    a memo somewhere in your files that names the deliverable, or a recent
    brain/log.md entry naming it alongside blind-spot language. Absence is a
    FAIL, not a warning: shipping without the second pass is the failure this
    whole gate exists to catch."""
    out: list[Check] = []
    base = path.name

    memo_hit = None
    for top in ("clients", "brain", "drafts"):
        d = root / top
        if not d.is_dir():
            continue
        for f in d.rglob("*.md"):
            if "blind" not in f.name.lower():
                continue
            try:
                if base in f.read_text(encoding="utf-8", errors="replace"):
                    memo_hit = f
                    break
            except OSError:
                continue
        if memo_hit:
            break

    log_hit = False
    log_path = root / "brain" / "log.md"
    if log_path.exists():
        try:
            tail = "\n".join(log_path.read_text(encoding="utf-8", errors="replace")
                             .splitlines()[-log_tail_lines:])
        except OSError:
            tail = ""
        if base in tail and re.search(r"(?i)blind[- ]spot|second pass", tail):
            log_hit = True

    if memo_hit:
        rel = memo_hit.relative_to(root) if memo_hit.is_relative_to(root) else memo_hit
        out.append(Check("evidence", "blind-spot", "PASS", f"memo {rel} names {base}"))
    elif log_hit:
        out.append(Check("evidence", "blind-spot", "PASS",
                         f"brain/log.md names {base} with blind-spot language"))
    else:
        out.append(Check("evidence", "blind-spot", "FAIL",
                         f"nothing on record shows a blind-spot pass for {base} - "
                         f"run blind-spot-review first"))
    return out


# --------------------------------------------------------------------- CLI --

def run_verb(verb: str, path: Path, root: Path, asof: _dt.date, cfg: dict) -> list[Check]:
    if verb == "template":
        return check_template(path, cfg)
    if verb == "placeholders":
        return check_placeholders(path)
    if verb == "date":
        return check_date(path, asof)
    if verb == "attribution":
        return check_attribution(path, cfg)
    if verb == "evidence":
        return check_evidence(path, root)
    raise SystemExit(f"unknown verb {verb}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Deterministic floor under the ship-deliverable gate. Read-only.")
    p.add_argument("verb", choices=["template", "placeholders", "date", "attribution",
                                    "evidence", "all"])
    p.add_argument("path", help="path to the deliverable")
    p.add_argument("--root", default=None, help="OS root override (for tests)")
    p.add_argument("--asof", default=None, help="YYYY-MM-DD (default today) for the 48h date check")
    args = p.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        print(f"deliverable_gate: no file at {path}", file=sys.stderr)
        return 1
    root = Path(args.root) if args.root else REPO_ROOT
    asof = _dt.date.fromisoformat(args.asof) if args.asof else _dt.date.today()
    cfg = read_os_config(root)

    verbs = (["template", "placeholders", "date", "attribution", "evidence"]
             if args.verb == "all" else [args.verb])
    checks: list[Check] = []
    for v in verbs:
        checks.extend(run_verb(v, path, root, asof, cfg))
    for c in checks:
        print(c.line())
    fails = sum(1 for c in checks if c.status == "FAIL")
    skips = sum(1 for c in checks if c.status == "SKIP")
    print(f"deliverable-gate: {'FAIL' if fails else 'PASS'} "
          f"({len(checks)} checks, {fails} fail, {skips} left to the reading pass)")
    return 2 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
