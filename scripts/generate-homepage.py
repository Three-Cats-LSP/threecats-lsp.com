#!/usr/bin/env python3
"""Generate homepage toolkit cards.

Uses only Tailwind classes present in the exported homepage CSS bundle.
Edit scripts/homepage-cards.json, then run:

    python scripts/generate-homepage.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CARDS_JSON = Path(__file__).resolve().parent / "homepage-cards.json"
INDEX = ROOT / "index.html"

GRID_MARKER = 'class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-4xl"'
GRID_MARKER_FIXED = (
    'class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 items-start w-full max-w-4xl"'
)
GRID_END_MARKER = '<div class="mt-20 w-full max-w-4xl"'

CARD_SHELL = (
    'relative rounded-xl border p-6 flex flex-col gap-4 transition-shadow duration-300 '
    "bg-card border-border hover:border-primary "
    "hover:shadow-[0_0_24px_0_rgba(255,140,66,0.18)] cursor-pointer"
)

SVG_ICONS = {
    "book-open": (
        '<svg class="lucide lucide-book-open w-7 h-7" fill="none" height="24" '
        'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
        'stroke-width="2" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M12 7v14"></path>'
        '<path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path>'
        "</svg>"
    ),
    "layers": (
        '<svg class="lucide lucide-layers w-7 h-7" fill="none" height="24" '
        'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
        'stroke-width="2" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
        '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"></path>'
        '<path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"></path>'
        '<path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"></path>'
        "</svg>"
    ),
}

ICON_EXTERNAL = (
    '<svg class="lucide lucide-external-link w-3.5 h-3.5" fill="none" height="24" '
    'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
    'stroke-width="2" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M15 3h6v6"></path><path d="M10 14 21 3"></path>'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></svg>'
)

ICON_EXTERNAL_SM = (
    '<svg class="lucide lucide-external-link w-3 h-3 opacity-50" fill="none" height="24" '
    'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
    'stroke-width="2" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M15 3h6v6"></path><path d="M10 14 21 3"></path>'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></svg>'
)


def render_icon(icon: dict[str, str]) -> str:
    if icon.get("type") == "img":
        src = html.escape(icon["src"])
        alt = html.escape(icon.get("alt", ""))
        return f'<img alt="{alt}" class="w-10 h-10 object-contain rounded" src="{src}"/>'
    name = icon.get("name", "book-open")
    return SVG_ICONS.get(name, SVG_ICONS["book-open"])


def render_featured(items: list[dict[str, str]]) -> str:
    if not items:
        return ""
    rows = []
    for item in items:
        title = html.escape(item["title"])
        href = html.escape(item["href"])
        desc = html.escape(item.get("description", ""))
        rows.append(
            f'<li><a class="group flex flex-col gap-0.5 hover:text-primary transition-colors duration-200" '
            f'href="{href}" rel="noopener noreferrer" target="_blank">'
            f'<span class="text-xs font-semibold text-foreground group-hover:text-primary flex items-center gap-1">'
            f"{title}{ICON_EXTERNAL_SM}</span>"
            f'<span class="text-xs text-muted-foreground leading-relaxed">{desc}</span></a></li>'
        )
    return '<ul class="mt-3 flex flex-col gap-2">' + "".join(rows) + "</ul>"


def render_card(card: dict[str, Any]) -> str:
    title = html.escape(card["title"])
    description = html.escape(card["description"])
    icon_html = render_icon(card["icon"])

    about_html = ""
    if card.get("about_href"):
        about = html.escape(card["about_href"])
        about_html = (
            f'<a class="absolute top-4 right-4 text-xs font-medium text-muted-foreground '
            f'hover:text-primary transition-colors duration-200 z-10" href="{about}" '
            f'rel="noopener noreferrer">About The App</a>'
        )

    featured_html = render_featured(card.get("featured") or [])

    cta = card["cta"]
    cta_label = html.escape(cta["label"])
    cta_href = html.escape(cta["href"])
    external = bool(cta.get("external"))
    cta_target = ' rel="noopener noreferrer" target="_blank"' if external else ' rel="noopener noreferrer"'
    discover = ' data-discover="true"' if card.get("kind") == "gear" else ""

    return f"""<div class="{CARD_SHELL}" style="opacity: 1; transform: none;">
{about_html}
<div class="w-12 h-12 rounded-lg flex items-center justify-center bg-primary/10 text-primary">{icon_html}</div>
<div>
<h2 class="text-lg font-semibold text-foreground mb-1">{title}</h2>
<p class="text-sm text-muted-foreground leading-relaxed">{description}</p>
{featured_html}
</div>
<a class="inline-flex items-center gap-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors duration-200"{discover} href="{cta_href}"{cta_target}>{cta_label}{ICON_EXTERNAL}</a>
</div>"""


def replace_cards_grid(page: str, cards_html: str) -> str:
    page = page.replace(GRID_MARKER, GRID_MARKER_FIXED, 1)
    grid_pos = page.find(GRID_MARKER_FIXED)
    if grid_pos < 0:
        raise SystemExit("Homepage card grid not found")
    open_pos = page.find(">", grid_pos) + 1
    close_pos = page.find(GRID_END_MARKER, open_pos)
    if close_pos < 0:
        raise SystemExit("Homepage card grid end not found")
    return page[:open_pos] + cards_html + "</div>" + page[close_pos:]


def main() -> None:
    config = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
    cards_html = "".join(render_card(card) for card in config.get("cards", []))
    page = INDEX.read_text(encoding="utf-8")
    INDEX.write_text(replace_cards_grid(page, cards_html), encoding="utf-8")
    print(f"Wrote {len(config.get('cards', []))} cards to {INDEX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
