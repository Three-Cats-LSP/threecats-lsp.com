#!/usr/bin/env python3
"""Verify d-planner-plus/ contains every path listed in site-assets-manifest.txt."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "d-planner-plus"
MANIFEST = APP / "site-assets-manifest.txt"
SKIP = {".nojekyll", "about.html"}


def main() -> int:
    if not MANIFEST.is_file():
        print(f"Missing manifest: {MANIFEST}", file=sys.stderr)
        return 1
    paths = [ln.strip() for ln in MANIFEST.read_text(encoding="utf-8").splitlines() if ln.strip()]
    missing = []
    for rel in paths:
        if rel in SKIP or rel.endswith(".apk"):
            continue
        if not (APP / rel).is_file():
            missing.append(rel)
    if missing:
        print(f"FAILED — {len(missing)} manifest path(s) missing under {APP}:")
        for rel in missing:
            print(f"  {rel}")
        return 1
    print(f"OK — {len(paths)} manifest paths present under d-planner-plus/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
