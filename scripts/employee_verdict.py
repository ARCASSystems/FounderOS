#!/usr/bin/env python3
"""employee_verdict.py - the performance loop for digital employees.

The problem it exists for: once the OS runs recurring jobs for you, there is no
record of whether any of them is actually any good. You notice a bad run, correct
it in the moment, and the correction lives nowhere. Six weeks later the same job
is still producing the same bad output, and nothing in the OS knows that.

This is the cheapest possible fix: one line per run you actually saw. ok,
needs-work, or failed, plus why. That ledger is the entire input to the review
that proposes changes to the job, and it is the only honest answer to "what is
this OS actually good at".

Doctrine: rules/digital-employees.md. Registry: roles/employees.yaml.

Subcommands, standard library only, ASCII-safe output:

  verdict   Append one verdict on a run. Append-only, never rewrites a line.
  list      Print verdicts (all, or --employee <id>), newest last.
  render    Write the org-chart view: per employee its job, last verdict,
            needs-work count, and whether a review is due. Zero LLM.
  archive   Roll entries older than 90 days into brain/archive/ - but only once
            the live ledger passes 500 lines, so no machinery runs ahead of need.
  drift     Cross-check every registry row against reality, and reality against
            the rows. Report-only.
  charters  Audit the charter of every row: a job with no tool grant, or one
            holding a grant wider than its job description claims. Report-only.

Review is due on exactly two triggers (the doctrine's performance loop):
  - 3 or more needs-work verdicts inside 30 days, or
  - monthly: a verdict exists newer than last_review, and last_review is null or
    30+ days old.
With zero verdicts nothing is ever due. A review with no evidence to read is not
a review, it is an invitation to invent a performance narrative.

Invariants: single writer for the verdicts ledger (nothing else appends to it),
append-only for verdicts, standard library only, no network, no API key. `drift`
and `charters` are report-only and never edit the registry - changes go through
the three registry doors in the doctrine (hire, review diff, retirement).

Usage:
  python scripts/employee_verdict.py verdict --employee follow-up-watcher \\
      --verdict needs-work --why "flagged a lead I had already replied to"
  python scripts/employee_verdict.py list --employee follow-up-watcher
  python scripts/employee_verdict.py render
  python scripts/employee_verdict.py drift --json
  python scripts/employee_verdict.py charters
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "roles" / "employees.yaml"
VERDICTS = REPO_ROOT / "brain" / "employee-verdicts.jsonl"
VIEW = REPO_ROOT / "brain" / "employees.md"
ARCHIVE_DIR = REPO_ROOT / "brain" / "archive"

VALID_VERDICTS = ("ok", "needs-work", "failed")
NEEDS_WORK_WINDOW_DAYS = 30
NEEDS_WORK_TRIGGER = 3
MONTHLY_DAYS = 30
ARCHIVE_THRESHOLD_LINES = 500
ARCHIVE_AGE_DAYS = 90


# ----- registry -----

def _flat_yaml():
    """Load scripts/flat_yaml.py by explicit path rather than by import name, so
    this works the same whether or not scripts/ is on sys.path."""
    src = Path(__file__).resolve().parent / "flat_yaml.py"
    spec = importlib.util.spec_from_file_location("founderos_flat_yaml", src)
    if spec is None or spec.loader is None:  # pragma: no cover - packaging accident
        raise SystemExit("employee_verdict: cannot load scripts/flat_yaml.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_registry(path: Path = REGISTRY) -> list[dict]:
    """The flat employees.yaml. A malformed line fails loud with the file and line
    number rather than dropping a field nobody notices is gone. An empty registry
    is valid and returns []; the shipped one carries five gated starter roles."""
    if not path.exists():
        raise SystemExit(
            f"employee_verdict: no registry at {path}. Copy it from "
            f"templates/roles/employees.yaml, which ships with five gated "
            f"starter roles - or write your own with `employees: []` in it.")
    try:
        employees = _flat_yaml().parse_flat_yaml(
            path.read_text(encoding="utf-8"),
            filename=str(path), record_key="employees")
    except ValueError as e:
        raise SystemExit(f"employee_verdict: {e}") from None
    for i, e in enumerate(employees, 1):
        if not e.get("id"):
            raise SystemExit(f"employee_verdict: registry entry #{i} has no id")
    ids = [e.get("id", "") for e in employees]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"employee_verdict: duplicate ids in registry: {sorted(dupes)}")
    return employees


def registry_ids(employees: list[dict]) -> set[str]:
    return {e["id"] for e in employees}


# ----- verdicts -----

def read_verdicts(path: Path = VERDICTS) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # one bad line never breaks the loop; the file is append-only
    return out


def append_verdict(employee: str, verdict: str, why: str, ref: str | None,
                   path: Path = VERDICTS, now: _dt.datetime | None = None) -> dict:
    rec = {
        "employee": employee,
        "ts": (now or _dt.datetime.now()).isoformat(timespec="seconds"),
        "verdict": verdict,
        "why": why,
    }
    if ref:
        rec["ref"] = ref
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=True) + "\n")
    return rec


def cmd_verdict(args) -> int:
    employees = parse_registry(Path(args.registry))
    if not employees:
        raise SystemExit(
            "employee_verdict: the registry is empty, so there is no job to grade. "
            "Add a row to roles/employees.yaml first (rules/digital-employees.md).")
    if args.employee not in registry_ids(employees):
        known = ", ".join(sorted(registry_ids(employees)))
        raise SystemExit(f"employee_verdict: unknown employee '{args.employee}'. Known: {known}")
    if args.verdict not in VALID_VERDICTS:
        raise SystemExit(f"employee_verdict: verdict must be one of {VALID_VERDICTS}")
    why = (args.why or "").strip()
    if not why:
        raise SystemExit("employee_verdict: --why is required - one line on what you saw. "
                         "A verdict with no why cannot feed a review.")
    if "\n" in why:
        raise SystemExit("employee_verdict: --why is one line, no newlines.")
    rec = append_verdict(args.employee, args.verdict, why, args.ref, Path(args.file))
    print(f"recorded: {rec['employee']} {rec['verdict']} ({rec['ts']})")
    return 0


def cmd_list(args) -> int:
    verdicts = read_verdicts(Path(args.file))
    if args.employee:
        verdicts = [v for v in verdicts if v.get("employee") == args.employee]
    for v in verdicts[-args.last:]:
        ref = f"  ref={v['ref']}" if v.get("ref") else ""
        print(f"{v.get('ts', '?')}  {v.get('employee', '?'):18} {v.get('verdict', '?'):10} "
              f"{v.get('why', '')}{ref}")
    if not verdicts:
        print("no verdicts recorded")
    return 0


# ----- render -----

def _parse_ts(ts: str) -> _dt.datetime | None:
    try:
        return _dt.datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def review_status(emp: dict, verdicts: list[dict], asof: _dt.date) -> tuple[str, int]:
    """Returns (review line, needs_work_in_window). Due on the two doctrine triggers
    only. With zero verdicts nothing is due."""
    mine = [v for v in verdicts if v.get("employee") == emp.get("id")]
    cutoff = asof - _dt.timedelta(days=NEEDS_WORK_WINDOW_DAYS)
    nw30 = 0
    newest: _dt.date | None = None
    for v in mine:
        ts = _parse_ts(v.get("ts", ""))
        if ts is None:
            continue
        d = ts.date()
        if d > asof:
            # A future-dated verdict is a typo, not evidence. Counting it would
            # trigger reviews off records that have not happened yet.
            continue
        if newest is None or d > newest:
            newest = d
        if v.get("verdict") == "needs-work" and d >= cutoff:
            nw30 += 1
    if nw30 >= NEEDS_WORK_TRIGGER:
        return (f"REVIEW DUE - {nw30} needs-work in {NEEDS_WORK_WINDOW_DAYS}d "
                f"(review {emp.get('id')})"), nw30
    last_review = (emp.get("last_review") or "").strip()
    lr_date = None
    if last_review and last_review.lower() != "null":
        try:
            lr_date = _dt.date.fromisoformat(last_review)
        except ValueError:
            lr_date = None
    if newest is not None:
        monthly_stale = lr_date is None or (asof - lr_date).days >= MONTHLY_DAYS
        unreviewed = lr_date is None or newest > lr_date
        if monthly_stale and unreviewed:
            return (f"review due (monthly) - verdicts newer than last_review "
                    f"(review {emp.get('id')})"), nw30
    return "no review due", nw30


def last_verdict_line(emp: dict, verdicts: list[dict]) -> str:
    mine = [v for v in verdicts if v.get("employee") == emp.get("id")]
    if not mine:
        return "none yet"
    v = mine[-1]
    return f"{v.get('verdict', '?')} ({v.get('ts', '?')[:10]}): {v.get('why', '')}"


def render_view(employees: list[dict], verdicts: list[dict], asof: _dt.date) -> str:
    lines = [
        "# Digital employees - org chart view",
        "",
        f"Rendered {asof.isoformat()} by scripts/employee_verdict.py render. Zero LLM.",
        "Registry: roles/employees.yaml. Doctrine: rules/digital-employees.md.",
        "",
        "Record a verdict after a run you actually saw:",
        "",
        "    python scripts/employee_verdict.py verdict --employee <id> \\",
        "        --verdict ok|needs-work|failed --why \"one line\"",
        "",
    ]
    if not employees:
        lines += [
            "## No digital employees yet",
            "",
            "The registry is empty, which is the honest starting state. Add your first row",
            "when a job has recurred three times and you have corrected it twice. That is",
            "the job worth writing down. See rules/digital-employees.md.",
            "",
        ]
        return "\n".join(lines)
    by_seat: dict[str, list[dict]] = {}
    for e in employees:
        by_seat.setdefault(e.get("seat", "unassigned"), []).append(e)
    for seat in sorted(by_seat):
        lines.append(f"## {seat}")
        lines.append("")
        for e in by_seat[seat]:
            review, nw30 = review_status(e, verdicts, asof)
            lines.append(f"### {e.get('id')} - {e.get('job_title', '?')} [{e.get('status', '?')}]")
            lines.append(f"- Job: {e.get('job_description', '?')}")
            lines.append(f"- Measure: {e.get('kpi', '?')}")
            lines.append(f"- Last verdict: {last_verdict_line(e, verdicts)}")
            if nw30:
                lines.append(f"- Needs-work last {NEEDS_WORK_WINDOW_DAYS}d: {nw30}")
            lines.append(f"- Review: {review}")
            lines.append("")
    return "\n".join(lines)


def cmd_render(args) -> int:
    employees = parse_registry(Path(args.registry))
    verdicts = read_verdicts(Path(args.file))
    asof = _dt.date.fromisoformat(args.asof) if args.asof else _dt.date.today()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_view(employees, verdicts, asof), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(employees)} employees, {len(verdicts)} verdicts)")
    return 0


# ----- archive -----

def cmd_archive(args) -> int:
    path = Path(args.file)
    if not path.exists():
        print("archive: no verdicts file - nothing to do")
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
            keep.append(l)  # fresh or unparseable lines never leave the live ledger
        else:
            roll.setdefault(d.strftime("%Y-%m"), []).append(l)
    if not roll:
        print(f"archive: over threshold but nothing older than {ARCHIVE_AGE_DAYS}d - nothing to roll")
        return 0
    arch_dir = Path(args.archive_dir)
    arch_dir.mkdir(parents=True, exist_ok=True)
    for month, rows in sorted(roll.items()):
        with (arch_dir / f"employee-verdicts-{month}.jsonl").open(
                "a", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(r + "\n")
    path.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8", newline="\n")
    rolled = sum(len(v) for v in roll.values())
    print(f"archive: rolled {rolled} entries older than {ARCHIVE_AGE_DAYS}d into "
          f"{arch_dir} ({len(keep)} kept live)")
    return 0


# ----- drift (report-only) -----

def registry_drift(root: Path) -> list[dict]:
    """Every row checked against reality, and reality checked against the rows.
    Report-only: fixes go through the three registry doors (hire, review diff,
    retirement), never through this command."""
    findings: list[dict] = []
    employees = parse_registry(root / "roles" / "employees.yaml")
    ids = {e.get("id") for e in employees}

    for e in employees:
        eid = e.get("id", "?")
        if (e.get("status") or "") == "retired":
            continue
        for part in (e.get("skill_chain") or "").split(","):
            w = part.strip().split()[0] if part.strip() else ""
            if "/" in w and w.endswith(".py") and not (root / w).exists():
                findings.append({"kind": "engine-missing", "employee": eid,
                                 "detail": f"skill_chain names {w} which does not exist"})
        if (e.get("status") or "") == "active" and not (e.get("run_record_source") or "").strip():
            findings.append({"kind": "active-without-evidence", "employee": eid,
                             "detail": "status is active but no run_record_source names where "
                                       "its runs are recorded - active means there is evidence"})
        if not (e.get("job_description") or "").strip():
            findings.append({"kind": "no-job-description", "employee": eid,
                             "detail": "no job_description - the human face is not optional"})

    agents_dir = root / ".claude" / "agents"
    if agents_dir.is_dir():
        for p in sorted(agents_dir.glob("*.md")):
            if p.stem not in ids:
                findings.append({"kind": "agent-file-unrostered", "employee": p.stem,
                                 "detail": f".claude/agents/{p.name} has no roles/employees.yaml row"})
    return findings


def cmd_drift(args) -> int:
    findings = registry_drift(Path(args.root))
    if args.json:
        print(json.dumps({"count": len(findings), "findings": findings}, ensure_ascii=True))
        return 0
    if not findings:
        print("drift: registry and reality agree.")
        return 0
    print(f"drift: {len(findings)} finding(s). Report only - fix through the three "
          f"registry doors (hire / review diff / retirement).\n")
    for f in findings:
        print(f"[{f['kind']}] {f['employee']}: {f['detail']}")
    return 0


# ----- charter audit (report-only) -----

# A grant that hands over a whole interpreter, a shell, or a file-editing tool is
# not a boundary. Those are refused on a job whose description says it only
# proposes, because "never sends" has to be a stated contract, not a loophole.
BLANKET_GRANTS = ("bash", "bash(*)", "shell", "*", "all")
BLANKET_PREFIXES = ("bash(python:", "bash(python3:", "bash(sh:", "bash(pwsh:",
                    "bash(powershell:", "bash(cmd:")
# Interpreters that, followed by a bare wildcard (no script path), grant the
# whole interpreter: Bash(python *), Bash(python3 *), Bash(py -3 *).
BLANKET_INTERPRETERS = ("python", "python3", "py", "sh", "bash", "pwsh",
                        "powershell", "cmd")


def _is_blanket_grant(grant_low: str) -> bool:
    if grant_low in BLANKET_GRANTS or grant_low.startswith(BLANKET_PREFIXES):
        return True
    if grant_low.startswith("bash(") and grant_low.endswith(")"):
        inner = grant_low[5:-1].strip()
        tokens = inner.split()
        if tokens and tokens[0] in BLANKET_INTERPRETERS \
                and "/" not in inner and "\\" not in inner:
            # No script path anywhere in the rule: the scope is the interpreter
            # itself, which is every script on the machine.
            return True
    return False
EDIT_TOOLS = ("edit", "write", "multiedit", "notebookedit")
PROPOSE_ONLY_SIGNALS = ("does not send", "never send", "never sends", "propose only",
                        "propose-only", "does not approve", "never approves")


def _skill_allowed_tools(root: Path, skill: str) -> list[str] | None:
    """Read the allowed-tools list from skills/<skill>/SKILL.md frontmatter.

    This is the second place the grant lives - the skill's declared runtime
    list. Returns None when the skill file is absent (a chain entry that is
    prose, or a plugin-path install where skills live in the engine) or the
    frontmatter has no allowed-tools key. Returns [] when the key exists but
    declares nothing - the caller treats that as its own finding.

    Handles the shapes Claude Code accepts: an inline list (["Read", "Bash"]),
    a bare comma-separated line, a space-separated line with no commas or
    parens, and a multiline YAML list of "- item" lines.
    """
    path = root / "skills" / skill / "SKILL.md"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if not lines or lines[0].strip() != "---":
        return None

    def _split(raw: str) -> list[str]:
        raw = raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            raw = raw[1:-1]
        if "," not in raw and "(" not in raw and " " in raw:
            chunks = raw.split()
        else:
            chunks = raw.split(",")
        return [c.strip().strip("'\"").strip() for c in chunks if c.strip().strip("'\"").strip()]

    in_list = False
    tools: list[str] = []
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return tools if in_list else None
        if in_list:
            if stripped.startswith("- "):
                t = stripped[2:].strip().strip("'\"").strip()
                if t:
                    tools.append(t)
                continue
            return tools
        if stripped.startswith("allowed-tools:"):
            raw = stripped.split(":", 1)[1].strip()
            if raw:
                return _split(raw)
            in_list = True
    return tools if in_list else None


def charter_findings(employees: list[dict], root: Path | None = None) -> list[dict]:
    out: list[dict] = []
    for e in employees:
        eid = e.get("id", "?")
        if (e.get("status") or "") == "retired":
            continue
        tools_raw = (e.get("tools") or "").strip()
        dispatch = (e.get("dispatch") or "").strip()
        grants = [t.strip() for t in tools_raw.split(",") if t.strip()]
        low = [g.lower() for g in grants]

        if not grants:
            out.append({"kind": "no-grant", "employee": eid,
                        "detail": "no tools field - the charter IS the grant, so this job "
                                  "cannot be dispatched at all (fail closed)"
                                  + (f"; dispatch says '{dispatch}'" if dispatch else "")})
            continue
        for g, g_low in zip(grants, low):
            if _is_blanket_grant(g_low):
                out.append({"kind": "blanket-grant", "employee": eid,
                            "detail": f"grant '{g}' hands over a whole interpreter or shell, "
                                      f"which permits every script on the machine including "
                                      f"any that send"})
        desc = (e.get("job_description") or "").lower() + " " + (e.get("never") or "").lower()
        propose_only = any(s in desc for s in PROPOSE_ONLY_SIGNALS)
        if propose_only:
            bad = [g for g, g_low in zip(grants, low) if g_low in EDIT_TOOLS]
            if bad:
                out.append({"kind": "propose-only-with-edit-tool", "employee": eid,
                            "detail": f"job says it only proposes, but the grant includes "
                                      f"{', '.join(bad)}"})
        if not (e.get("may_write") or "").strip():
            out.append({"kind": "no-may-write", "employee": eid,
                        "detail": "no may_write field - name every store it may change, "
                                  "in plain language"})
        if not (e.get("never") or "").strip():
            out.append({"kind": "no-never", "employee": eid,
                        "detail": "no never field - the prohibitions are what make the shape "
                                  "of the job readable in one line"})

        # The seam check, both directions. The grant lives in two places: this
        # row, and the allowed-tools list each chain skill declares. The two
        # lists are kept identical (per chain, the charter covers the union),
        # and drift in either direction is a finding: a wider skill list means
        # the charter understates what the seat may do, and a charter tool no
        # skill declares means the charter promises a grant nothing carries.
        # Comparison is case-sensitive on purpose - a case-only difference in a
        # script path is a real difference on Linux.
        if root is not None:
            charter_exact = set(grants)
            chain = [s.strip() for s in (e.get("skill_chain") or "").split(",") if s.strip()]
            chain_union: set[str] = set()
            any_resolved = False
            for skill in chain:
                ftools = _skill_allowed_tools(root, skill)
                if ftools is None:
                    continue
                any_resolved = True
                if not ftools:
                    out.append({"kind": "skill-grant-missing", "employee": eid,
                                "detail": f"skills/{skill}/SKILL.md has an allowed-tools key that "
                                          f"declares nothing - the seat's runtime list is "
                                          f"undeclared, so the charter has nothing to hold against"})
                    continue
                chain_union.update(ftools)
                for t in ftools:
                    if _is_blanket_grant(t.lower()):
                        out.append({"kind": "skill-grant-blanket", "employee": eid,
                                    "detail": f"skills/{skill}/SKILL.md allowed-tools grants '{t}' - "
                                              f"a whole shell or interpreter, so this row's "
                                              f"narrower grant is decorative"})
                    elif t not in charter_exact:
                        out.append({"kind": "skill-grant-drift", "employee": eid,
                                    "detail": f"skills/{skill}/SKILL.md allowed-tools grants '{t}', "
                                              f"which this row's tools field does not - the skill's "
                                              f"declared list is wider than the charter; align them "
                                              f"in the same commit"})
            if any_resolved:
                for g in grants:
                    if g not in chain_union:
                        out.append({"kind": "charter-grant-drift", "employee": eid,
                                    "detail": f"this row grants '{g}' but no skill in its chain "
                                              f"declares it in allowed-tools - the charter promises "
                                              f"a grant nothing carries; align them in the same "
                                              f"commit"})
    return out


def cmd_charters(args) -> int:
    registry_path = Path(args.registry)
    employees = parse_registry(registry_path)
    findings = charter_findings(employees, root=registry_path.resolve().parent.parent)
    if args.json:
        print(json.dumps({"count": len(findings), "findings": findings}, ensure_ascii=True))
        return 0
    if not employees:
        print("charters: the registry is empty. Nothing to audit, which is the honest "
              "starting state.")
        return 0
    if not findings:
        print(f"charters: {len(employees)} row(s), every charter states its grant, its "
              f"writes, and its prohibitions.")
        return 0
    print(f"charters: {len(findings)} finding(s) across {len(employees)} row(s). Report only.\n")
    for f in findings:
        print(f"[{f['kind']}] {f['employee']}: {f['detail']}")
    return 0


# ----- cli -----

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="The performance loop for digital employees (rules/digital-employees.md).")
    sub = p.add_subparsers(dest="cmd", required=True)

    common_registry = dict(default=str(REGISTRY), help="path to roles/employees.yaml")
    common_file = dict(default=str(VERDICTS), help="path to the verdicts ledger")

    pv = sub.add_parser("verdict", help="Record one verdict on a run you saw.")
    pv.add_argument("--employee", required=True)
    pv.add_argument("--verdict", required=True, choices=list(VALID_VERDICTS))
    pv.add_argument("--why", required=True, help="one line on what you saw")
    pv.add_argument("--ref", default=None, help="optional reference (a queue item, a file)")
    pv.add_argument("--registry", **common_registry)
    pv.add_argument("--file", **common_file)
    pv.set_defaults(func=cmd_verdict)

    pl = sub.add_parser("list", help="Print verdicts, newest last.")
    pl.add_argument("--employee", default=None)
    pl.add_argument("--last", type=int, default=50)
    pl.add_argument("--file", **common_file)
    pl.set_defaults(func=cmd_list)

    pr = sub.add_parser("render", help="Write the org chart view.")
    pr.add_argument("--registry", **common_registry)
    pr.add_argument("--file", **common_file)
    pr.add_argument("--out", default=str(VIEW))
    pr.add_argument("--asof", default=None, help="YYYY-MM-DD (default today)")
    pr.set_defaults(func=cmd_render)

    pa = sub.add_parser("archive", help="Roll old verdicts out of the live ledger.")
    pa.add_argument("--file", **common_file)
    pa.add_argument("--archive-dir", dest="archive_dir", default=str(ARCHIVE_DIR))
    pa.add_argument("--threshold", type=int, default=ARCHIVE_THRESHOLD_LINES)
    pa.add_argument("--force", action="store_true", help="roll even below the threshold")
    pa.add_argument("--asof", default=None)
    pa.set_defaults(func=cmd_archive)

    pd = sub.add_parser("drift", help="Cross-check the registry against reality. Report-only.")
    pd.add_argument("--root", default=str(REPO_ROOT))
    pd.add_argument("--json", action="store_true")
    pd.set_defaults(func=cmd_drift)

    pc = sub.add_parser("charters", help="Audit every row's grant. Report-only.")
    pc.add_argument("--registry", **common_registry)
    pc.add_argument("--json", action="store_true")
    pc.set_defaults(func=cmd_charters)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
