# Get In Water

Dive trip packing checklist app — part of the [Three Cats LSP](https://threecats-lsp.com) **Diver's Toolkit**.

Maintain a **master gear list**, create **per-trip checklists**, tick items off as you pack, and export TXT or PDF for printing or sharing. Use it alongside [LSP D-Planner+](https://threecats-lsp.com/d-planner-plus/) — plan the dive, then pack for it.

🌐 **Live app:** https://threecats-lsp.com/get-in-water/  
📲 **Android APK:** https://threecats-lsp.com/get-in-water/download.html  

**Current version: 1.4.2**

---

## Diver's Toolkit

| App | Description | Link |
|-----|-------------|------|
| **[LSP D-Planner+](https://threecats-lsp.com/d-planner-plus/)** | Unified OC + CCR decompression planning — Bühlmann, VPM-B, Rec/Tec | [Repo](https://github.com/Three-Cats-LSP/LSP_D-planner-plus) |
| **[T-Viewer](https://threecats-lsp.com/t-viewer/)** | Open and share exported dive plan TXT/PDF files | — |
| **Get In Water** ← *this app* | Dive trip packing checklists | [Repo](https://github.com/Three-Cats-LSP/Get-In-Water) |

All apps at the [Diver's Toolkit hub](https://threecats-lsp.com).

---

## Features

### Master List & Templates
- **Master gear list** — your default packing list; new trips start from it or any saved template
- **Starter templates** — Recreational, Underwater Photographer, Technical Diver (built-in, resettable)
- Edit under **Settings → Templates**

### Per-Trip Checklists
- Create named trips from master list or a template
- Tick items off as you pack — progress bar tracks completion
- Items carry notes and quantity

### Export
- **TXT** — plain text gear list to clipboard or Downloads
- **PDF** — formatted packing list with trip name, date, and item notes
- Share via any Android share target (WhatsApp, email, etc.)

### Cloud sync (optional)
- **Sign in with Google** to sync checklists between the web app and Android
- **Offline-first** — works fully without an account; sync when signed in
- **Home screen Sync button** — manual sync without reloading the app
- Start packing on your phone, finish on desktop (or vice versa)
- Configure Firebase once — see [Cloud sync setup](#cloud-sync-setup) for contributors

### Android Native Features
- Full offline support — no internet needed after install
- Home-screen launcher name **GiW** (short label under the icon)
- Edge-to-edge layout, light/dark theme
- Export TXT/PDF to app storage, then share via the system sheet (Downloads when the device allows)

---

## Web App

Open https://threecats-lsp.com/get-in-water/ in any modern browser.

**Install as PWA:**
1. **Safari (iPhone/iPad):** Share → Add to Home Screen → Add
2. **Chrome (Android):** ⋮ → Install app / Add to Home Screen → confirm
3. **Chrome (desktop):** Click install icon in address bar

---

## Android App

Built with [Capacitor](https://capacitorjs.com). Direct APK — no Play Store required.

**Requirements:** Android 5.0+ (API 21)

**Install:**
1. Download APK from https://threecats-lsp.com/get-in-water/download.html
2. Allow "Install from unknown sources" in Android settings
3. Open the downloaded APK and install

---

## Cloud sync setup

Optional Google sign-in uses [Firebase](https://firebase.google.com) (Auth + Firestore). See [`.env.example`](.env.example) for one-time console steps:

1. Create a Firebase project and enable **Google** sign-in
2. Create Firestore and deploy [`firestore.rules`](firestore.rules)
3. Copy web config into local `firebase-config.js` (from [`firebase-config.example.js`](firebase-config.example.js); file is gitignored)
4. Add Android app → `google-services.json` in `android/app/` (not committed)
5. Ensure `android/variables.gradle` has `rgcfaIncludeGoogle = true` (required for Google Sign-In in APK)
6. Register SHA-1 fingerprints for debug/release keystores
7. GitHub secrets: `GOOGLE_SERVICES_JSON` (base64 of `google-services.json`), `FIREBASE_WEB_CONFIG` (base64 of `firebase-config.js`)

**Manual test checklist**

| Test | Expected |
|------|----------|
| Signed out | All features work locally; no cloud calls |
| Web sign-in | Trip created on desktop appears on phone after sync |
| Android sign-in | Ticked items on phone visible on web |
| Offline edit | Changes push when back online |
| First sign-in conflict | Dialog: keep device / use cloud / merge trips |
| Home Sync button | Pulls/pushes without app reload |
| Sign out | Local data kept; cloud listener stops |

---

## License

MIT — free to use, modify, and distribute. Optional Google account for cloud sync; no ads, no subscription.

---

*Three Cats LSP · [threecats-lsp.com](https://threecats-lsp.com)*
