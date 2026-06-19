# Get In Water

Dive trip packing checklist — a companion app in the [Three Cats LSP](https://threecats-lsp.com) **Diver's Toolkit**.

Maintain a **master gear list**, create **per-trip checklists**, tick items off as you pack, and export **TXT** or **PDF** for printing. Works alongside **[LSP D-Planner](https://threecats-lsp.com/d-planner/)** — plan the dive, then pack for it.

🌐 **Web app**: https://threecats-lsp.com/get-in-water/

**Current version: 1.3.0**

---

## Diver's Toolkit

| App | Purpose |
|-----|---------|
| **[LSP D-Planner](https://threecats-lsp.com/d-planner/)** | Decompression planning (Bühlmann, VPM-B, Rec/Tec) |
| **[T-Viewer](https://threecats-lsp.com/t-viewer/)** | Open and share exported dive plan TXT/PDF files |
| **Get In Water** | Trip packing checklists (this app) |

All apps live on the [Diver's Toolkit hub](https://threecats-lsp.com).

---

## Features

### Master gear list & templates
- **Master gear list** — your default packing list; new trips can start from it or any saved template
- Edit under **Settings → Templates** (master gear card or full editor)
- **Starter templates** — Recreational, Underwater photographer, Technical diver (built-in, resettable)
- Create, copy, edit, and delete custom templates
- Add template items to the master gear list with one tap
- **Export** master gear as TXT or PDF from the gear editor

### Trip checklists
- **New trip** — pick **Master gear list** or any template from Settings → Templates (checks start cleared)
- **Multi-day trips** — start/finish dates, or **One day trip**
- **Trip location** and **#tags** on the home screen and trip header
- **Pre-dive / post-dive phases** — filter items by when to pack (night before, at dock, before first dive, after last dive)
- **Critical items** banner — must-not-forget gear highlighted at the top
- **Quantities** — track packed count vs total (e.g. 2× spare O-ring)
- **Item notes** — nitrox mix, dry bag #, etc.
- **Bag grouping** — carry-on, checked bag, camera case, boat bin
- Per-trip categories and trip-only items without changing the master list
- **Unpack mode** — reverse checklist after the trip (toggle on trip subbar)
- **Return mode** — separate homeward packing checklist when heading home (toggle on trip subbar)
- **Buddy copy** — share a subset of categories with checks cleared
- Duplicate, pin, archive, and delete trips
- **Celebration overlay** when everything is packed (outbound or return)

### Home screen
- Search trips, tags, locations, and gear names
- Sort by newest, date, progress, or name
- **Filter menu** — hide completed trips; show archived trips
- Countdown to trip start date
- Pin a trip to the top of the list

### Export & backup
- **Export menu** on each trip and in the master gear editor — one dropdown, all formats:
  - Full checklist (TXT / PDF)
  - Remaining items (TXT / PDF)
  - By bag (TXT / PDF) — grouped by carry-on, checked, camera, boat, etc.
- **Share remaining list** — quick share from the trip ⋮ menu
- **JSON backup** — under **Settings → About**; export all trips, master gear, and templates, or import on a new device

### App experience
- LSP D-Planner design system — dark/light theme, card layout, bubble background
- Theme-aware app icon (light/dark)
- **PWA** — install from the browser; offline use via service worker
- **Android home-screen widget** — pinned trip packing progress at a glance
- All data stored locally in `localStorage` (`giw_v1`) — no account, no server

---

## Web & Android

### Web / PWA
Open https://threecats-lsp.com/get-in-water/ in any modern browser. Install as a PWA for home-screen access and offline packing lists.

**Installation:**
1. Open https://threecats-lsp.com/get-in-water/ on your phone, tablet, or computer
2. **Safari (iPhone / iPad):** Tap **Share** (square with arrow) → **Add to Home Screen** → **Add**
3. **Chrome (Android):** Tap **⋮** menu → **Install app** or **Add to Home screen** → confirm
4. **Chrome (desktop):** Click the install icon in the address bar, or **⋮** → **Install Get In Water**

### Android APK
📲 **[Download APK](https://threecats-lsp.com/get-in-water/download.html)**

Built with Capacitor. APK is updated automatically by GitHub Actions on each release.

**APK installation:**
1. Open the download page on your Android device
2. Tap **Download APK**
3. Open the downloaded file
4. Allow *Install from unknown sources* if prompted
5. Install and launch Get In Water

---

## UI overview

Open **?** from the home screen for settings. Two tabs:

| Tab | Description |
|-----|-------------|
| **Templates** | Master gear list card, starter templates, template editor, add items to master gear |
| **About** | App info, JSON backup export/import, Diver's Toolkit links |

| Screen | Description |
|--------|-------------|
| **Home** | Trip list with progress, search/sort, **+** new trip (name, template, dates, tags), filter menu (hide completed / show archived), **?** settings |
| **Trip** | Phase tabs; **Unpack** / **Return** toggles; checklist by category; critical banner; qty controls; **+** add card; **Export** dropdown (TXT/PDF); **⋮** menu (details, pin, buddy copy, share, reset, archive, delete) |

---

## Repository structure

| Path | Purpose |
|------|---------|
| `index.html` | Self-contained web app |
| `manifest.json` | PWA manifest |
| `sw.js` | Service worker — offline caching |
| `capacitor-bridge.js` | Android file export bridge |
| `download.html` | APK download page |
| `icon-192.png`, `icon-512.png` | App icons (dark theme) |
| `icon-192-light.png`, `icon-512-light.png` | App icons (light theme) |
| `android/` | Capacitor Android project (incl. packing widget) |
| `Android Apk/` | Latest built APK (auto-updated by CI) |

---

## Build APK locally

```bash
npm ci
mkdir -p www
cp index.html manifest.json sw.js capacitor-bridge.js icon-192.png icon-512.png icon-192-light.png icon-512-light.png www/
npx cap sync android
cd android && ./gradlew assembleDebug
```

---

## Deployment

Static single-file app served from GitHub Pages via [threecats-lsp.com/get-in-water/](https://threecats-lsp.com/get-in-water/). Pushes to `main` trigger APK build and homepage sync through the Three Cats LSP site pipeline.

---

## Disclaimer

Get In Water is a packing checklist only. It does not replace formal dive training, certification, or a calibrated dive computer. Always verify your own gear and dive plans. Use at your own risk.

---

*Developed by Three Cats LSP · [@threecats_lsp](https://www.instagram.com/threecats_lsp)*
