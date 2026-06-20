#!/usr/bin/env python3
"""Generate styled about.html pages from app README files."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_DIR = ROOT / "scripts" / "readmes"

APPS = [
    {
        "slug": "d-planner",
        "title": "LSP D-Planner",
        "icon_src": "/d-planner/icon-192.png",
        "app_url": "/d-planner/",
        "readme_names": ("d-planner.md",),
        "sibling_readme": ROOT.parent / "LSP_D-planner" / "README.md",
        "out": ROOT / "d-planner" / "about.html",
    },
    {
        "slug": "d-planner-ccr",
        "title": "LSP D-Planner + CCR",
        "icon_src": "/d-planner-ccr/icon-192.png",
        "app_url": "/d-planner-ccr/",
        "readme_names": ("d-planner-ccr.md",),
        "sibling_readme": ROOT.parent / "LSP_D-planner-CCR" / "README.md",
        "out": ROOT / "d-planner-ccr" / "about.html",
    },
    {
        "slug": "t-viewer",
        "title": "T-Viewer",
        "icon_src": "/t-viewer/icon-192.png",
        "app_url": "/t-viewer/",
        "readme_names": ("t-viewer.md",),
        "sibling_readme": ROOT.parent / "T-Viewer" / "README.md",
        "out": ROOT / "t-viewer" / "about.html",
    },
    {
        "slug": "get-in-water",
        "title": "Get In Water",
        "icon_src": "/get-in-water/icon-192.png",
        "app_url": "/get-in-water/",
        "readme_names": ("get-in-water.md",),
        "sibling_readme": ROOT.parent / "Get-In-Water" / "README.md",
        "out": ROOT / "get-in-water" / "about.html",
    },
]


def resolve_readme(app: dict) -> Path:
    for name in app["readme_names"]:
        cached = README_DIR / name
        if cached.is_file():
            return cached
    sibling = app["sibling_readme"]
    if sibling.is_file():
        return sibling
    raise FileNotFoundError(f"No README for {app['slug']}")


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def is_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and "|" in s[1:-1]


def is_table_sep(line: str) -> bool:
    s = line.strip().strip("|")
    if not s:
        return False
    return all(part.strip().replace(":", "") == "---" or part.strip() == "---" for part in s.split("|"))


def md_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    in_ul = False
    in_ol = False
    in_pre = False
    pre_buf: list[str] = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()

        if in_pre:
            if raw.startswith("```"):
                out.append("<pre><code>" + html.escape("\n".join(pre_buf)) + "</code></pre>")
                pre_buf = []
                in_pre = False
            else:
                pre_buf.append(raw)
            i += 1
            continue

        if raw.startswith("```"):
            close_lists()
            in_pre = True
            i += 1
            continue

        if is_table_row(raw):
            close_lists()
            table_lines = []
            while i < len(lines) and is_table_row(lines[i].rstrip()):
                table_lines.append(lines[i].rstrip())
                i += 1
            if len(table_lines) >= 2 and is_table_sep(table_lines[1]):
                header = [c.strip() for c in table_lines[0].strip("|").split("|")]
                body_rows = table_lines[2:]
                out.append("<table><thead><tr>")
                for cell in header:
                    out.append(f"<th>{inline_md(cell)}</th>")
                out.append("</tr></thead><tbody>")
                for row in body_rows:
                    cells = [c.strip() for c in row.strip("|").split("|")]
                    out.append("<tr>")
                    for cell in cells:
                        out.append(f"<td>{inline_md(cell)}</td>")
                    out.append("</tr>")
                out.append("</tbody></table>")
            continue

        if not raw.strip():
            close_lists()
            i += 1
            continue

        if raw.strip() == "---":
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", raw)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline_md(m.group(2))}</h{level}>")
            i += 1
            continue

        if raw.startswith("> "):
            close_lists()
            out.append(f"<blockquote><p>{inline_md(raw[2:])}</p></blockquote>")
            i += 1
            continue

        if re.match(r"^[-*]\s+", raw):
            if not in_ul:
                close_lists()
                out.append("<ul>")
                in_ul = True
            item = re.sub(r"^[-*]\s+", "", raw)
            out.append(f"<li>{inline_md(item)}</li>")
            i += 1
            continue

        if re.match(r"^\d+\.\s+", raw):
            if not in_ol:
                close_lists()
                out.append("<ol>")
                in_ol = True
            item = re.sub(r"^\d+\.\s+", "", raw)
            out.append(f"<li>{inline_md(item)}</li>")
            i += 1
            continue

        close_lists()
        out.append(f"<p>{inline_md(raw)}</p>")
        i += 1

    close_lists()
    if in_pre and pre_buf:
        out.append("<pre><code>" + html.escape("\n".join(pre_buf)) + "</code></pre>")
    return "\n".join(out)


def page_html(app: dict, body: str) -> str:
    title = app["title"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>About · {html.escape(title)} · Three Cats LSP</title>
  <meta name="description" content="About {html.escape(title)} — part of the Three Cats LSP Diver's Toolkit."/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="/about.css"/>
</head>
<body>
  <div class="page-bg" aria-hidden="true"></div>
  <div class="page-dots" aria-hidden="true"></div>
  <header class="site-header">
    <a class="logo-link" href="/">
      <span class="logo-mark"><img src="{app["icon_src"]}" alt="{html.escape(title)}" width="40" height="40"/></span>
      <span>Diver's Toolkit</span>
    </a>
    <div class="header-actions">
      <a class="btn btn-ghost" href="/">All apps</a>
      <a class="btn btn-primary" href="{app["app_url"]}">Open App</a>
    </div>
  </header>
  <main class="about-main">
    <div class="about-card">
      <p class="about-eyebrow">About {html.escape(title)}</p>
      <article class="prose">
{body}
      </article>
    </div>
  </main>
  <footer class="site-footer">Three Cats LSP · Diver's Toolkit</footer>
</body>
</html>
"""


def main() -> None:
    for app in APPS:
        md = resolve_readme(app).read_text(encoding="utf-8")
        body = md_to_html(md)
        app["out"].write_text(page_html(app, body), encoding="utf-8", newline="\n")
        print(f"Wrote {app['out'].relative_to(ROOT)}")


if __name__ == "__main__":
    main()
