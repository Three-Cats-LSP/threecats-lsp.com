# Get In Water

Get In Water is a free dive-trip packing checklist app. It helps you keep a master gear list, create trip-specific packing lists, track what is packed, and export checklists as TXT or PDF.

- Live app: https://threecats-lsp.com/get-in-water/
- Android APK: https://threecats-lsp.com/get-in-water/download.html
- Repository: https://github.com/Three-Cats-LSP/Get-In-Water
- Toolkit hub: https://threecats-lsp.com
- Current version: 1.4.2
- License: MIT

## What It Is For

Plan the dive in LSP D-Planner+. Read the plan in T-Viewer. Pack for the trip with Get In Water.

Use it for:

- weekend recreational dives;
- technical dive trips;
- underwater photography trips;
- travel packing;
- team or buddy gear checks;
- reusable personal templates.

## Three Cats LSP Toolkit

| App | Purpose | Live app |
| --- | --- | --- |
| LSP D-Planner+ | OC, CCR, pSCR, rec and tech decompression planning | https://threecats-lsp.com/d-planner-plus/ |
| T-Viewer | Dive-plan TXT/PDF viewer and editor | https://threecats-lsp.com/t-viewer/ |
| Get In Water | Dive trip packing lists and exportable checklists | https://threecats-lsp.com/get-in-water/ |

## Features

### Master Gear List

- Maintain one master list of your normal gear.
- Add item notes and quantities.
- Edit, reorder, and remove items.
- Use the master list as the starting point for new trips.

### Templates

- Built-in starter templates:
  - Recreational diver
  - Underwater photographer
  - Technical diver
- Reset built-in templates when needed.
- Create your own reusable templates.

### Trip Checklists

- Create named trips.
- Start from the master list or a template.
- Tick items off as you pack.
- Track completion with a progress indicator.
- Keep trip-specific notes and quantities.

### Export And Sharing

- Export TXT packing lists.
- Export formatted PDF packing lists.
- Copy checklist text.
- Share through Android or browser share targets.

### Optional Cloud Sync

- Optional Google sign-in.
- Sync trips and lists between browser and Android.
- Works fully offline without an account.
- Manual Sync button for controlled push/pull.
- Conflict handling for first sign-in.

Cloud sync is optional. Local-only use is fully supported.

## Install

### Web / PWA

Open:

```text
https://threecats-lsp.com/get-in-water/
```

Install from your browser:

| Platform | Install path |
| --- | --- |
| iPhone / iPad Safari | Share -> Add to Home Screen |
| Android Chrome | Menu -> Install app or Add to Home Screen |
| Desktop Chrome / Edge / Vivaldi | Install icon in address bar |

### Android APK

Download:

```text
https://threecats-lsp.com/get-in-water/download.html
```

Requirements:

- Android 5.0+ / API 21+
- Allow "Install unknown apps" for your browser or file manager

## Typical Workflow

1. Maintain your master gear list.
2. Create a trip checklist.
3. Remove gear you do not need for that trip.
4. Add trip-specific gear, notes, and quantities.
5. Tick items off while packing.
6. Export or share the checklist.

## Contributor Notes

Optional Google sync uses Firebase Auth and Firestore. Contributor setup uses local Firebase config files and GitHub secrets for Android builds.

Key files:

- `firebase-config.example.js`
- `.env.example`
- `firestore.rules`
- `android/`

## Safety Notice

Get In Water is a packing aid. It cannot know whether your equipment is appropriate, serviced, analyzed, charged, or safe for a specific dive. Always check life-support equipment personally and follow your training and team procedures.

## Links

- LSP D-Planner+: https://threecats-lsp.com/d-planner-plus/
- T-Viewer: https://threecats-lsp.com/t-viewer/
- Get In Water APK: https://threecats-lsp.com/get-in-water/download.html
- GitHub organization: https://github.com/Three-Cats-LSP
- Instagram: https://www.instagram.com/threecats_lsp
