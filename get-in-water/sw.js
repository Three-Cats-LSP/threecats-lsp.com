const CACHE_NAME = 'giw-v1.4.3';
const ASSETS = [
  '/get-in-water/',
  '/get-in-water/index.html',
  '/get-in-water/manifest.json',
  '/get-in-water/sw.js',
  '/get-in-water/capacitor-bridge.js',
  '/get-in-water/backup-sanitize.js',
  '/get-in-water/firebase-config.js',
  '/get-in-water/sync.js',
  '/get-in-water/vendor/firebase/firebase-app-compat.js',
  '/get-in-water/vendor/firebase/firebase-auth-compat.js',
  '/get-in-water/vendor/firebase/firebase-firestore-compat.js',
  '/get-in-water/vendor/jspdf.umd.min.js',
  '/get-in-water/vendor/fonts/DejaVuSans.ttf',
  '/get-in-water/vendor/fonts/DejaVuSans-Bold.ttf',
  '/get-in-water/icon-192.png',
  '/get-in-water/icon-512.png',
  '/get-in-water/icon-192-light.png',
  '/get-in-water/icon-512-light.png'
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
  return /\/get-in-water\/icon-\d+/.test(url.pathname);
}

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (isFirebaseRequest(url)) {
    e.respondWith(fetch(e.request));
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
