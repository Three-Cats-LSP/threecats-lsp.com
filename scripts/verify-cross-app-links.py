#!/usr/bin/env python3
"""Verify public app mirrors expose the full Three Cats app link row.

The individual app repositories can be correct while the threecats-lsp.com
mirror is stale. This check runs against the deploy tree so Pages cannot ship
an app row that is missing one of the sibling apps.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


APP_LINKS = {
    "d-planner-plus": "https://threecats-lsp.com/d-planner-plus/",
    "t-viewer": "https://threecats-lsp.com/t-viewer/",
    "get-in-water": "https://threecats-lsp.com/get-in-water/",
    "seabirds": "https://threecats-lsp.com/seabirds/",
}

APP_ICON_MARKERS = {
    "d-planner-plus": ("d-planner-plus/icon-192.png", "app-dplanner.png"),
    "t-viewer": ("t-viewer/icon-192.png", "app-tviewer.png"),
    "get-in-water": ("get-in-water/icon-192.png", "giw-icon-192.png", "app-getinwater.png"),
    "seabirds": ("seabirds/icon-192.png", "seabirds/icon.svg", "app-seabirds"),
}

PAGES = {
    "d-planner-plus": Path("d-planner-plus/index.html"),
    "t-viewer": Path("t-viewer/index.html"),
    "get-in-water": Path("get-in-water/index.html"),
    "seabirds": Path("seabirds/index.html"),
}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"missing page: {path}") from None


def verify(root: Path) -> list[str]:
    errors: list[str] = []
    for app, rel_path in PAGES.items():
        html = _read(root / rel_path)
        expected_apps = [name for name in APP_LINKS if name != app]
        for expected in expected_apps:
            href = APP_LINKS[expected]
            if href not in html:
                errors.append(f"{rel_path}: missing link to {expected} ({href})")
            if not any(marker in html for marker in APP_ICON_MARKERS[expected]):
                markers = ", ".join(APP_ICON_MARKERS[expected])
                errors.append(f"{rel_path}: missing visible icon marker for {expected} ({markers})")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    args = parser.parse_args(argv)

    errors = verify(args.root)
    if errors:
        print("Cross-app link verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("OK - public app mirrors include sibling app links and icons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
