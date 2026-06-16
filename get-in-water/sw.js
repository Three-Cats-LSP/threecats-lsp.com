const CACHE_NAME = 'giw-v1.3.1';
const ASSETS = [
  '/get-in-water/',
  '/get-in-water/index.html',
  '/get-in-water/manifest.json',
  '/get-in-water/sw.js',
  '/get-in-water/icon-192.png',
  '/get-in-water/icon-512.png',
  '/get-in-water/icon-192-light.png',
  '/get-in-water/icon-512-light.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
