#!/usr/bin/env python3
"""agent_runs.py - the run log a job writes about itself.

The problem it exists for: the org chart in roles/employees.yaml has a
`run_record_source` field, and until now it held prose naming a place. Nothing
wrote there. So the only record of a job running was you noticing it and typing
a verdict, which means the verdict ledger is a sample of the runs you happened
to watch. A run nobody watched left no trace at all, and `employee-review` read
that biased sample as if it were the record.

This is the cheapest possible fix, and it inverts who does the remembering: the
job writes one line when it finishes. What it read, what it produced, how it
ended, and what it could not do. You stop being the recording device.

What this is NOT: analytics, a timer, or a quality score. A run line says a run
happened and what came out of it. Whether the output was any good is still a
human verdict (scripts/employee_verdict.py) - and the two together are what let
a review say "this seat ran fourteen times, you saw three, here are the other
eleven" instead of building a performance story out of a job description.

Doctrine: rules/digital-employees.md. Registry: roles/employees.yaml.

Subcommands, standard library only, ASCII-safe output:

  record    Append one run line. Append-only, never rewrites a line.
  list      Print runs (all, or --seat <id>), newest last.
  summary   Per seat: run count, last run, outcome split, unwatched-run count.
  archive   Roll runs older than 90 days into brain/archive/, once the live log
            passes 1000 lines.

Row shape:
  {
    "ts": "2026-08-05T19:40:11", "run_id": "a1b2c3d4e5f6",
    "seat": "daily-assistant",
    "trigger": "morning loop, asked by hand",
    "read": ["brain/needs-attention.md", "cadence/queue.md"],
    "produced": ["brain/log.md#morning-loop-2026-08-05"],
    "outcome": "ok",              # ok | refused | failed
    "could_not": "the queue file was missing so nothing was scored"
  }

The run_id is what ties a verdict to a specific run: grade one with
`python scripts/employee_verdict.py record ... --ref run:<run_id>`, and the
summary's unwatched count then reflects which runs a verdict actually names
instead of subtracting per-seat totals (runs recorded before run_id existed
count as unwatched until a verdict names them).

`refused` is a first-class outcome, not a failure. A propose-only job that
declined to act because the charter said no is the charter working, and a log
that cannot say that would push every honest refusal into the failed bucket.

Invariants: single writer for the run log (nothing else appends to it),
append-only, standard library only, no network, no API key. No personal data by
rule - a run line holds seat ids, file paths, and one plain sentence, never an
email address, a phone number, or a money amount. `record` refuses input that
looks like one of those rather than storing it.

Usage:
  python scripts/agent_runs.py record --seat daily-assistant \\
      --trigger "morning loop" --read "brain/needs-attention.md,cadence/queue.md" \\
      --produced "brain/log.md" --outcome ok
  python scripts/agent_runs.py record --seat next-move-caller --trigger "what next" \\
      --outcome refused --could-not "no customer in the snapshot, asked for it instead"
  python scripts/agent_runs.py list --seat daily-assistant
  python scripts/agent_runs.py summary
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "roles" / "employees.yaml"
RUNS = REPO_ROOT / "brain" / "agent-runs.jsonl"
VERDICTS = REPO_ROOT / "brain" / "employee-verdicts.jsonl"
ARCHIVE_DIR = REPO_ROOT / "brain" / "archive"

VALID_OUTCOMES = ("ok", "refused", "failed")
ARCHIVE_THRESHOLD_LINES = 1000
ARCHIVE_AGE_DAYS = 90

# No personal data and no money in a run line, by rule. Same shape of guard as
# the provisional-fact ledger, and for the same reason: these files get read
# back months later by something that will treat every field as safe to quote.
# Dates come out of the text before the phone test runs, because an ISO date is
# a phone number's exact shape.
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_DATE_RE = re.compile(r"\b\d{4}-\d{1,2}-\d{1,2}\b|\b\d{1,2}[/.]\d{1,2}[/.]\d{2,4}\b")
_PHONE_RE = re.compile(r"(?:\d[ \-]?){7,}\d")
_MONEY_RE = re.compile(
    r"\b[A-Z]{3}\s?\d{2,}"
    r"|(?<!\d)(?!(?:19|20)\d\d\b)\d[\d,.]*\s?[A-Z]{3}\b"
    r"|[$£€¥]\s*\d")


def _reject_personal(label: str, text: str) -> None:
    if not text:
        return
    if _EMAIL_RE.search(text):
        raise SystemExit(f"agent_runs: {label} looks like it holds an email address. "
                         f"A run line is a seat id, a path, and a plain sentence.")
    if _MONEY_RE.search(text):
        raise SystemExit(f"agent_runs: {label} looks like it holds a money amount. "
                         f"Commercial terms never go in the run log.")
    if _PHONE_RE.search(_DATE_RE.sub(" ", text)):
        raise SystemExit(f"agent_runs: {label} looks like it holds a phone number. "
                         f"A run line is a seat id, a path, and a plain sentence.")


# ----- registry -----

def _flat_yaml():
    """Load scripts/flat_yaml.py by explicit path rather than by import name, so
    this works the same whether or not scripts/ is on sys.path."""
    src = Path(__file__).resolve().parent / "flat_yaml.py"
    spec = importlib.util.spec_from_file_location("founderos_flat_yaml", src)
    if spec is None or spec.loader is None:  # pragma: no cover - packaging accident
        raise SystemExit("agent_runs: cannot load scripts/flat_yaml.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def registry_ids(path: Path) -> set[str] | None:
    """Seat ids from the org chart, or None when there is no chart to check
    against. A missing registry is not an error here: an install with no org
    chart can still record runs, and refusing to would make the log depend on a
    file it does not need."""
    if not path.exists():
        return None
    try:
        rows = _flat_yaml().parse_flat_yaml(
            path.read_text(encoding="utf-8"),
            filename=str(path), record_key="employees")
    except ValueError as e:
        raise SystemExit(f"agent_runs: {e}") from None
    return {r["id"] for r in rows if r.get("id")}


# ----- read / write -----

def read_runs(path: Path | None = None) -> list[dict]:
    path = path or RUNS
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # one bad line never breaks the loop; the file is append-only
    return out


def _split_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def append_run(seat: str, trigger: str, read: list[str], produced: list[str],
               outcome: str, could_not: str | None,
               path: Path = RUNS, now: _dt.datetime | None = None) -> dict:
    ts = (now or _dt.datetime.now()).isoformat(timespec="seconds")
    # A stable id per run, so a verdict can point at THIS run (--ref run:<id>)
    # and the unwatched count can match runs to verdicts instead of guessing
    # from per-seat totals. Derived, not random, and salted with the log's
    # current length so two identical triggers in the same second still get
    # two ids - a collision would let one verdict vouch for both runs.
    n = 0
    if path.exists():
        n = sum(1 for l in path.read_text(encoding="utf-8").splitlines() if l.strip())
    run_id = hashlib.sha256(
        f"{seat}|{ts}|{trigger}|{n}".encode("utf-8")).hexdigest()[:12]
    rec: dict = {
        "ts": ts,
        "run_id": run_id,
        "seat": seat,
        "trigger": trigger,
        "read": read,
        "produced": produced,
        "outcome": outcome,
    }
    if could_not:
        rec["could_not"] = could_not
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=True) + "\n")
    return rec


def cmd_record(args) -> int:
    ids = registry_ids(Path(args.registry))
    if ids is not None and args.seat not in ids:
        known = ", ".join(sorted(ids)) or "(the registry has no rows)"
        raise SystemExit(f"agent_runs: unknown seat '{args.seat}'. Known: {known}")
    if args.outcome not in VALID_OUTCOMES:
        raise SystemExit(f"agent_runs: outcome must be one of {VALID_OUTCOMES}")
    trigger = (args.trigger or "").strip()
    if not trigger:
        raise SystemExit("agent_runs: --trigger is required - one line on what set this run "
                         "off. A run with no trigger cannot be told apart from a test.")
    could_not = (args.could_not or "").strip()
    if args.outcome in ("refused", "failed") and not could_not:
        raise SystemExit(f"agent_runs: --could-not is required when the outcome is "
                         f"'{args.outcome}'. A refusal or a failure with no reason teaches "
                         f"nothing at review time.")
    for label, text in (("--trigger", trigger), ("--could-not", could_not),
                        ("--produced", args.produced or ""), ("--read", args.read or "")):
        _reject_personal(label, text)
    if "\n" in trigger or "\n" in could_not:
        raise SystemExit("agent_runs: --trigger and --could-not are one line each.")
    rec = append_run(args.seat, trigger, _split_list(args.read), _split_list(args.produced),
                     args.outcome, could_not or None, Path(args.file))
    print(f"recorded: {rec['seat']} {rec['outcome']} ({rec['ts']})")
    return 0


def cmd_list(args) -> int:
    runs = read_runs(Path(args.file))
    if args.seat:
        runs = [r for r in runs if r.get("seat") == args.seat]
    if args.json:
        print(json.dumps({"count": len(runs), "runs": runs[-args.last:]}, ensure_ascii=True))
        return 0
    for r in runs[-args.last:]:
        produced = ", ".join(r.get("produced") or []) or "-"
        tail = f"  could not: {r['could_not']}" if r.get("could_not") else ""
        rid = r.get("run_id", "-")
        print(f"{r.get('ts', '?')}  {rid:12}  {r.get('seat', '?'):18} "
              f"{r.get('outcome', '?'):8} {r.get('trigger', '')} -> {produced}{tail}")
    if not runs:
        print("no runs recorded")
    return 0


# ----- summary -----

def _parse_ts(ts: str) -> _dt.datetime | None:
    try:
        return _dt.datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def read_verdicts(path: Path) -> dict[str, dict]:
    """Per seat: how many verdicts exist, and which run ids they reference
    (a verdict recorded with --ref run:<run_id>). Used to say how many runs
    went unwatched - by MATCHING verdicts to runs, not by subtracting totals,
    because old, duplicate, or queue-level verdicts would otherwise mark
    unreviewed runs as watched."""
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        seat = rec.get("employee")
        if not seat:
            continue
        entry = out.setdefault(seat, {"count": 0, "run_refs": []})
        entry["count"] += 1
        ref = (rec.get("ref") or "").strip()
        if ref.startswith("run:"):
            entry["run_refs"].append(ref[4:])
    return out


def summarise(runs: list[dict], verdicts: dict[str, dict]) -> list[dict]:
    by_seat: dict[str, list[dict]] = {}
    for r in runs:
        by_seat.setdefault(r.get("seat", "?"), []).append(r)
    out: list[dict] = []
    for seat in sorted(by_seat):
        rows = by_seat[seat]
        outcomes: dict[str, int] = {}
        for r in rows:
            key = r.get("outcome", "?")
            outcomes[key] = outcomes.get(key, 0) + 1
        last = max((r.get("ts", "") for r in rows), default="")
        v = verdicts.get(seat, {"count": 0, "run_refs": []})
        run_ids = {r["run_id"] for r in rows if r.get("run_id")}
        watched_ids = run_ids & set(v["run_refs"])
        matched_verdicts = sum(1 for ref in v["run_refs"] if ref in run_ids)
        out.append({
            "seat": seat,
            "runs": len(rows),
            "last_run": last,
            "outcomes": outcomes,
            "verdicts": v["count"],
            # A run counts as watched only when a verdict names it by run id
            # (--ref run:<id>). Verdicts with no run ref (queue-level, legacy)
            # still count as verdicts, but they cannot vouch for any particular
            # run - which is exactly the sampling bias this number exists to
            # make visible.
            "unwatched": len(rows) - len(watched_ids),
            "unmatched_verdicts": v["count"] - matched_verdicts,
        })
    return out


def cmd_summary(args) -> int:
    runs = read_runs(Path(args.file))
    verdicts = read_verdicts(Path(args.verdicts))
    rows = summarise(runs, verdicts)
    if args.json:
        print(json.dumps({"count": len(rows), "seats": rows}, ensure_ascii=True))
        return 0
    if not rows:
        print("summary: no runs recorded yet. A seat that has never run has nothing to "
              "review, which is the honest starting state.")
        return 0
    for r in rows:
        split = ", ".join(f"{k} {v}" for k, v in sorted(r["outcomes"].items()))
        print(f"{r['seat']:18} runs {r['runs']:4}  last {r['last_run'][:10] or '?':10}  "
              f"{split}")
        if r["unwatched"]:
            aside = (f" ({r['unmatched_verdicts']} verdict(s) name no run)"
                     if r["unmatched_verdicts"] else "")
            print(f"{'':18} no verdict names {r['unwatched']} of them - "
                  f"grade one with employee_verdict.py record --ref run:<id>{aside}")
    return 0


# ----- archive -----

def cmd_archive(args) -> int:
    path = Path(args.file)
    if not path.exists():
        print("archive: no run log - nothing to do")
        return 0
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(lines) <= args.threshold and not args.force:
        print(f"archive: {len(lines)} lines, threshold {args.threshold} - nothing to do")
        return 0
    asof = _dt.date.fromisoformat(args.asof) if args.asof else _dt.date.today()
    cutoff = asof - _dt.timedelta(days=ARCHIVE_AGE_DAYS)
    keep: list[str] = []
    roll: dict[str, list[str]] = {}
    for l in lines:
        d = None
        try:
            d = _parse_ts(json.loads(l).get("ts", ""))
        except json.JSONDecodeError:
            pass
        if d is None or d.date() >= cutoff:
            keep.append(l)  # fresh or unparseable lines never leave the live log
        else:
            roll.setdefault(d.strftime("%Y-%m"), []).append(l)
    if not roll:
        print(f"archive: over threshold but nothing older than {ARCHIVE_AGE_DAYS}d - "
              f"nothing to roll")
        return 0
    arch_dir = Path(args.archive_dir)
    arch_dir.mkdir(parents=True, exist_ok=True)
    for month, rows in sorted(roll.items()):
        with (arch_dir / f"agent-runs-{month}.jsonl").open(
                "a", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(r + "\n")
    path.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8", newline="\n")
    rolled = sum(len(v) for v in roll.values())
    print(f"archive: rolled {rolled} runs older than {ARCHIVE_AGE_DAYS}d into {arch_dir} "
          f"({len(keep)} kept live)")
    return 0


# ----- cli -----

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="The run log for digital employees (rules/digital-employees.md).")
    sub = p.add_subparsers(dest="cmd", required=True)

    common_file = dict(default=str(RUNS), help="path to brain/agent-runs.jsonl")

    pr = sub.add_parser("record", help="Append one run line. The job's closing act.")
    pr.add_argument("--seat", required=True, help="the roles/employees.yaml id")
    pr.add_argument("--trigger", required=True, help="one line on what set this run off")
    pr.add_argument("--read", default="", help="comma-separated paths it actually read")
    pr.add_argument("--produced", default="", help="comma-separated files or item ids it wrote")
    pr.add_argument("--outcome", required=True, choices=list(VALID_OUTCOMES))
    pr.add_argument("--could-not", dest="could_not", default="",
                    help="one line on what it could not do (required on refused/failed)")
    pr.add_argument("--registry", default=str(REGISTRY))
    pr.add_argument("--file", **common_file)
    pr.set_defaults(func=cmd_record)

    pl = sub.add_parser("list", help="Print runs, newest last.")
    pl.add_argument("--seat", default=None)
    pl.add_argument("--last", type=int, default=50)
    pl.add_argument("--json", action="store_true")
    pl.add_argument("--file", **common_file)
    pl.set_defaults(func=cmd_list)

    ps = sub.add_parser("summary", help="Per seat: runs, last run, outcomes, unwatched count.")
    ps.add_argument("--json", action="store_true")
    ps.add_argument("--file", **common_file)
    ps.add_argument("--verdicts", default=str(VERDICTS))
    ps.set_defaults(func=cmd_summary)

    pa = sub.add_parser("archive", help="Roll old runs out of the live log.")
    pa.add_argument("--file", **common_file)
    pa.add_argument("--archive-dir", dest="archive_dir", default=str(ARCHIVE_DIR))
    pa.add_argument("--threshold", type=int, default=ARCHIVE_THRESHOLD_LINES)
    pa.add_argument("--force", action="store_true", help="roll even below the threshold")
    pa.add_argument("--asof", default=None)
    pa.set_defaults(func=cmd_archive)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
