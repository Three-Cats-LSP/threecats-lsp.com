#!/usr/bin/env python3
from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text(encoding="utf-8")
match = re.search(
    r'alt="Three Cats LSP"[^>]*src="(data:image/png;base64,([^"]+))"',
    html,
)
if not match:
    raise SystemExit("Three Cats LSP logo not found in index.html")

out_dir = ROOT / "assets"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "Just Cats.png"
out_path.write_bytes(base64.b64decode(match.group(2)))
print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")
