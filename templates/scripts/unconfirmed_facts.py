#!/usr/bin/env python3
"""unconfirmed_facts.py - the ledger for things you heard once and cannot verify yet.

The problem it exists for: you have one recording of a call, and in it someone
mentions a company name, a surname, or a number you never saw written down. That
detail is now in your notes reading exactly like a fact. Two weeks later it gets
copied into a document, and nobody can say where it came from. A name heard once
is provisional, and the only thing that resolves it is a second source or you
confirming it - never a better transcript, because the information was never in
the audio to begin with.

So provisional details get their own place to wait. This ledger holds the
question, never the answer. `confirm` records the real value and points at the
file that should carry it. Writing it into that file stays your step, deliberately.

Nothing here is a fact until it is confirmed. That is the whole point.

Invariants: single writer for the ledger file (nothing else appends to it),
standard library only, no network, no API key, and no personal data by rule - a
name or a short claim, never an email, a phone number, or a money amount. `add`
refuses input that looks like one of those rather than storing it.

Row shape:
  {
    "id": "uf-2026-07-25-001", "created": "2026-07-25",
    "fact": "the company may be called <name>",
    "context": "said once in Tuesday's call, never spelled out",
    "source": "recorder | handoff | capture | brief | manual",
    "owning_file": "context/clients.md",   # where a confirmed value belongs
    "entity": "acme-co",                   # who or what it is about (optional)
    "status": "open|confirmed|cut",
    "value": null,                         # the confirmed value, set by confirm
    "resolution": null,                    # one-line why, set by confirm or cut
    "created_ts": "...", "resolved_ts": null
  }

Usage:
  python scripts/unconfirmed_facts.py add --fact "the company may be called Acme" \\
      --context "said once on the call, never spelled out" --source recorder \\
      --owning-file context/clients.md --entity acme --dedup-key acme-name
  python scripts/unconfirmed_facts.py list [--status open] [--json]
  python scripts/unconfirmed_facts.py confirm --id uf-2026-07-25-001 \\
      --value "Acme Holdings" --note "confirmed by email"
  python scripts/unconfirmed_facts.py cut --id uf-2026-07-25-001 --note "never a real name"
  python scripts/unconfirmed_facts.py render
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STORE = REPO_ROOT / "brain" / "unconfirmed-facts.jsonl"
VIEW = REPO_ROOT / "brain" / "unconfirmed-facts.md"

VALID_STATUS = ["open", "confirmed", "cut"]
TERMINAL = {"confirmed", "cut"}

# No personal data and no money in a fact, by rule. The guard catches an email, a
# phone-length run of digits, and a number sitting next to a currency. It does NOT
# reject a bare number: a year ("the 2026 cohort"), a count ("25 people"), or a date
# is exactly the kind of claim this ledger exists to hold. Two exclusions are what
# make that true rather than merely intended:
#   - Dates come out of the text before the phone test runs. "2026-07-25" is eight
#     digits joined by hyphens, which is a phone number's exact shape.
#   - A year is excluded from the money test. "the 2026 CEO" and "the 2024 KPI" are
#     claims about a person and a target, not amounts. The cost of that exclusion is
#     that a bare "2000 USD" reads as a year and gets through - write it "USD 2000".
# Currency is matched generically (any three-letter code, or a symbol) so no market
# is special.
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_DATE_RE = re.compile(r"\b\d{4}-\d{1,2}-\d{1,2}\b|\b\d{1,2}[/.]\d{1,2}[/.]\d{2,4}\b")
_PHONE_RE = re.compile(r"(?:\d[ \-]?){7,}\d")
_MONEY_RE = re.compile(
    r"\b[A-Z]{3}\s?\d{2,}"                                # currency code, then the number
    r"|(?<!\d)(?!(?:19|20)\d\d\b)\d[\d,.]*\s?[A-Z]{3}\b"  # the number, then the code
    r"|(?<!\d)\d[\d,.]*\s?[km]\b"                         # shorthand: 500k, 2m
    r"|[$£€¥]\s*\d")                                      # a currency symbol


def _today(override: str | None = None) -> _dt.date:
    return _dt.date.fromisoformat(override) if override else _dt.date.today()


def _stamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def _now_iso() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


# ----- read / write -----

def read_rows(path: Path | None = None) -> list[dict]:
    path = path or STORE
    if not path.exists():
        return []
    rows: list[dict] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            rows.append(json.loads(raw))
        except json.JSONDecodeError as e:
            print(f"unconfirmed_facts: skipping malformed line {i}: {e}", file=sys.stderr)
    return rows


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def write_rows(rows: list[dict], path: Path | None = None) -> None:
    path = path or STORE
    lines = [json.dumps(r, ensure_ascii=False) for r in rows]
    _atomic_write(path, "\n".join(lines) + ("\n" if lines else ""))


def append_row(row: dict, path: Path | None = None) -> None:
    path = path or STORE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _next_id(rows: list[dict], created: str) -> str:
    prefix = f"uf-{created}-"
    nums = []
    for r in rows:
        rid = r.get("id", "")
        if isinstance(rid, str) and rid.startswith(prefix):
            tail = rid[len(prefix):]
            if tail.isdigit():
                nums.append(int(tail))
    return f"{prefix}{(max(nums) + 1) if nums else 1:03d}"


def _pii_reason(text: str) -> str | None:
    t = text or ""
    if _EMAIL_RE.search(t):
        return "looks like an email address"
    if _PHONE_RE.search(_DATE_RE.sub(" ", t)):
        return "looks like a phone number (a long run of digits)"
    if _MONEY_RE.search(t):
        return "looks like a money amount (a number next to a currency)"
    return None


# ----- render -----

def render_md(rows: list[dict]) -> str:
    out: list[str] = []
    out.append(f"<!-- refreshed: {_stamp()} -->")
    out.append("<!-- generated by: python scripts/unconfirmed_facts.py render -->")
    out.append("")
    out.append("# Unconfirmed facts")
    out.append("")
    out.append("Every provisional name or claim waiting to be confirmed or cut. A confirm "
               "records the value and names the file that should carry it - writing it into "
               "that file stays your step. Nothing on this page is a fact until it is "
               "confirmed.")
    out.append("")
    open_rows = [r for r in rows if r.get("status") == "open"]
    resolved = [r for r in rows if r.get("status") in TERMINAL]
    out.append(f"{len(open_rows)} open, {len(resolved)} resolved, {len(rows)} total.")
    out.append("")
    if not rows:
        out.append("_Nothing logged. Nothing is waiting._")
        return "\n".join(out) + "\n"

    out.append("## Open - waiting on a confirm or a cut")
    out.append("")
    if not open_rows:
        out.append("_None. Everything logged has been resolved._")
        out.append("")
    for r in sorted(open_rows, key=lambda r: r.get("id", "")):
        ent = f", about {r['entity']}" if r.get("entity") else ""
        out.append(f"- `{r.get('id', '?')}` {r.get('fact', '(no fact)')}  "
                   f"(source {r.get('source', '?')}{ent})")
        if r.get("context"):
            out.append(f"    - context: {r['context']}")
        if r.get("owning_file"):
            out.append(f"    - lands in: {r['owning_file']}")

    out.append("")
    out.append("## Resolved")
    out.append("")
    if not resolved:
        out.append("_None yet._")
    for r in sorted(resolved, key=lambda r: r.get("resolved_ts") or ""):
        if r.get("status") == "confirmed":
            verb = f"CONFIRMED as \"{r.get('value', '')}\""
        else:
            verb = "CUT"
        note = f" - {r['resolution']}" if r.get("resolution") else ""
        out.append(f"- `{r.get('id', '?')}` {r.get('fact', '')} -> {verb}{note}")
    return "\n".join(out).rstrip() + "\n"


def do_render(rows: list[dict] | None = None) -> None:
    _atomic_write(VIEW, render_md(rows if rows is not None else read_rows()))


# ----- commands -----

def cmd_add(args) -> int:
    for field, val in (("--fact", args.fact), ("--context", args.context or "")):
        reason = _pii_reason(val)
        if reason:
            print(f"unconfirmed_facts add: {field} {reason} - this ledger holds names and "
                  f"claims, never personal data or money. Rephrase around it.", file=sys.stderr)
            return 1

    rows = read_rows()
    if args.dedup_key:
        for r in rows:
            if r.get("dedup_key") == args.dedup_key:
                print(f"SKIP duplicate: dedup-key {args.dedup_key} is already logged as {r.get('id')}.")
                return 0

    created = _today(args.today).isoformat()
    row = {
        "id": _next_id(rows, created),
        "created": created,
        "fact": args.fact.strip(),
        "context": (args.context or "").strip(),
        "source": args.source,
        "owning_file": (args.owning_file or "").strip() or None,
        "entity": (args.entity or "").strip().lower() or None,
        "dedup_key": (args.dedup_key or "").strip() or None,
        "status": "open",
        "value": None,
        "resolution": None,
        "created_ts": _now_iso(),
        "resolved_ts": None,
    }
    append_row(row)
    do_render()
    print(json.dumps(row, ensure_ascii=False))
    return 0


def _resolve(args, status: str, value: str | None) -> int:
    rows = read_rows()
    hit = next((r for r in rows if r.get("id") == args.id), None)
    if hit is None:
        print(f"unconfirmed_facts {status}: no row with id {args.id}", file=sys.stderr)
        return 1
    if hit.get("status") in TERMINAL:
        print(f"unconfirmed_facts {status}: {args.id} is already {hit['status']}. Reopening is "
              f"a manual edit - the ledger never silently flips a resolved row.", file=sys.stderr)
        return 1
    hit["status"] = status
    hit["value"] = value
    hit["resolution"] = (getattr(args, "note", None) or "").strip() or None
    hit["resolved_ts"] = _now_iso()
    write_rows(rows)
    do_render(rows)
    tail = f" as \"{value}\"" if value else ""
    landing = (f"  ->  now write it into {hit['owning_file']}"
               if (status == "confirmed" and hit.get("owning_file")) else "")
    print(f"{args.id}: {status}{tail}{landing}")
    return 0


def cmd_confirm(args) -> int:
    if not (args.value or "").strip():
        print("unconfirmed_facts confirm: --value is required (the confirmed value).", file=sys.stderr)
        return 1
    return _resolve(args, "confirmed", args.value.strip())


def cmd_cut(args) -> int:
    return _resolve(args, "cut", None)


def cmd_list(args) -> int:
    rows = read_rows()
    if args.status:
        rows = [r for r in rows if r.get("status") == args.status]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False))
        return 0
    if not rows:
        print("(nothing waiting)")
        return 0
    for r in sorted(rows, key=lambda r: r.get("id", "")):
        ent = f" [{r['entity']}]" if r.get("entity") else ""
        print(f"{r.get('id', '?')}  ({r.get('status', '?')}){ent}  {r.get('fact', '')}")
    return 0


def cmd_render(args) -> int:
    do_render()
    print(f"Rendered {VIEW.name} from {len(read_rows())} rows.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="The ledger for things heard once: confirm or cut before anything hardens.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add", help="Log a provisional fact (no personal data, no money).")
    pa.add_argument("--fact", required=True, help="the provisional claim, one line")
    pa.add_argument("--context", default=None, help="why it is provisional, and where it came from")
    pa.add_argument("--source", required=True, help="recorder | handoff | capture | brief | manual")
    pa.add_argument("--owning-file", dest="owning_file", default=None,
                    help="the file a confirmed value should land in")
    pa.add_argument("--entity", default=None, help="who or what it is about (a short slug)")
    pa.add_argument("--dedup-key", dest="dedup_key", default=None,
                    help="a stable key so the same provisional is not logged twice")
    pa.add_argument("--today", default=None, help="override today's date (YYYY-MM-DD), for tests")
    pa.set_defaults(func=cmd_add)

    pc = sub.add_parser("confirm", help="Confirm a fact with its real value.")
    pc.add_argument("--id", required=True)
    pc.add_argument("--value", required=True, help="the confirmed value")
    pc.add_argument("--note", default=None, help="one line on who or what confirmed it")
    pc.set_defaults(func=cmd_confirm)

    pk = sub.add_parser("cut", help="Cut a fact that was never real.")
    pk.add_argument("--id", required=True)
    pk.add_argument("--note", default=None, help="one line on why it was cut")
    pk.set_defaults(func=cmd_cut)

    pl = sub.add_parser("list", help="List rows, optionally filtered by --status.")
    pl.add_argument("--status", default=None, choices=VALID_STATUS)
    pl.add_argument("--json", action="store_true")
    pl.set_defaults(func=cmd_list)

    prn = sub.add_parser("render", help="Rebuild the readable view from the ledger.")
    prn.set_defaults(func=cmd_render)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
