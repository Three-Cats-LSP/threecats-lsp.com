from pathlib import Path
import re

s = Path("index.html").read_text(encoding="utf-8")
giw = s.find(">Get In Water</h2>")
chunk = s[giw - 1500 : giw + 800]
classes = re.findall(r'class="([^"]{10,120})"', chunk)
print("Classes near GIW:")
for c in classes:
    print(" ", c[:100])

# Find card start: look for About The App link before GIW
about = s.rfind('/get-in-water/about.html', 0, giw)
print("\nabout link at", about)
print(s[about - 400 : about + 1200])
