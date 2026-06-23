import re
from pathlib import Path

s = Path("index.html").read_text(encoding="utf-8")
for title in ["LSP D-Planner", "T-Viewer", "Get In Water"]:
    i = s.find(f">{title}</h2>")
    if i < 0:
        print(f"NOT FOUND: {title}")
        continue
    start = s.rfind('group relative flex flex-col', 0, i)
    start = s.rfind("<div", 0, start)
    candidates = [x for x in [
        s.find('group relative flex flex-col', i + 10),
        s.find("</section>", i),
    ] if x > 0]
    nxt = min(candidates) if candidates else i + 2000
    card = s[start:nxt]
    Path(f"scripts/card-{title.replace(' ', '-').lower()}.snippet.html").write_text(card, encoding="utf-8")
    print(f"{title}: {len(card)} chars -> scripts/card-{title.replace(' ', '-').lower()}.snippet.html")
