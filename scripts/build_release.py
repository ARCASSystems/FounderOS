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
  FounderOS-<version>.dmg          macOS only, and only when hdiutil is there

What goes in: every file git tracks, and nothing else. Using `git ls-files` as
the source means anything gitignored is excluded by construction rather than by
a list somebody has to remember to update - no `.git`, no `__pycache__`, no
`.pytest_cache`, no `voice/runtime-log.jsonl`, no local state. It also means
the ZIP and a `git clone` hand over the same tree, so the five install paths
cannot drift apart.

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
  python scripts/build_release.py --version 1.55.0
  python scripts/build_release.py --skip-dmg
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


def build_zip(version: str, out_dir: Path) -> Path:
    entries = tracked_files()
    refuse_excluded([p for p, _ in entries])

    zip_path = out_dir / f"{ASSET_STEM}-{version}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # The root folder entry, carrying the read-only marker that tells
        # Windows to read desktop.ini at all.
        root = zipfile.ZipInfo(f"{FOLDER_NAME}/")
        root.create_system = 3  # unix, so the exec bit below survives
        root.external_attr = (
            (stat.S_IFDIR | 0o755) << 16
        ) | DOS_DIRECTORY | DOS_READONLY
        z.writestr(root, b"")

        for rel, mode in entries:
            source = REPO / rel
            if not source.is_file():
                # A tracked file missing from the working tree means a broken
                # checkout. Say so rather than shipping a hole.
                raise SystemExit(f"Tracked but missing from the working tree: {rel}")

            info = zipfile.ZipInfo.from_file(source, f"{FOLDER_NAME}/{rel}")
            info.create_system = 3
            unix_mode = 0o755 if mode == 0o100755 else 0o644
            dos = 0
            if Path(rel).name == "desktop.ini":
                dos = DOS_HIDDEN | DOS_SYSTEM
            info.external_attr = ((stat.S_IFREG | unix_mode) << 16) | dos
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, source.read_bytes())

    return zip_path


def write_checksum(zip_path: Path) -> Path:
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    sidecar = zip_path.with_suffix(zip_path.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8")
    return sidecar


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

    for rel, mode in tracked_files():
        target = staging / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, target)
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
    args = ap.parse_args()

    version = read_version(args.version)
    out_dir = (REPO / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building Founder OS {version}")
    zip_path = build_zip(version, out_dir)
    sidecar = write_checksum(zip_path)

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  zip: {zip_path.name}  {len(names)} entries, {size_mb:.1f} MB")
    print(f"  sha256: {sidecar.read_text(encoding='utf-8').split()[0]}")
    print(f"  extracts to: {FOLDER_NAME}/")

    if not args.skip_dmg:
        dmg = build_dmg(version, out_dir)
        if dmg is not None:
            print(f"  dmg: {dmg.name}  {dmg.stat().st_size / (1024 * 1024):.1f} MB")

    print()
    print("Upload to the release tagged v" + version + ". The README download")
    print("link must point at that asset - scripts/check_download_links.py")
    print("fails the suite if it does not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
