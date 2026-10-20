#!/usr/bin/env python3
"""Build the downloadable Founder OS release.

Why this exists: for fifty-three versions the only download link pointed at
`archive/refs/heads/main.zip`, GitHub's raw branch archive. It extracts to a
folder called `FounderOS-main` and reads to a non-technical founder as exactly
what it is, a developer artifact. This builds the thing they should get
instead: one named file, extracting to one named folder, carrying the icon.

What it produces, into `dist/`:

  FounderOS-<version>.zip          the release asset
  FounderOS-<version>.zip.sha256   the checksum line for the release notes
  FounderOS.zip                    the same bytes under a name that never changes
  FounderOS.zip.sha256             its checksum line
  FounderOS-<version>.dmg          macOS only, and only when hdiutil is there

Why the unversioned copy: GitHub serves
`releases/latest/download/FounderOS.zip` from whichever release is newest,
but only when that release carries an asset with exactly that name. Uploaded
with every release, it is a download link that never has to be edited, so a
version bump can no longer leave the front door pointing at a 404.

Line endings: the archive carries what git holds, which is LF for every text
file. Two files must reach the founder as CRLF - `Start Founder OS.bat` (cmd
misparses labels in an LF batch file) and `desktop.ini` (Explorer reads it
inconsistently otherwise) - and `.gitattributes` says so with eol=crlf. A
checkout applies that; an archive built from blobs did not, so the shipped
.bat was LF. Every path whose `git check-attr eol` is crlf is now converted on
the way into the zip.

What goes in: every file git tracks, read from git's own object store rather
than from the working copy. Anything gitignored is excluded by construction
rather than by a list somebody has to remember - no `.git`, no `__pycache__`,
no `voice/runtime-log.jsonl`, no local state.

Reading blobs rather than files is the part worth keeping. Taking the file list
from git and the CONTENT from disk shipped whatever happened to be in the
working tree: an uncommitted edit, a debugging line, a pasted key. It also
shipped Windows line endings, because `.gitattributes` normalises on checkin
and a Windows checkout is CRLF on disk, so a ZIP built on Windows and a `git
clone` on Linux were not the same tree. Both are closed by asking git for the
bytes. A dirty tree is refused outright anyway, since the version you ship
should be the version you can go back to.

Two details that are easy to get wrong and expensive to miss:

  The exec bit. `Start Founder OS.command` is only double-clickable on a Mac if
  it keeps mode 755 through the archive. The mode comes from git's own index,
  not from the working copy, because a Windows checkout does not carry it.

  The DOS attribute bits. Windows draws the folder icon named in desktop.ini
  only when the folder carries the read-only marker bit, so the root entry is
  written with it, and desktop.ini with hidden and system. Measured on Windows
  11 against Explorer's own extractor: it ignores all three. Tools that read
  them, 7-Zip among them, get a branded folder straight out of the archive;
  everyone else gets it on the first double-click, because `Start Founder OS.bat`
  sets the same three bits itself. The launcher is the mechanism that carries
  the Explorer path, not a fallback for it.

Usage:

  python scripts/build_release.py                 # version from VERSION
  python scripts/build_release.py --version 1.56.0
  python scripts/build_release.py --skip-dmg
  python scripts/build_release.py --allow-dirty  # build anyway, marked in the output
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# The name the folder carries once it is extracted. This is what the founder
# looks at for the next several years, so it is the product name, not a slug.
FOLDER_NAME = "Founder OS"
ASSET_STEM = "FounderOS"

# MS-DOS attribute bits, as stored in the low byte of external_attr.
DOS_READONLY = 0x01
DOS_HIDDEN = 0x02
DOS_SYSTEM = 0x04
DOS_DIRECTORY = 0x10

# Paths that must never reach a release even if something starts tracking them.
# git already excludes all of these; this is the second lock, not the first.
NEVER_SHIP = (
    ".git/",
    "__pycache__/",
    ".pytest_cache/",
    "voice/runtime-log.jsonl",
)


def run(args: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(REPO), capture_output=True, text=True, **kw)


def tracked_files() -> list[tuple[str, int]]:
    """Every tracked path with its git file mode. Sorted, so builds repeat."""
    r = run(["git", "ls-files", "-s"])
    if r.returncode != 0:
        raise SystemExit(f"git ls-files failed: {r.stderr.strip()}")
    out: list[tuple[str, int]] = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        mode = int(meta.split()[0], 8)
        out.append((path, mode))
    return sorted(out)


def blob_bytes(rel: str) -> bytes:
    """The committed content of one tracked path, straight from git.

    Git rather than `open(path)`: the working copy can carry an uncommitted
    edit and, on Windows, carries CRLF where the repository holds LF. Neither
    belongs in something a stranger downloads.
    """
    return read_blobs([rel])[rel]


def staged_but_uncommitted(rels: list[str]) -> list[str]:
    """Tracked paths that do not exist at HEAD yet.

    `git add` on a new file puts it in `ls-files` while HEAD has never seen it,
    so the blob read dies with a bare "missing" from git. Named here so
    --allow-dirty says what to do instead of crashing.
    """
    r = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD"],
                       cwd=str(REPO), capture_output=True, text=True)
    if r.returncode != 0:
        return []
    at_head = set(r.stdout.splitlines())
    return [rel for rel in rels if rel not in at_head]


def read_blobs(rels: list[str]) -> dict[str, bytes]:
    """Every blob through ONE git process.

    `git show` per file spawned five hundred processes and took over a minute
    on Windows. `cat-file --batch` reads the same objects down one pipe.
    """
    if not rels:
        return {}
    proc = subprocess.Popen(
        ["git", "cat-file", "--batch"], cwd=str(REPO),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    query = "".join(f"HEAD:{r}\n" for r in rels).encode("utf-8")
    out, err = proc.communicate(query)
    if proc.returncode != 0:
        raise SystemExit(f"git cat-file failed: {err.decode(errors='replace')[:200]}")

    result: dict[str, bytes] = {}
    pos = 0
    for rel in rels:
        nl = out.find(b"\n", pos)
        if nl == -1:
            raise SystemExit(f"git cat-file returned nothing for {rel}")
        header = out[pos:nl].decode("utf-8", "replace")
        if header.endswith(("missing", "ambiguous")):
            raise SystemExit(f"git could not read HEAD:{rel} - {header}")
        size = int(header.rsplit(" ", 1)[1])
        start = nl + 1
        result[rel] = out[start:start + size]
        pos = start + size + 1            # skip the trailing newline git adds
    return result


def crlf_paths(rels: list[str]) -> set[str]:
    """The tracked paths .gitattributes marks eol=crlf, asked of git itself so
    the rule has one home. One process, NUL-separated, so a space in a name
    (Start Founder OS.bat) cannot split a record."""
    if not rels:
        return set()
    r = subprocess.run(
        ["git", "check-attr", "-z", "--stdin", "eol"],
        cwd=str(REPO), input=("\0".join(rels) + "\0").encode("utf-8"),
        capture_output=True,
    )
    if r.returncode != 0:
        # Failing open here ships an LF .bat, the exact defect this exists to
        # stop, so a broken attribute lookup stops the build instead.
        raise SystemExit("git check-attr failed, so line endings cannot be set: "
                         + r.stderr.decode("utf-8", "replace").strip()[:200])
    fields = r.stdout.decode("utf-8", "replace").split("\0")
    out: set[str] = set()
    for i in range(0, len(fields) - 2, 3):
        path, _attr, value = fields[i], fields[i + 1], fields[i + 2]
        if value == "crlf":
            out.add(path)
    return out


def to_crlf(data: bytes) -> bytes:
    """LF to CRLF without doubling a CR that is already there."""
    return data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def dirty_paths() -> list[str]:
    """Tracked files that differ from HEAD. An untracked file is not a problem:
    it cannot reach the archive, because the archive is built from the index."""
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                       cwd=str(REPO), capture_output=True, text=True)
    if r.returncode != 0:
        # A gate that cannot check must not wave things through. Failing open
        # here means a broken git call silently ships whatever is on disk.
        raise SystemExit(
            "git status failed, so the working tree cannot be checked:\n  "
            + (r.stderr or "").strip()[:200]
            + "\nRefusing to build rather than guessing the tree is clean."
        )
    return [ln[3:].strip() for ln in r.stdout.splitlines() if ln.strip()]


def refuse_excluded(paths: list[str]) -> None:
    bad = [p for p in paths if any(p == n or p.startswith(n) for n in NEVER_SHIP)]
    if bad:
        raise SystemExit(
            "These paths are tracked but must never ship:\n  "
            + "\n  ".join(bad)
            + "\nUntrack them before building a release."
        )


def read_version(explicit: str | None) -> str:
    if explicit:
        return explicit.strip().lstrip("v")
    version_file = REPO / "VERSION"
    if not version_file.is_file():
        raise SystemExit("No VERSION file and no --version given.")
    return version_file.read_text(encoding="utf-8").strip().lstrip("v")


def build_zip(version: str, out_dir: Path, allow_dirty: bool = False) -> Path:
    entries = tracked_files()
    refuse_excluded([p for p, _ in entries])

    dirty = dirty_paths()
    if dirty and not allow_dirty:
        raise SystemExit(
            "The working tree has uncommitted changes, so the release would not "
            "match any commit:\n  " + "\n  ".join(dirty[:20])
            + ("\n  ..." if len(dirty) > 20 else "")
            + "\nCommit them, or pass --allow-dirty if you mean it. Either way the "
              "archive carries the COMMITTED bytes, never the working copy."
        )

    new_files = staged_but_uncommitted([rel for rel, _ in entries])
    if new_files:
        raise SystemExit(
            "These files are staged but not committed, so HEAD has no bytes for "
            "them:\n  " + "\n  ".join(new_files[:20])
            + ("\n  ..." if len(new_files) > 20 else "")
            + "\nCommit them or unstage them. --allow-dirty cannot help here: the "
              "archive is built from HEAD and HEAD does not have these files."
        )

    zip_path = out_dir / f"{ASSET_STEM}-{version}.zip"
    if zip_path.exists():
        zip_path.unlink()

    # One timestamp for every entry, taken from the commit, so two builds of the
    # same commit produce the same archive.
    r = subprocess.run(["git", "show", "-s", "--format=%ct", "HEAD"],
                       cwd=str(REPO), capture_output=True, text=True)
    import datetime as _dt
    when = (_dt.datetime.fromtimestamp(int(r.stdout.strip()))
            if r.returncode == 0 and r.stdout.strip().isdigit() else _dt.datetime.now())
    stamp = (when.year, when.month, when.day, when.hour, when.minute, when.second)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # The root folder entry, carrying the read-only marker that tells
        # Windows to read desktop.ini at all.
        root = zipfile.ZipInfo(f"{FOLDER_NAME}/", date_time=stamp)
        root.create_system = 3  # unix, so the exec bit below survives
        root.external_attr = (
            (stat.S_IFDIR | 0o755) << 16
        ) | DOS_DIRECTORY | DOS_READONLY
        z.writestr(root, b"")

        blobs = read_blobs([rel for rel, _ in entries])
        crlf = crlf_paths([rel for rel, _ in entries])
        for rel, mode in entries:
            data = blobs[rel]
            if rel in crlf:
                data = to_crlf(data)
            info = zipfile.ZipInfo(f"{FOLDER_NAME}/{rel}", date_time=stamp)
            info.create_system = 3
            unix_mode = 0o755 if mode == 0o100755 else 0o644
            dos = 0
            if Path(rel).name == "desktop.ini":
                dos = DOS_HIDDEN | DOS_SYSTEM
            info.external_attr = ((stat.S_IFREG | unix_mode) << 16) | dos
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)

    return zip_path


def write_checksum(zip_path: Path) -> Path:
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    sidecar = zip_path.with_suffix(zip_path.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8")
    return sidecar


def write_stable_copy(zip_path: Path) -> tuple[Path, Path]:
    """dist/FounderOS.zip: the same bytes as the versioned asset, under the one
    name `releases/latest/download/FounderOS.zip` resolves to. Its own
    checksum line names the file it sits next to."""
    stable = zip_path.with_name(f"{ASSET_STEM}.zip")
    if stable.exists():
        stable.unlink()
    shutil.copyfile(zip_path, stable)
    return stable, write_checksum(stable)


def _shown(p: Path) -> str:
    try:
        return p.relative_to(REPO).as_posix()
    except ValueError:
        return str(p)


def upload_lines(version: str, groups: list[list[Path]]) -> list[str]:
    """One `gh release upload` line per asset and its checksum. Printed, never
    run: publishing is the maintainer's decision, made with eyes open."""
    return [
        f"gh release upload v{version} "
        + " ".join(f'"{_shown(p)}"' for p in group)
        + " --clobber"
        for group in groups if group
    ]


def build_dmg(version: str, out_dir: Path) -> Path | None:
    """Build the Mac disk image. Returns None, with a reason, when it cannot."""
    if sys.platform != "darwin":
        print("  dmg: skipped, not running on macOS")
        return None
    if shutil.which("hdiutil") is None:
        print("  dmg: skipped, hdiutil not found")
        return None

    staging = out_dir / "_dmg" / FOLDER_NAME
    if staging.parent.exists():
        shutil.rmtree(staging.parent)
    staging.mkdir(parents=True)

    entries = tracked_files()
    blobs = read_blobs([rel for rel, _ in entries])
    crlf = crlf_paths([rel for rel, _ in entries])
    for rel, mode in entries:
        target = staging / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        data = blobs[rel]                         # committed bytes, as above
        target.write_bytes(to_crlf(data) if rel in crlf else data)
        if mode == 0o100755:
            target.chmod(0o755)

    icns = REPO / "assets" / "arcas.icns"
    if icns.is_file():
        shutil.copy2(icns, staging.parent / ".VolumeIcon.icns")
        if shutil.which("SetFile"):
            subprocess.run(["SetFile", "-a", "C", str(staging.parent)], check=False)
        else:
            print("  dmg: volume icon copied but not marked "
                  "(SetFile missing - run xcode-select --install)")

    dmg_path = out_dir / f"{ASSET_STEM}-{version}.dmg"
    if dmg_path.exists():
        dmg_path.unlink()
    r = subprocess.run(
        ["hdiutil", "create", "-volname", FOLDER_NAME, "-srcfolder",
         str(staging.parent), "-ov", "-format", "UDZO", str(dmg_path)],
        capture_output=True, text=True,
    )
    shutil.rmtree(staging.parent, ignore_errors=True)
    if r.returncode != 0:
        print(f"  dmg: hdiutil failed - {r.stderr.strip()}")
        return None
    return dmg_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Founder OS release assets.")
    ap.add_argument("--version", help="Release version. Defaults to the VERSION file.")
    ap.add_argument("--out", default="dist", help="Output directory (default: dist).")
    ap.add_argument("--skip-dmg", action="store_true", help="Do not attempt the dmg.")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="Build from HEAD even with uncommitted changes present.")
    args = ap.parse_args()

    version = read_version(args.version)
    out_dir = (REPO / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building Founder OS {version}")
    zip_path = build_zip(version, out_dir, allow_dirty=args.allow_dirty)
    sidecar = write_checksum(zip_path)
    stable, stable_sidecar = write_stable_copy(zip_path)

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  zip: {zip_path.name}  {len(names)} entries, {size_mb:.1f} MB")
    print(f"  sha256: {sidecar.read_text(encoding='utf-8').split()[0]}")
    print(f"  stable copy: {stable.name} (same bytes; the latest/download link)")
    print(f"  extracts to: {FOLDER_NAME}/")
    print("  contents: the committed bytes at HEAD, not the working copy")
    if args.allow_dirty and dirty_paths():
        print("  WARNING: --allow-dirty was passed and the tree is dirty. The "
              "archive still holds HEAD, so it does NOT contain your uncommitted work.")

    dmg = None
    if not args.skip_dmg:
        dmg = build_dmg(version, out_dir)
        if dmg is not None:
            print(f"  dmg: {dmg.name}  {dmg.stat().st_size / (1024 * 1024):.1f} MB")

    print()
    print("Release checklist:")
    print("  1. Upload to the release tagged v" + version + " (the versioned asset,")
    print("     then the stable copy every release must also carry):")
    for line in upload_lines(version, [[zip_path, sidecar], [stable, stable_sidecar],
                                       [dmg] if dmg is not None else []]):
        print("       " + line)
    print("  2. Prove GitHub serves them - the text check alone said 'Current' for")
    print("     v1.56.0 while its asset was a 404:")
    print("       python scripts/check_download_links.py --require-published")
    print("  The README download link must point at that asset;")
    print("  scripts/check_download_links.py fails the suite if it does not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
