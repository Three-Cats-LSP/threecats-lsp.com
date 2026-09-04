const CACHE_NAME = 'giw-v1.4.7';

function getAppBasePath() {
  const p = self.location.pathname || '/';
  if (p.includes('/get-in-water/')) return '/get-in-water/';
  if (p.includes('/Get-In-Water/')) return '/Get-In-Water/';
  const swDir = p.replace(/[^/]*$/, '');
  return swDir || '/get-in-water/';
}

const APP_BASE = getAppBasePath();
const OFFLINE_INDEX = APP_BASE + 'index.html';
const ASSETS = [
  APP_BASE,
  OFFLINE_INDEX,
  APP_BASE + 'manifest.json',
  APP_BASE + 'sw.js',
  APP_BASE + 'capacitor-bridge.js',
  APP_BASE + 'backup-sanitize.js',
  APP_BASE + 'firebase-config.js',
  APP_BASE + 'sync.js',
  APP_BASE + 'vendor/firebase/firebase-app-compat.js',
  APP_BASE + 'vendor/firebase/firebase-auth-compat.js',
  APP_BASE + 'vendor/firebase/firebase-firestore-compat.js',
  APP_BASE + 'vendor/jspdf.umd.min.js',
  APP_BASE + 'vendor/fonts/DejaVuSans.ttf',
  APP_BASE + 'vendor/fonts/DejaVuSans-Bold.ttf',
  APP_BASE + 'icon-192.png',
  APP_BASE + 'icon-512.png',
  APP_BASE + 'icon-192-light.png',
  APP_BASE + 'icon-512-light.png'
];

const NETWORK_ONLY = [
  'firebaseapp.com',
  'googleapis.com',
  'gstatic.com',
  'google.com'
];

function isFirebaseRequest(url) {
  return NETWORK_ONLY.some(host => url.hostname.includes(host));
}

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache =>
        Promise.allSettled(
          ASSETS.map(url =>
            cache.add(url).catch(err => console.warn('[SW] precache skipped:', url, err))
          )
        )
      )
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function isIconAsset(url) {
  return url.pathname.startsWith(APP_BASE) && /\/icon-\d+/.test(url.pathname);
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
  if (isFirebaseRequest(url)) {
    e.respondWith(fetch(e.request));
    return;
  }
  if (e.request.mode === 'navigate' || (e.request.headers.get('Accept') || '').includes('text/html')) {
    e.respondWith(
      fetch(e.request)
        .then(response => {
          if (response.ok && url.pathname.startsWith(APP_BASE)) {
            const clone = response.clone();
            e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(new Request(url.origin + url.pathname), clone)));
          }
          return response;
        })
        .catch(() => caches.match(e.request, { ignoreSearch: true })
          .then(cached => cached || caches.match(OFFLINE_INDEX, { ignoreSearch: true })))
    );
    return;
  }
  if (isIconAsset(url)) {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
    return;
  }
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
