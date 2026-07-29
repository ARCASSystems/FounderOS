#!/usr/bin/env python3
"""skills_sync.py - make sure a skill can actually be found by something.

The problem it exists for, and it is the expensive kind because nothing looks
broken: a skill only ever runs if something can find it. You can write ninety
well-formed skills, every one with a clean description, and have most of them
reachable by nothing at all. No slash command names them, no registry row lists
them, no other skill points at them. They are perfect and invisible, and the OS
quietly behaves as though they were never written.

Two jobs, matching the two ways a skill goes missing:

  reachability  Is every skill in skills/ reachable from at least one surface -
                a slash command, the registry, the bootloader, the docs, another
                skill, or the discoverable manifest? Anything reachable from
                nothing is named. This is the check that catches the real failure.

  check/apply   Claude Code discovers skills natively in .claude/skills/. For the
                handful you want reached the moment you describe a situation
                (rather than after the model reads a registry), skills/discoverable.yaml
                names them and --apply copies them there. --check reports drift
                between source and copy.

skills/ is the single source. The copy under .claude/skills/ is generated and
gitignored. Never edit it: the next --apply overwrites it.

Invariants: standard library only (no PyYAML - the manifest is read by
scripts/flat_yaml.py), no network, no API key. --check and --reachability write
nothing. --apply writes only inside .claude/skills/, and only ever removes a
directory it could have created itself: a plugin's skill or one you placed by
hand is left alone.

Usage:
  python scripts/skills_sync.py --reachability          # the real check
  python scripts/skills_sync.py --reachability --json   # machine form, for verify
  python scripts/skills_sync.py --check                 # report copy drift, exit 1 if any
  python scripts/skills_sync.py --apply                 # sync, then re-check
  python scripts/skills_sync.py --check --quiet-when-clean
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "skills" / "discoverable.yaml"
DESC_LIMIT = 1024  # Claude Code rejects a longer description outright


def _flat_yaml():
    src = Path(__file__).resolve().parent / "flat_yaml.py"
    spec = importlib.util.spec_from_file_location("founderos_flat_yaml", src)
    if spec is None or spec.loader is None:  # pragma: no cover - packaging accident
        raise SystemExit("skills_sync: cannot load scripts/flat_yaml.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----- reading -----

def load_manifest(path: Path = MANIFEST) -> dict:
    """Both blocks of the manifest, as {'discoverable': [...], 'never_touch': [...]}
    of skill names. A missing manifest is not an error: it means nothing has been
    promoted to native discovery yet, which is a valid state."""
    if not path.exists():
        return {"discoverable": [], "never_touch": []}
    fy = _flat_yaml()
    text = path.read_text(encoding="utf-8")
    out = {}
    for block in ("discoverable", "never_touch"):
        rows = fy.parse_flat_yaml(text, filename=str(path), record_key=block)
        out[block] = [r["skill"] for r in rows if r.get("skill")]
    return out


def frontmatter(skill_md: Path) -> tuple[str | None, str | None]:
    """(name, description) from the SKILL.md frontmatter, or (None, None)."""
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return (None, None)
    fm = m.group(1)
    nm = re.search(r"^name:\s*(.+)$", fm, re.M)
    ds = re.search(r"^description:\s*(.+(?:\n\s+.+)*)$", fm, re.M)
    name = nm.group(1).strip().strip("\"'") if nm else None
    desc = " ".join(ds.group(1).split()) if ds else None
    return (name, desc)


def live_skills(repo: Path = REPO) -> list[str]:
    root = repo / "skills"
    if not root.is_dir():
        return []
    return sorted(p.parent.name for p in root.glob("*/SKILL.md")
                  if "_archive" not in p.parts)


def tree_digest(d: Path) -> str:
    """Content hash of a skill directory. Line endings are normalised: a Windows
    checkout flips CRLF and would otherwise report permanent false drift."""
    h = hashlib.sha256()
    for f in sorted(p for p in d.rglob("*") if p.is_file()):
        h.update(str(f.relative_to(d)).replace(os.sep, "/").encode())
        h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


# ----- reachability (the check that matters) -----

# Every surface a session could find a skill through. A skill named by any one of
# these is reachable; one named by none is invisible however well it is written.
def reachability(repo: Path = REPO) -> dict:
    skills = live_skills(repo)
    manifest = load_manifest(repo / "skills" / "discoverable.yaml")
    promoted = set(manifest.get("discoverable") or [])

    surfaces: dict[str, str] = {}

    cmd_dir = repo / ".claude" / "commands"
    if cmd_dir.is_dir():
        for p in cmd_dir.glob("*.md"):
            body = p.read_text(encoding="utf-8", errors="ignore")
            for name in re.findall(r"skills/([a-z0-9_-]+)/SKILL\.md", body):
                surfaces.setdefault(name, f"command /{p.stem}")

    for rel, label in (("skills/index.md", "the registry"),
                       ("CLAUDE.md", "the bootloader"),
                       ("docs/skills.md", "the docs")):
        p = repo / rel
        if not p.is_file():
            continue
        body = p.read_text(encoding="utf-8", errors="ignore")
        for name in skills:
            if name in surfaces:
                continue
            # A registry row or a docs heading names the skill directly.
            if re.search(rf"\[{re.escape(name)}\]\({re.escape(name)}/SKILL\.md\)", body) \
                    or re.search(rf"(?m)^###\s+{re.escape(name)}\s*$", body) \
                    or re.search(rf"`?/founder-os:{re.escape(name)}`?", body) \
                    or re.search(rf"skills/{re.escape(name)}/SKILL\.md", body):
                surfaces[name] = label

    # Another skill pointing at it counts: a chain is a real path to being run.
    for p in (repo / "skills").glob("*/SKILL.md"):
        owner = p.parent.name
        body = p.read_text(encoding="utf-8", errors="ignore")
        for name in re.findall(r"skills/([a-z0-9_-]+)/SKILL\.md", body):
            if name != owner:
                surfaces.setdefault(name, f"skill {owner}")

    for name in promoted:
        surfaces.setdefault(name, "the discoverable manifest")

    unreachable = [s for s in skills if s not in surfaces]
    return {
        "total": len(skills),
        "reachable": len(skills) - len(unreachable),
        "unreachable": unreachable,
        "promoted": sorted(promoted),
        "by_surface": surfaces,
    }


# ----- checking the copy -----

def check(repo: Path = REPO, manifest: dict | None = None,
          user_skills_dir: Path | None = None) -> tuple[list[str], list[str], list[str]]:
    """(errors, drift, warnings). Errors cannot load at all. Drift is the copy
    disagreeing with the source. Warnings never fail the check."""
    man = manifest or load_manifest(repo / "skills" / "discoverable.yaml")
    src_root = repo / "skills"
    dst_root = repo / ".claude" / "skills"
    never = set(man.get("never_touch") or [])
    wanted = list(man.get("discoverable") or [])

    errors: list[str] = []
    drift: list[str] = []
    warnings: list[str] = []

    for name in wanted:
        src = src_root / name
        md = src / "SKILL.md"
        if not md.exists():
            errors.append(f"{name}: named in the manifest but skills/{name}/SKILL.md does not exist")
            continue
        fm_name, desc = frontmatter(md)
        if not desc:
            errors.append(f"{name}: SKILL.md has no description - it cannot load")
        elif len(desc) > DESC_LIMIT:
            errors.append(f"{name}: description is {len(desc)} chars, over the {DESC_LIMIT} "
                          f"limit - it will not load")
        if fm_name and fm_name != name:
            errors.append(f"{name}: frontmatter says name: {fm_name} - it must match the directory")

        dst = dst_root / name
        if not dst.exists():
            drift.append(f"{name}: not in .claude/skills - the model cannot see it natively")
        elif tree_digest(src) != tree_digest(dst):
            drift.append(f"{name}: the copy in .claude/skills differs from skills/{name}")

    if dst_root.exists():
        for d in sorted(p for p in dst_root.iterdir() if p.is_dir()):
            if d.name not in wanted and d.name not in never:
                drift.append(f"{d.name}: in .claude/skills but not in the manifest - orphan copy")

    # A same-named skill in the user directory is a second answer to the same question,
    # and which one replies is not something you control.
    usd = user_skills_dir if user_skills_dir is not None else (
        Path(os.environ.get("USERPROFILE", os.path.expanduser("~"))) / ".claude" / "skills")
    if usd.exists():
        for d in sorted(p for p in usd.iterdir() if p.is_dir()):
            if d.name in wanted:
                src_md, usr_md = src_root / d.name / "SKILL.md", d / "SKILL.md"
                detail = ""
                if src_md.exists() and usr_md.exists():
                    a, b = src_md.stat().st_size, usr_md.stat().st_size
                    if a != b:
                        detail = f" (this OS {a}b vs the user copy {b}b)"
                warnings.append(f"{d.name}: also in ~/.claude/skills{detail} - two versions of "
                                f"the same skill exist and you do not control which one answers")
    return (errors, drift, warnings)


# ----- applying -----

def apply(repo: Path = REPO, manifest: dict | None = None) -> list[str]:
    """Materialise the manifest into .claude/skills. Returns the actions taken."""
    man = manifest or load_manifest(repo / "skills" / "discoverable.yaml")
    src_root = repo / "skills"
    dst_root = repo / ".claude" / "skills"
    never = set(man.get("never_touch") or [])
    wanted = list(man.get("discoverable") or [])
    dst_root.mkdir(parents=True, exist_ok=True)
    actions: list[str] = []

    for name in wanted:
        src = src_root / name
        if not (src / "SKILL.md").exists():
            actions.append(f"skipped {name} - no skills/{name}/SKILL.md")
            continue
        dst = dst_root / name
        if dst.exists():
            if tree_digest(src) == tree_digest(dst):
                continue
            shutil.rmtree(dst)
            actions.append(f"updated {name}")
        else:
            actions.append(f"added {name}")
        shutil.copytree(src, dst)

    for d in sorted(p for p in dst_root.iterdir() if p.is_dir()):
        # Only ever removes a copy this script could have made. A plugin skill or an
        # unrelated directory stays where it is.
        if d.name not in wanted and d.name not in never and (src_root / d.name).exists():
            shutil.rmtree(d)
            actions.append(f"removed {d.name} - no longer in the manifest")
    return actions


# ----- the capability page -----
#
# One generated answer to "what can this actually do", built from the skills that
# are installed rather than from a list somebody maintains. A hand-kept registry
# is wrong the first week someone forgets it, and a wrong capability list is worse
# than none: it teaches you the OS cannot do something it can.
CAPABILITY_PAGE = Path("docs") / "what-this-can-do.md"
CAPABILITY_MARK = "<!-- generated by scripts/skills_sync.py --capabilities. Do not hand-edit. -->"

# Grouping is by the command surface a skill is reached through, because that is
# how a founder thinks about it. Anything unmatched lands in "Everything else",
# which is honest rather than filed under a heading that does not fit.
CAPABILITY_GROUPS = [
    ("Your day", ("today", "next", "morning-loop", "queue", "priority-triage",
                  "weekly-review", "since-last-session", "menu", "founder-next-move")),
    ("Your brain", ("brain-log", "brain-pass", "catch-up", "knowledge-capture",
                    "ingest", "query", "cross-link", "wiki-build", "lint",
                    "log-archive", "memory-pass", "observation-rollup", "history")),
    ("Writing in your voice", ("your-voice", "voice-interview", "brand-interview",
                               "linkedin-post", "email-drafter", "client-update",
                               "content-repurposer", "proposal-writer", "sop-writer",
                               "your-deliverable-template", "brand-voice-interview")),
    ("Customers and pipeline", ("prospect-init", "meeting-prep", "pipeline-start",
                                "reconnect-prompt", "linkedin-network-scan",
                                "linkedin-power-audit", "linkedin-warm-revival",
                                "linkedin-brand-direction", "review-responder")),
    ("Thinking it through", ("decision-framework", "strategic-analysis",
                             "bottleneck-diagnostic", "unit-economics",
                             "founder-coaching", "forcing-questions",
                             "founder-scope-challenge", "blind-spot-review",
                             "what-to-change", "strategic-read")),
    ("Your team of roles", ("employee-review", "profile-router", "routines")),
    ("Keeping it healthy", ("verify", "audit", "housekeeping", "readiness-check",
                            "os-evolve", "founder-review", "skill-creator",
                            "backup", "restore", "save", "own-your-history",
                            "session-handoff", "connect", "tune")),
    ("Before anything leaves your machine", ("pre-send-check", "ship-deliverable",
                                             "approval-gates", "data-security")),
]


def skills_root(repo: Path = REPO) -> Path:
    """Where the skills actually live for this install shape.

    A git-clone, curl or ZIP install keeps them in the folder. A plugin install
    keeps the founder's data in their folder and the engine under ~/.claude/plugins,
    so reading `<repo>/skills` there finds nothing and would generate an empty page
    claiming the OS can do nothing. Same resolution order the verify skill uses.
    """
    local = repo / "skills"
    if local.is_dir():
        return local
    return Path.home() / ".claude" / "plugins" / "founder-os" / "skills"


def _first_sentence(desc: str, limit: int = 220) -> str:
    """One plain line per skill. A description is written to trigger a match, so
    it often opens with a pile of quoted phrases; the page wants the sentence a
    person would read."""
    desc = re.sub(r"^[>|][+-]?\s*", "", desc.strip())   # YAML folded/literal marker
    desc = re.sub(r'"[^"]*"(,\s*)?', "", desc)          # drop the trigger phrases
    desc = re.sub(r"\(or run [^)]*\)", "", desc)
    desc = re.sub(r"\s+", " ", desc).strip(" ,.;")
    for sep in (". ", "? "):
        if sep in desc:
            desc = desc.split(sep)[0]
            break
    return (desc[: limit - 1] + "…") if len(desc) > limit else desc


def capability_page(repo: Path = REPO) -> str:
    root = skills_root(repo)
    rows: dict[str, str] = {}
    for md in sorted(root.glob("*/SKILL.md")) if root.is_dir() else []:
        if "_archive" in md.parts:
            continue
        _, desc = frontmatter(md)
        if not desc:
            continue
        rows[md.parent.name] = _first_sentence(desc)

    # Deliberately no version stamp. The page is about what is installed, not
    # about which release you are on, and stamping it would make every version
    # bump mark the page stale - so a founder editing one skill would be blocked
    # by a number that has nothing to do with their edit. The page drifts only
    # when the skill set drifts, which is the only drift worth a gate.
    out = [
        "# What this can do",
        "",
        CAPABILITY_MARK,
        "",
        f"Generated from the {len(rows)} skills installed here.",
        "",
        "Nothing on this page is maintained by hand, so it cannot claim a capability "
        "that is not installed or miss one that is. If a skill is here, it is on your "
        "disk. Say the thing in plain language; the slash command in brackets is the "
        "shortcut, not the requirement.",
        "",
        "Regenerate after adding or removing a skill:",
        "",
        "```",
        "python scripts/skills_sync.py --capabilities",
        "```",
        "",
    ]

    placed: set[str] = set()
    for title, names in CAPABILITY_GROUPS:
        present = [n for n in names if n in rows]
        if not present:
            continue
        out += [f"## {title}", ""]
        for n in present:
            out.append(f"- **{n}** - {rows[n]}")
            placed.add(n)
        out.append("")

    rest = [n for n in sorted(rows) if n not in placed]
    if rest:
        out += ["## Everything else", "",
                "Installed and working. They have not been sorted into a group above, "
                "which says something about this page and nothing about them.", ""]
        for n in rest:
            out.append(f"- **{n}** - {rows[n]}")
        out.append("")

    if not rows:
        out += ["No skills found.", "",
                "On a plugin install the skills live under `~/.claude/plugins/founder-os/`, "
                "not in this folder. If that path is missing, the engine is not reachable "
                "and `/founder-os:verify` will say so.", ""]

    return "\n".join(out)


def capabilities_cmd(repo: Path = REPO, write: bool = True) -> int:
    """Write the page, or report drift without writing."""
    target = repo / CAPABILITY_PAGE
    fresh = capability_page(repo)
    current = target.read_text(encoding="utf-8") if target.exists() else None
    if current is not None and current.replace("\r\n", "\n") == fresh:
        print(f"capabilities: {target.as_posix()} is current.")
        return 0
    if not write:
        state = "missing" if current is None else "stale"
        print(f"capabilities: {target.as_posix()} is {state}. A skill was added or "
              f"removed and the page was not rebuilt, so it now understates or "
              f"overstates what this install can do.\n"
              f"  fix: python scripts/skills_sync.py --capabilities")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(fresh, encoding="utf-8", newline="\n")
    print(f"capabilities: wrote {target.as_posix()}")
    return 0


def _report_reachability(r: dict, as_json: bool) -> int:
    if as_json:
        print(json.dumps({k: r[k] for k in ("total", "reachable", "unreachable", "promoted")},
                         ensure_ascii=True))
        return 0
    if not r["unreachable"]:
        print(f"skills-reachability: {r['reachable']}/{r['total']} skills reachable from at "
              f"least one surface. Nothing is invisible.")
        if r["promoted"]:
            print(f"  natively discoverable ({len(r['promoted'])}): {', '.join(r['promoted'])}")
        return 0
    print(f"skills-reachability: {len(r['unreachable'])} of {r['total']} skills are reachable "
          f"from NOTHING - no command, no registry row, no docs entry, no other skill.\n")
    for name in r["unreachable"]:
        print(f"  unreachable  {name}")
    print("\nFix any one of these: add a registry row in skills/index.md, add a slash command, "
          "name it in docs/skills.md, or promote it in skills/discoverable.yaml.")
    return 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--reachability", action="store_true",
                   help="is every skill reachable from at least one surface (writes nothing)")
    p.add_argument("--check", action="store_true", help="report copy drift, never write")
    p.add_argument("--apply", action="store_true", help="sync the manifest into .claude/skills")
    p.add_argument("--json", action="store_true", help="machine form (with --reachability)")
    p.add_argument("--quiet-when-clean", action="store_true",
                   help="print nothing when there is no drift")
    p.add_argument("--capabilities", action="store_true",
                   help="regenerate docs/what-this-can-do.md from the installed skills")
    args = p.parse_args(argv)

    if args.capabilities:
        # --capabilities --check reports drift and writes nothing, which is what
        # the commit gate and CI call.
        return capabilities_cmd(write=not args.check)

    if args.reachability:
        return _report_reachability(reachability(), args.json)

    if args.apply:
        actions = apply()
        if not actions and not args.quiet_when_clean:
            actions = ["nothing to do - .claude/skills already matches the manifest"]
        for line in actions:
            print("skills-sync: " + line, flush=True)

    errors, drift, warnings = check()
    count = len(load_manifest().get("discoverable") or [])

    if not errors and not drift:
        if not args.quiet_when_clean:
            print(f"skills-sync: {count} skills promoted to native discovery, "
                  f".claude/skills matches skills/", flush=True)
            for w in warnings:
                print("  warn  " + w, flush=True)
        return 0

    print(f"skills-sync: {len(errors)} error(s), {len(drift)} drift - fix with "
          f"python scripts/skills_sync.py --apply", flush=True)
    for e in errors:
        print("  ERROR " + e, flush=True)
    for d in drift:
        print("  drift " + d, flush=True)
    for w in warnings:
        print("  warn  " + w, flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
