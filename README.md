# Three Cats LSP — Diver's Toolkit

Homepage and deployment hub for the **Three Cats LSP Diver's Toolkit** — free, open-source scuba apps and 3D-printed dive gadgets, built by divers for divers.

🌐 **Live site**: https://threecats-lsp.com

---

## Apps

| App | Web | APK | GitHub |
|-----|-----|-----|--------|
| **[LSP D-Planner](https://threecats-lsp.com/d-planner/)** | [Open](https://threecats-lsp.com/d-planner/) | [Download](https://threecats-lsp.com/d-planner/download.html) | [LSP_D-planner](https://github.com/Three-Cats-LSP/LSP_D-planner) |
| **[T-Viewer](https://threecats-lsp.com/t-viewer/)** | [Open](https://threecats-lsp.com/t-viewer/) | [Download](https://threecats-lsp.com/t-viewer/download.html) | [T-Viewer](https://github.com/Three-Cats-LSP/T-Viewer) |
| **[Get In Water](https://threecats-lsp.com/get-in-water/)** | [Open](https://threecats-lsp.com/get-in-water/) | [Download](https://threecats-lsp.com/get-in-water/download.html) | [Get-In-Water](https://github.com/Three-Cats-LSP/Get-In-Water) |

### LSP D-Planner
Technical and recreational decompression planner. Bühlmann ZHL-16C + GF, VPM-B, VPM-B/GFS, trimix, multi-gas, Rec/Tec modes. Export dive plans as TXT or PDF.

**Current version: 2.10.1**

### T-Viewer
Companion for LSP D-Planner exports. Open, read, edit, and share dive plan TXT/PDF files on Android or in the browser — syntax highlighting for deco schedules, gas labels, and warnings.

### Get In Water
Dive trip packing checklist. Master gear list, starter templates, per-trip checklists with quantities, notes, critical items, packing phases, tags, unpack mode, buddy copy, JSON backup, and TXT/PDF export. Android home-screen widget for pinned trip progress.

**Current version: 1.3.0**

---

## Typical workflow

1. **Plan** — build a dive profile in LSP D-Planner
2. **Export** — save the plan as TXT or PDF
3. **Review** — open the file in T-Viewer on your phone
4. **Pack** — use Get In Water to checklist your gear for the trip

---

## Site structure

| Path | Purpose |
|------|---------|
| `index.html` | Diver's Toolkit homepage |
| `gadgets.html` | 3D-printed dive gadgets |
| `d-planner/` | Synced LSP D-Planner web app + APK |
| `t-viewer/` | Synced T-Viewer web app + APK |
| `get-in-water/` | Synced Get In Water web app + APK |
| `.github/workflows/sync-apps.yml` | Pulls latest apps from upstream repos |

App folders are updated automatically when upstream repositories push to `main`. The workflow can also be triggered manually from the Actions tab (`sync-d-planner`, `sync-t-viewer`, `sync-get-in-water`, and APK sync jobs).

---

## Install any app on your phone

All three apps are progressive web apps (PWAs) and can be added to your home screen:

1. Open the app URL in your mobile browser
2. **Safari (iPhone / iPad):** Share → **Add to Home Screen**
3. **Chrome (Android):** **⋮** → **Install app** or **Add to Home screen**

Or install the Android APK from each app's download page for native features (file export, widgets, share targets).

---

## Support

LSP D-Planner, T-Viewer, and Get In Water are free and open-source. If they help your diving, consider [supporting development via PayPal](https://paypal.me/ThreeCatsLSP).

Follow [@threecats_lsp](https://www.instagram.com/threecats_lsp) on Instagram for updates.

---

## Disclaimer

These tools are aids for trained divers. They do not replace formal dive training, certification, or a calibrated dive computer. Always verify your own plans and gear. Use at your own risk.

---

*Three Cats LSP · Precision tools for scuba divers*
