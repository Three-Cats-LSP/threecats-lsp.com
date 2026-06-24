#!/usr/bin/env python3
"""Generate knowledge-base/index.html from scripts/knowledge-base-resources.json.

Fetches public metadata for YouTube (oEmbed) and Instagram (og: tags).
Add URLs to the JSON file, then run:

    python scripts/generate-knowledge-base.py

Optional per-item overrides in JSON: title, description, author.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESOURCES = Path(__file__).resolve().parent / "knowledge-base-resources.json"
OUT = ROOT / "knowledge-base" / "index.html"
USER_AGENT = "Mozilla/5.0 (compatible; ThreeCatsLSP-KnowledgeBase/1.0)"


def fetch_bytes(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_text(url: str) -> str:
    return fetch_bytes(url).decode("utf-8", "replace")


def normalize_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url.strip())
    host = (parsed.netloc or "").lower().removeprefix("www.")
    path = parsed.path.rstrip("/")

    if host in {"youtube.com", "m.youtube.com", "youtu.be"}:
        video_id = None
        if host == "youtu.be":
            video_id = path.lstrip("/").split("/")[0]
        else:
            qs = urllib.parse.parse_qs(parsed.query)
            if "v" in qs:
                video_id = qs["v"][0]
            elif path.startswith("/shorts/"):
                video_id = path.split("/")[2]
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"

    if host == "instagram.com":
        m = re.match(r"/(reel|p|tv)/([^/]+)", path)
        if m:
            return f"https://www.instagram.com/{m.group(1)}/{m.group(2)}/"

    return urllib.parse.urlunparse(
        (parsed.scheme or "https", parsed.netloc, path + "/", "", "", "")
    )


def platform_for(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if "instagram.com" in host:
        return "instagram"
    return "link"


def first_line(text: str, max_len: int = 100) -> str:
    line = text.strip().splitlines()[0].strip() if text.strip() else ""
    if len(line) <= max_len:
        return line
    cut = line[: max_len - 1].rsplit(" ", 1)[0]
    return cut + "…"


def summarize(text: str, max_len: int = 200) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) <= max_len:
        return text
    cut = text[: max_len - 1].rsplit(" ", 1)[0]
    return cut + "…"


def meta_tag(page_html: str, prop: str) -> str | None:
    m = re.search(
        rf'<meta[^>]+property="{re.escape(prop)}"[^>]+content="([^"]*)"',
        page_html,
        re.I,
    )
    if not m:
        m = re.search(
            rf'content="([^"]*)"[^>]+property="{re.escape(prop)}"',
            page_html,
            re.I,
        )
    return html.unescape(m.group(1)) if m else None


def fetch_youtube(url: str) -> dict[str, str]:
    api = (
        "https://www.youtube.com/oembed?format=json&url="
        + urllib.parse.quote(url, safe="")
    )
    data = json.loads(fetch_bytes(api))
    return {
        "title": data.get("title", "").strip(),
        "author": data.get("author_name", "").strip(),
        "description": "",
    }


def fetch_instagram(url: str) -> dict[str, str]:
    page = fetch_text(url)
    og_desc = meta_tag(page, "og:description") or ""
    og_title = meta_tag(page, "og:title") or ""

    author = ""
    caption = ""

    m = re.search(r"-\s*@?([\w.]+)\s+on\s+[^:]+:\s*(.+)$", og_desc, re.S)
    if m:
        author = m.group(1).strip()
        caption = m.group(2).strip().strip('"')
    elif og_title:
        m2 = re.search(
            r"on Instagram:\s*(?:&quot;|\"?)(.+?)(?:&quot;|\"?)\s*$",
            og_title,
            re.S,
        )
        if m2:
            caption = html.unescape(m2.group(1)).strip()
        m3 = re.search(r"^([\w.]+)\s+on Instagram:", og_title)
        if m3:
            author = m3.group(1).strip()

    caption = html.unescape(caption)
    caption = re.sub(r"#[\w]+", "", caption)
    caption = caption.strip()

    title = instagram_title(caption) if caption else first_line(og_title, 80)
    return {
        "title": title,
        "author": author,
        "description": summarize(caption) if caption else "",
    }


def instagram_title(caption: str) -> str:
    """Short display title from an Instagram caption."""
    for sep in ("\n\n", "\n", ". ", "! "):
        if sep in caption:
            head = caption.split(sep, 1)[0].strip()
            if len(head) >= 8:
                return first_line(head, 80)
    return first_line(caption, 80)


def fetch_metadata(url: str) -> dict[str, str]:
    platform = platform_for(url)
    try:
        if platform == "youtube":
            return fetch_youtube(url)
        if platform == "instagram":
            return fetch_instagram(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
        print(f"warning: could not fetch metadata for {url}: {exc}", file=sys.stderr)
    return {"title": url, "author": "", "description": ""}


def parse_item(raw: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw, str):
        return {"url": raw}
    return dict(raw)


def resolve_item(item: dict[str, Any], badge: str) -> dict[str, str]:
    url = normalize_url(item["url"])
    fetched = fetch_metadata(url)

    title = (item.get("title") or fetched["title"] or url).strip()
    author = (item.get("author") or fetched["author"] or "").strip()
    description = (item.get("description") or fetched["description"] or "").strip()

    platform = platform_for(url)
    if platform == "youtube":
        meta = f"{author} · YouTube" if author else "YouTube"
    elif platform == "instagram":
        meta = f"@{author} · Instagram" if author else "Instagram"
    else:
        host = urllib.parse.urlparse(url).netloc.removeprefix("www.")
        meta = host

    return {
        "url": url,
        "badge": badge,
        "title": title,
        "meta": meta,
        "description": description,
    }


def render_resource(item: dict[str, str]) -> str:
    desc_html = ""
    if item["description"]:
        desc_html = (
            f'\n              <span class="resource-desc">{html.escape(item["description"])}</span>'
        )
    return f"""          <li>
            <a class="resource-link" href="{html.escape(item["url"])}" rel="noopener noreferrer" target="_blank">
              <span class="resource-title"><span class="resource-badge">{html.escape(item["badge"])}</span> {html.escape(item["title"])}</span>
              <span class="resource-meta">{html.escape(item["meta"])}</span>{desc_html}
            </a>
          </li>"""


def render_page(data: dict[str, Any], sections_html: list[str]) -> str:
    intro = html.escape(data.get("intro", ""))
    body_sections = "\n\n".join(sections_html)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Knowledge Base · Three Cats LSP</title>
  <meta name="description" content="Useful links and knowledge for divers — videos, reels, and reading to become a better diver. Part of the Three Cats LSP Diver's Toolkit."/>
  <link rel="canonical" href="https://threecats-lsp.com/knowledge-base/"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="/about.css"/>
  <style>
    .resource-list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .resource-list li {{ margin: 0; }}
    .resource-link {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 14px 16px;
      border: 1px solid var(--border);
      border-radius: 12px;
      text-decoration: none;
      background: rgba(0, 0, 0, 0.2);
      transition: border-color 0.2s, background 0.2s;
    }}
    .resource-link:hover {{
      border-color: var(--primary);
      background: var(--primary-dim);
    }}
    .resource-title {{
      font-weight: 600;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.95rem;
    }}
    .resource-meta {{
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .resource-desc {{
      font-size: 0.85rem;
      color: var(--muted);
      line-height: 1.5;
    }}
    .resource-badge {{
      display: inline-block;
      font-size: 0.65rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      padding: 2px 7px;
      border-radius: 4px;
      background: var(--primary-dim);
      color: var(--primary);
      flex-shrink: 0;
    }}
    .intro-note {{
      font-size: 0.9rem;
      color: var(--muted);
      margin-bottom: 1.5rem;
      padding: 12px 14px;
      border-left: 3px solid var(--primary);
      background: var(--primary-dim);
      border-radius: 0 8px 8px 0;
    }}
  </style>
</head>
<body>
  <div class="page-bg" aria-hidden="true"></div>
  <div class="page-dots" aria-hidden="true"></div>
  <header class="site-header">
    <a class="logo-link" href="/">
      <span class="logo-mark"><img src="/assets/Just%20Cats.png" alt="Three Cats LSP" width="40" height="40"/></span>
      <span>Diver's Toolkit</span>
    </a>
    <div class="header-actions">
      <a class="btn btn-ghost" href="/">All apps</a>
    </div>
  </header>
  <main class="about-main">
    <div class="about-card">
      <p class="about-eyebrow">Knowledge Base</p>
      <article class="prose">
        <h1>Knowledge Base</h1>
        <p class="intro-note">{intro}</p>

{body_sections}

        <hr>
        <p>More materials will be added over time. Part of the <a href="https://threecats-lsp.com">Three Cats LSP Diver's Toolkit</a>.</p>
      </article>
    </div>
  </main>
  <footer class="site-footer">Three Cats LSP · Diver's Toolkit</footer>
</body>
</html>
"""


def main() -> None:
    data = json.loads(RESOURCES.read_text(encoding="utf-8"))
    sections_html: list[str] = []

    for section in data.get("sections", []):
        badge = section.get("badge", "Link")
        items = [resolve_item(parse_item(raw), badge) for raw in section.get("items", [])]
        if not items:
            continue
        rows = "\n".join(render_resource(item) for item in items)
        sections_html.append(
            f"""        <h2>{html.escape(section.get("title", "Links"))}</h2>
        <ul class="resource-list">
{rows}
        </ul>"""
        )

    OUT.write_text(render_page(data, sections_html), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(sections_html)} sections)")


if __name__ == "__main__":
    main()
