#!/usr/bin/env python3
"""Replace OC + CCR homepage cards with single LSP D-Planner+ card."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / "index.html"
html = index_path.read_text(encoding="utf-8")

CARD_START = '<div class="relative rounded-xl border p-6 flex flex-col gap-4 transition-shadow duration-300 bg-card border-border'

def extract_card(html: str, about_href: str) -> tuple[str, str, str]:
    """Return (before, card, after) removing one card by about link."""
    marker = f'href="{about_href}"'
    pos = html.find(marker)
    if pos < 0:
        raise SystemExit(f"Card not found: {about_href}")
    start = html.rfind(CARD_START, 0, pos)
    if start < 0:
        raise SystemExit(f"Card start not found for {about_href}")
    # card ends at next card start or grid close
    next_card = html.find(CARD_START, start + len(CARD_START))
    grid_end = html.find("</div></div></section>", start)
    if next_card > 0 and (grid_end < 0 or next_card < grid_end):
        end = next_card
    else:
        end = grid_end if grid_end > start else len(html)
    return html[:start], html[start:end], html[end:]

# Remove CCR then OC (order preserves indices if we do from later in file first)
for about in ("/d-planner-ccr/about.html", "/d-planner/about.html"):
    before, card, after = extract_card(html, about)
    html = before + after

# Insert Plus card before T-Viewer
tv_pos = html.find("/t-viewer/about.html")
if tv_pos < 0:
    raise SystemExit("T-Viewer card not found")
start = html.rfind(CARD_START, 0, tv_pos)

plus_card = '''<div class="relative rounded-xl border p-6 flex flex-col gap-4 transition-shadow duration-300 bg-card border-border hover:border-primary hover:shadow-[0_0_24px_0_rgba(255,140,66,0.18)] cursor-pointer" style="opacity: 1; transform: none;"><a class="absolute top-4 right-4 text-xs font-medium text-muted-foreground hover:text-primary transition-colors duration-200 z-10" href="/d-planner-plus/about.html" rel="noopener noreferrer">About The App</a><div class="w-12 h-12 rounded-lg flex items-center justify-center bg-primary/10 text-primary"><img alt="LSP D-Planner+" class="w-10 h-10 object-contain rounded" src="/d-planner-plus/icon-192.png"/></div><div class="flex-1"><h2 class="text-lg font-semibold text-foreground mb-1">LSP D-Planner+</h2><p class="text-sm text-muted-foreground leading-relaxed">Unified open-circuit and rebreather decompression planner — Bühlmann ZHL-16C + GF, VPM-B, CCR, pSCR, bailout, Tier 3 engine, offline PWA and Android.</p></div><a class="inline-flex items-center gap-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors duration-200 mt-auto" href="/d-planner-plus/" rel="noopener noreferrer" target="_blank">Open App<svg class="lucide lucide-external-link h-3.5 w-3.5" fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M15 3h6v6"></path><path d="M10 14 21 3"></path><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></svg></a></div>'''

html = html[:start] + plus_card + html[start:]

# JSON-LD: replace two planner entries with one Plus entry
ld_block = re.search(
    r'\{\s*"@type": "SoftwareApplication",\s*"name": "LSP D-Planner",.*?\},\s*'
    r'\{\s*"@type": "SoftwareApplication",\s*"name": "LSP D-Planner \+ CCR",.*?\}',
    html,
    re.DOTALL,
)
if ld_block:
    plus_ld = '''{
      "@type": "SoftwareApplication",
      "name": "LSP D-Planner+",
      "applicationCategory": "SportsApplication",
      "operatingSystem": "Web, Android",
      "url": "https://threecats-lsp.com/d-planner-plus/",
      "description": "Unified OC and rebreather decompression planner with Bühlmann ZHL-16C, VPM-B, CCR, pSCR, and bailout support."
    }'''
    html = html[: ld_block.start()] + plus_ld + html[ld_block.end() :]

# Meta / support copy
html = html.replace(
    "LSP D-Planner, LSP D-Planner + CCR, T-Viewer, and Get In Water",
    "LSP D-Planner+, T-Viewer, and Get In Water",
)
html = html.replace(
    "the LSP D-Planner deco schedule app",
    "the LSP D-Planner+ deco schedule app",
)
html = html.replace(
    "Includes LSP D-Planner decompression app",
    "Includes LSP D-Planner+ decompression app",
)

index_path.write_text(html, encoding="utf-8")
print("Homepage updated: LSP D-Planner+ card, JSON-LD, meta copy")
