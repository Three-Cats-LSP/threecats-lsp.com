"""Insert LSP D-Planner + CCR card into homepage index.html."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / "index.html"
index = index_path.read_text(encoding="utf-8")

if "d-planner-ccr/about.html" in index:
    print("CCR card already present")
    raise SystemExit(0)

CARD_CLASS = 'class="relative rounded-xl border p-6 flex flex-col gap-4 transition-shadow duration-300 bg-card border-border'

# Extract one full card as SVG template (T-Viewer)
tv = index.find("/t-viewer/about.html")
if tv < 0:
    raise SystemExit("T-Viewer card not found")
start = index.rfind("<div " + CARD_CLASS.replace('class="', 'class="'), 0, tv)
if start < 0:
    start = index.rfind('<div class="relative rounded-xl border p-6 flex flex-col gap-4', 0, tv)
end = index.find('<div class="relative rounded-xl border p-6 flex flex-col gap-4', tv + 10)
if end < 0:
    end = index.find("</section>", tv)
template = index[start:end]

# External link SVG from template
svg_match = re.search(
    r'(<svg class="lucide lucide-external-link[^"]*"[^>]*>.*?</svg>)',
    template,
    re.DOTALL,
)
ext_svg = svg_match.group(1) if svg_match else ""

ccr_card = f'''<div class="relative rounded-xl border p-6 flex flex-col gap-4 transition-shadow duration-300 bg-card border-border hover:border-primary hover:shadow-[0_0_24px_0_rgba(255,140,66,0.18)] cursor-pointer" style="opacity: 1; transform: none;"><a class="absolute top-4 right-4 text-xs font-medium text-muted-foreground hover:text-primary transition-colors duration-200 z-10" href="/d-planner-ccr/about.html" rel="noopener noreferrer">About The App</a><div class="w-12 h-12 rounded-lg flex items-center justify-center bg-primary/10 text-primary"><img alt="LSP D-Planner + CCR" class="w-10 h-10 object-contain rounded" src="/d-planner-ccr/icon-192.png"/></div><div class="flex-1"><h2 class="text-lg font-semibold text-foreground mb-1">LSP D-Planner + CCR</h2><p class="text-sm text-muted-foreground leading-relaxed">Rebreather edition — CCR, passive SCR (pSCR), bailout, and descent setpoint. Bühlmann ZH-L16C + GF and VPM-B on the v2.20.x foundation. Separate from open-circuit D-Planner.</p></div><a class="inline-flex items-center gap-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors duration-200 mt-auto" href="/d-planner-ccr/" rel="noopener noreferrer" target="_blank">Open App{ext_svg}</a></div>'''

# Insert before T-Viewer card
new_index = index[:start] + ccr_card + index[start:]

# JSON-LD entry after LSP D-Planner
ld = new_index.find('"name": "LSP D-Planner",')
if ld > 0:
    url_end = new_index.find('"url": "https://threecats-lsp.com/d-planner/"', ld)
    obj_end = new_index.find("}", url_end)
    insert = """,
    {
      "@type": "SoftwareApplication",
      "name": "LSP D-Planner + CCR",
      "applicationCategory": "SportsApplication",
      "operatingSystem": "Web, Android",
      "url": "https://threecats-lsp.com/d-planner-ccr/",
      "description": "Rebreather decompression planner — CCR, pSCR, bailout. Separate edition from LSP D-Planner."
    }"""
    new_index = new_index[: obj_end + 1] + insert + new_index[obj_end + 1 :]

new_index = new_index.replace(
    "LSP D-Planner, T-Viewer, and Get In Water are free",
    "LSP D-Planner, LSP D-Planner + CCR, T-Viewer, and Get In Water are free",
)

index_path.write_text(new_index, encoding="utf-8")
print("OK: inserted CCR card before T-Viewer")
