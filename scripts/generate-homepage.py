#!/usr/bin/env python3
"""Generate homepage toolkit cards with the current card design.

Edit scripts/homepage-cards.json (and knowledge-base-resources.json for KB previews),
then run:

    python scripts/generate-homepage.py
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CARDS_JSON = Path(__file__).resolve().parent / "homepage-cards.json"
KB_JSON = Path(__file__).resolve().parent / "knowledge-base-resources.json"
INDEX = ROOT / "index.html"

GRID_MARKER = 'class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-4xl"'
GRID_END_MARKER = '<div class="mt-20 w-full max-w-4xl"'

CARD_SHELL = (
    'group relative overflow-hidden rounded-xl border border-border/80 bg-card/70 '
    "backdrop-blur-sm p-6 flex flex-col gap-4 transition-all duration-300 "
    "hover:border-primary/45 hover:shadow-[0_10px_36px_-10px_rgba(255,140,66,0.28)] "
    "hover:-translate-y-0.5"
)

SVG_ICONS = {
    "book-open": (
        '<svg class="lucide lucide-book-open w-7 h-7" fill="none" height="24" '
        'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
        'stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M12 7v14"></path>'
        '<path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path>'
        "</svg>"
    ),
    "layers": (
        '<svg class="lucide lucide-layers w-7 h-7" fill="none" height="24" '
        'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
        'stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
        '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"></path>'
        '<path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"></path>'
        '<path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"></path>'
        "</svg>"
    ),
}

ICON_EXTERNAL = (
    '<svg class="lucide lucide-external-link w-3.5 h-3.5 shrink-0 opacity-80" fill="none" '
    'height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
    'stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M15 3h6v6"></path><path d="M10 14 21 3"></path>'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></svg>'
)

ICON_CHEVRON = (
    '<svg class="lucide lucide-chevron-right w-3.5 h-3.5 shrink-0 opacity-80" fill="none" '
    'height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
    'stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
    '<path d="m9 18 6-6-6-6"></path></svg>'
)

ICON_EXTERNAL_SM = (
    '<svg class="lucide lucide-external-link w-3 h-3 opacity-50 shrink-0" fill="none" '
    'height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
    'stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M15 3h6v6"></path><path d="M10 14 21 3"></path>'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></svg>'
)


def load_kb_featured(limit: int, skip_badges: list[str] | None = None) -> list[dict[str, str]]:
    if not KB_JSON.is_file():
        return []
    skip = {b.lower() for b in (skip_badges or [])}
    data = json.loads(KB_JSON.read_text(encoding="utf-8"))
    items: list[dict[str, str]] = []
    for section in data.get("sections", []):
        badge = section.get("badge", "Link")
        if badge.lower() in skip:
            continue
        for raw in section.get("items", []):
            if isinstance(raw, str):
                entry = {"url": raw}
            else:
                entry = dict(raw)
            url = entry.get("url", "")
            title = entry.get("title") or ""
            if not title or title.startswith("http"):
                continue
            desc = entry.get("description", "")
            items.append(
                {
                    "title": title,
                    "description": desc,
                    "href": url,
                    "badge": badge,
                }
            )
            if len(items) >= limit:
                return items
    return items


def render_icon(icon: dict[str, str]) -> str:
    if icon.get("type") == "img":
        src = html.escape(icon["src"])
        alt = html.escape(icon.get("alt", ""))
        return (
            f'<img alt="{alt}" class="w-10 h-10 object-contain rounded-lg" src="{src}"/>'
        )
    name = icon.get("name", "book-open")
    return SVG_ICONS.get(name, SVG_ICONS["book-open"])


def render_featured(items: list[dict[str, str]]) -> str:
    if not items:
        return ""
    rows = []
    for item in items:
        title = html.escape(item["title"])
        href = html.escape(item["href"])
        badge = html.escape(item.get("badge", "Link"))
        desc = item.get("description", "")
        desc_html = ""
        if desc:
            desc_html = (
                f'<span class="text-[11px] text-muted-foreground leading-snug line-clamp-2">'
                f"{html.escape(desc)}</span>"
            )
        rows.append(
            f"""<li><a class="group/item flex items-start gap-2.5 rounded-lg border border-transparent px-2.5 py-2 -mx-1 hover:border-primary/20 hover:bg-primary/5 transition-colors duration-200" href="{href}" rel="noopener noreferrer" target="_blank"><span class="text-[9px] font-bold uppercase tracking-wider text-primary/75 mt-0.5 shrink-0 w-9">{badge}</span><span class="min-w-0 flex flex-col gap-0.5"><span class="text-xs font-semibold text-foreground group-hover/item:text-primary flex items-center gap-1">{title}{ICON_EXTERNAL_SM}</span>{desc_html}</span></a></li>"""
        )
    return (
        '<ul class="mt-3 flex flex-col gap-0.5 border-t border-border/40 pt-3">'
        + "".join(rows)
        + "</ul>"
    )


def render_card(card: dict[str, Any]) -> str:
    category = html.escape(card.get("category", "Toolkit"))
    title = html.escape(card["title"])
    description = html.escape(card["description"])
    icon_html = render_icon(card["icon"])

    about_html = ""
    if card.get("about_href"):
        about = html.escape(card["about_href"])
        about_html = (
            f'<a class="absolute top-4 right-4 text-[11px] font-medium text-muted-foreground '
            f'hover:text-primary transition-colors duration-200 z-10" href="{about}" '
            f'rel="noopener noreferrer">About</a>'
        )

    featured: list[dict[str, str]] = []
    if card.get("featured"):
        featured = card["featured"]
    elif card.get("featured_from_kb"):
        featured = load_kb_featured(
            int(card["featured_from_kb"]),
            card.get("featured_kb_skip_badges"),
        )

    featured_html = render_featured(featured)

    cta = card["cta"]
    cta_label = html.escape(cta["label"])
    cta_href = html.escape(cta["href"])
    external = bool(cta.get("external"))
    cta_icon = ICON_EXTERNAL if external else ICON_CHEVRON
    cta_target = ' rel="noopener noreferrer" target="_blank"' if external else ' rel="noopener noreferrer"'
    discover = ' data-discover="true"' if not external and card.get("kind") == "gear" else ""

    return f"""<div class="{CARD_SHELL}">
<div class="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/55 to-transparent"></div>
{about_html}
<div class="flex items-start gap-3.5">
<div class="w-12 h-12 rounded-xl flex items-center justify-center bg-primary/10 text-primary ring-1 ring-primary/20 shrink-0">{icon_html}</div>
<div class="min-w-0 pt-0.5">
<span class="text-[10px] font-semibold uppercase tracking-[0.14em] text-primary/90">{category}</span>
<h2 class="text-lg font-semibold text-foreground mt-1 mb-1 leading-tight">{title}</h2>
</div>
</div>
<div class="flex-1">
<p class="text-sm text-muted-foreground leading-relaxed">{description}</p>
{featured_html}
</div>
<a class="inline-flex items-center justify-between gap-2 w-full text-sm font-medium text-primary hover:text-primary/80 transition-colors duration-200 mt-auto pt-4 border-t border-border/50 group-hover:border-primary/15"{discover} href="{cta_href}"{cta_target}><span>{cta_label}</span>{cta_icon}</a>
</div>"""


def replace_cards_grid(page: str, cards_html: str) -> str:
    grid_pos = page.find(GRID_MARKER)
    if grid_pos < 0:
        raise SystemExit("Homepage card grid not found")
    open_pos = page.find(">", grid_pos) + 1
    close_pos = page.find(GRID_END_MARKER, open_pos)
    if close_pos < 0:
        raise SystemExit("Homepage card grid end not found")
    return page[:open_pos] + cards_html + page[close_pos:]


def main() -> None:
    config = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
    cards_html = "".join(render_card(card) for card in config.get("cards", []))
    page = INDEX.read_text(encoding="utf-8")
    INDEX.write_text(replace_cards_grid(page, cards_html), encoding="utf-8")
    print(f"Wrote {len(config.get('cards', []))} cards to {INDEX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
