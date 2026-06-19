# T-Viewer

A companion app for **[LSP D-Planner](https://github.com/Three-Cats-LSP/LSP_D-planner)** — open, read, edit, and share dive plan **TXT** and **PDF** files exported by LSP D-Planner on your phone or in the browser.

Part of the [Three Cats LSP](https://threecats-lsp.com) **Diver's Toolkit**.

🌐 **Web app**: https://threecats-lsp.com/t-viewer/

Also runs in any browser — no install required.

---

## Diver's Toolkit

| App | Purpose |
|-----|---------|
| **[LSP D-Planner](https://threecats-lsp.com/d-planner/)** | Decompression planning (Bühlmann, VPM-B, Rec/Tec) |
| **T-Viewer** | Open and share exported dive plan TXT/PDF files (this app) |
| **[Get In Water](https://threecats-lsp.com/get-in-water/)** | Trip packing checklists |

All apps live on the [Diver's Toolkit hub](https://threecats-lsp.com).

---

## Web App

Add T-Viewer to your home screen for quick access from Safari or Chrome.

**Installation:**
1. Open https://threecats-lsp.com/t-viewer/ on your phone, tablet, or computer
2. **Safari (iPhone / iPad):** Tap **Share** (square with arrow) → **Add to Home Screen** → **Add**
3. **Chrome (Android):** Tap **⋮** menu → **Install app** or **Add to Home screen** → confirm
4. **Chrome (desktop):** Click the install icon in the address bar, or **⋮** → **Install T-Viewer**

### Android APK

T-Viewer is also available as a native Android app built with Capacitor.

📲 **[Download APK](https://threecats-lsp.com/t-viewer/download.html)**

**APK installation:**
1. Open the download page on your Android device
2. Tap **Download APK**
3. Open the downloaded file from your Downloads folder
4. If prompted, allow *Install from unknown sources* in Settings
5. Install and launch T-Viewer

Export a dive plan as **TXT** or **PDF** from LSP D-Planner and share it directly into T-Viewer on Android.

---

## Features

### File support
- Open `.txt`, `.log`, `.plan`, `.div`, and **`.pdf`** files
- Receive shared files directly from LSP D-Planner on Android
- Drag and drop on desktop browser (web version)

### Text plans
- **Syntax highlighting** for deco logs:
  - Section headers (cyan / blue)
  - Parameter lines — `Algorithm :`, `Depth :`, `Deco Gas 1 :` etc. (teal)
  - Data rows — `Stp`, `Asc`, `Des` etc. (amber in dark / black in light)
  - Separator lines (dim)
  - Warning keywords (orange / red)
- **Edit mode** — modify file contents; save back to device or discard with confirmation
- No word wrap — long deco table rows scroll horizontally for clean alignment
- Copy and share text

### PDF plans
- View LSP D-Planner PDF exports in-app (PDF.js)
- Page navigation bar for multi-page documents

### Appearance & settings
- Dark and light theme — tap 🌙 / ☀️ to toggle
- Customizable colors — adjust syntax and UI colors per theme via the **COLORS** tab
- Font selector — System Default, Monospace, Roboto Mono, Source Code Pro, JetBrains Mono, Open Sans, Noto Sans
- Pinch-to-zoom — font size shown in top bar
- All settings persisted in `localStorage`

---

## UI

### Top bar

| Button | Action |
|--------|--------|
| Folder icon | Open a file |
| Copy icon | Copy all text to clipboard |
| Edit icon | Enter edit mode (text files) |
| Save icon | Save / download edited file (edit mode) |
| Share icon | Share current file |
| `?` | Open COLORS / ABOUT modal |
| Font size label | Current size (e.g. `15px`) — pinch to zoom |
| 🌙 / ☀️ | Toggle dark / light theme |

### `?` modal — COLORS tab *(opens first)*

- Font selector for the content area
- Dark / Light sub-tabs with live color editing
- Reset button per theme

### `?` modal — ABOUT tab

- App description and feature list
- **Links:** Diver's Toolkit hub, T-Viewer GitHub, T-Viewer APK, Thingiverse, Instagram, PayPal

---

## Syntax highlighting

| Class | Pattern | Dark | Light |
|-------|---------|------|-------|
| `.h` Header | All-caps lines (`DECO PLAN`, `GAS CONSUMPTION`) | cyan | blue |
| `.s` Separator | Lines of dashes / equals / dots | dim | grey |
| `.d` Data | Depth/time units (`60m`, `3:00`) | amber | black |
| `.w` Warning | `warn`, `caution`, `deco`, `stop` etc. | orange | red |
| `.l` Label | `Key : Value` parameter lines | teal | dark teal |

All colors are customizable via the COLORS tab.

---

## Repository structure

| Path | Purpose |
|------|---------|
| `index.html` | Self-contained web app |
| `manifest.json` | PWA manifest |
| `download.html` | Android APK download page |
| `android/` | Capacitor Android project |
| `Android Apk/` | Latest built APK (auto-updated by CI) |

---

## Deployment

Static single-file app served from [threecats-lsp.com/t-viewer/](https://threecats-lsp.com/t-viewer/). Android APK is built by GitHub Actions on push to `main` and synced to the homepage.

---

## Disclaimer

T-Viewer is a file viewer and editor. It does not perform decompression calculations. Always use a calibrated dive computer and formal dive training. Use at your own risk.

---

*Developed by Three Cats LSP · [@threecats_lsp](https://www.instagram.com/threecats_lsp)*
