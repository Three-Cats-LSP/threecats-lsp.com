#!/usr/bin/env python3
"""Copy local app trees into threecats-lsp.com deploy folders (dev/preview sync)."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent

DEPLOYS = [
    {
        "src": PARENT / "LSP_D-planner",
        "dst": ROOT / "d-planner",
        "files": [
            "index.html", "download.html", "manifest.json", "sw.js", "capacitor-bridge.js",
            "icon-192.png", "icon-512.png",
            "zhl-engine-bundle.js", "zhl-schedule-worker.js", "zhl-worker-bridge.js",
            "tests.html", "tests-extended.html", "tests-massive.html", "tests-massive-main.html", "tests-verify.html",
        ],
        "dirs": ["vendor"],
        "readme": "d-planner.md",
    },
    {
        "src": PARENT / "LSP_D-planner-CCR",
        "dst": ROOT / "d-planner-ccr",
        "files": [
            "index.html", "download.html", "manifest.json", "sw.js", "capacitor-bridge.js",
            "icon-192.png",
            "tests.html", "tests-extended.html", "tests-massive.html", "tests-massive-main.html",
            "tests-verify.html", "tests-pscr-otu-cns.html",
        ],
        "dirs": [],
        "readme": "d-planner-ccr.md",
    },
    {
        "src": PARENT / "LSP_D-planner-plus",
        "dst": ROOT / "d-planner-plus",
        "files": [
            "index.html", "download.html", "manifest.json", "sw.js", "app-version.js",
            "capacitor-bridge.js",
            "icon-192.png", "icon-512.png",
            "zhl-engine-bundle.js", "vpm-engine-bundle.js", "zhl-schedule-worker.js", "zhl-worker-bridge.js",
            "tests.html", "tests-extended.html", "tests-massive.html", "tests-massive-main.html",
            "tests-verify.html", "tests-pscr-otu-cns.html", "tests-ccr-differential.html",
        ],
        "dirs": ["vendor"],
        "readme": "d-planner-plus.md",
    },
]

for spec in DEPLOYS:
    src: Path = spec["src"]
    dst: Path = spec["dst"]
    dst.mkdir(parents=True, exist_ok=True)
    for name in spec["files"]:
        s = src / name
        if s.is_file():
            shutil.copy2(s, dst / name)
    for dname in spec["dirs"]:
        sdir = src / dname
        ddir = dst / dname
        if sdir.is_dir():
            if ddir.exists():
                shutil.rmtree(ddir)
            shutil.copytree(sdir, ddir)
    readme_src = src / "README.md"
    if readme_src.is_file():
        (ROOT / "scripts" / "readmes" / spec["readme"]).write_text(
            readme_src.read_text(encoding="utf-8"), encoding="utf-8"
        )
    print(f"Synced {src.name} -> {dst.relative_to(ROOT)}")
