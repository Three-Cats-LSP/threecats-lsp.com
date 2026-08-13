#!/usr/bin/env python3
"""Build the exact static tree uploaded to GitHub Pages."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT_FILES = [
    ".nojekyll",
    "CNAME",
    "README.md",
    "about.css",
    "gadgets.html",
    "index.html",
]

PUBLIC_DIRS = [
    "assets",
    "d-planner",
    "d-planner-ccr",
    "d-planner-plus",
    "get-in-water",
    "knowledge-base",
    "seabirds",
    "subsurface-neo",
    "t-viewer",
]


def copy_file(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def copy_dir(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)


def build(root: Path, out_dir: Path) -> None:
    root = root.resolve()
    out_dir = out_dir.resolve()
    if out_dir == root or root in out_dir.parents:
        shutil.rmtree(out_dir, ignore_errors=True)
    elif out_dir.exists():
        raise SystemExit(f"Refusing to overwrite output outside repo: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    for rel in ROOT_FILES:
        copy_file(root / rel, out_dir / rel)
    for rel in PUBLIC_DIRS:
        copy_dir(root / rel, out_dir / rel)

    # The stable download URL is SeaBirds-Windows-Setup.exe. Historical,
    # versioned installers belong in GitHub Releases and needlessly make every
    # Pages snapshot tens of megabytes larger.
    seabirds_dir = out_dir / "seabirds"
    for installer in seabirds_dir.glob("SeaBirds-Windows-Setup-*.exe"):
        installer.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, default=Path("_site"))
    args = parser.parse_args()
    build(args.root, args.out)
    print(f"OK - built Pages artifact at {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
