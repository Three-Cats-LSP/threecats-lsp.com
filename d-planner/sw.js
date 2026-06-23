// LSP D-Planner — Service Worker
// Network-first for HTML (always fresh), cache-first for static assets.
// Bump CACHE_VERSION on every deploy to force old SW replacement.

const CACHE_VERSION = 'lsp-dplanner-v2.40.01';

// These are never cached — always fetched live or passed through
const NEVER_CACHE = [
  '.apk',
  '.aab',
  'raw.githubusercontent.com'
];

function shouldNeverCache(url) {
  return NEVER_CACHE.some(pattern => url.href.includes(pattern));
}

function isHTMLRequest(request) {
  const accept = request.headers.get('Accept') || '';
  return accept.includes('text/html');
}

function getAppBasePath() {
  const p = self.location.pathname || '/';
  if (p.includes('/d-planner')) return '/d-planner/';
  if (p.includes('/LSP_D-planner')) return '/LSP_D-planner/';
  const swDir = p.replace(/[^/]*$/, '');
  return swDir || '/LSP_D-planner/';
}

const APP_BASE = getAppBasePath();
const OFFLINE_INDEX = APP_BASE + 'index.html';

// Required for offline/PWA startup after v2.40.00 Tier-3 split (Issue #10)
const PRECACHE_ASSETS = [
  OFFLINE_INDEX,
  APP_BASE + 'capacitor-bridge.js',
  APP_BASE + 'zhl-engine-bundle.js',
  APP_BASE + 'zhl-worker-bridge.js',
  APP_BASE + 'zhl-schedule-worker.js',
  APP_BASE + 'vendor/jspdf.umd.min.js',
  APP_BASE + 'manifest.json',
  APP_BASE + 'icon-192.png',
  APP_BASE + 'icon-512.png',
];

// Install — skip waiting immediately so new SW takes over fast
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(PRECACHE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate — delete ALL old caches, claim clients immediately
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key !== CACHE_VERSION)
          .map(key => {
            console.log('[SW] Deleting old cache:', key);
            return caches.delete(key);
          })
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Fetch strategy:
//   - APK / external URLs: pass through, never intercept
//   - HTML (index.html, navigation): network-first, cache fallback
//   - Everything else (JS, CSS, fonts, etc.): cache-first, network fallback
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Never intercept cross-origin or APK requests
  if (url.origin !== self.location.origin) return;
  if (shouldNeverCache(url)) return;

  // Network-first for HTML — ensures index.html is always up to date
  if (isHTMLRequest(event.request) || url.pathname.endsWith('.html') || url.pathname.endsWith('/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response.ok) {
            // Update cache with fresh version
            const clone = response.clone();
            caches.open(CACHE_VERSION).then(cache => {
              const key = new Request(url.origin + url.pathname);
              cache.put(key, clone);
            });
          }
          return response;
        })
        .catch(() => {
          // Network failed — serve cached version as offline fallback
          return caches.match(event.request, { ignoreSearch: true })
            .then(match => match || caches.match(OFFLINE_INDEX, { ignoreSearch: true }));
        })
    );
    return;
  }

  // Cache-first for all other static assets
  event.respondWith(
    caches.match(event.request, { ignoreSearch: true })
      .then(cached => {
        if (cached) return cached;
        return fetch(event.request)
          .then(response => {
            if (response.ok && url.pathname.startsWith(APP_BASE)) {
              const clone = response.clone();
              const cacheKey = new Request(url.origin + url.pathname);
              caches.open(CACHE_VERSION).then(cache => cache.put(cacheKey, clone));
            }
            return response;
          });
      })
  );
});
