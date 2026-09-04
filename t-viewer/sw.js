const CACHE_NAME = 't-viewer-v1.1.1';

function getAppBasePath() {
  const p = self.location.pathname || '/';
  if (p.includes('/t-viewer/')) return '/t-viewer/';
  if (p.includes('/T-Viewer/')) return '/T-Viewer/';
  const swDir = p.replace(/[^/]*$/, '');
  return swDir || '/t-viewer/';
}

const APP_BASE = getAppBasePath();
const OFFLINE_INDEX = APP_BASE + 'index.html';
const ASSETS = [
  APP_BASE,
  OFFLINE_INDEX,
  APP_BASE + 'manifest.json',
  APP_BASE + 'sw.js',
  APP_BASE + 'icon-192.png',
  APP_BASE + 'icon-512.png',
  APP_BASE + 'icon-192-light.png',
  APP_BASE + 'icon-512-light.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => Promise.allSettled(ASSETS.map(url => cache.add(url))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  if (event.request.mode === 'navigate' || (event.request.headers.get('Accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response.ok && url.pathname.startsWith(APP_BASE)) {
            const clone = response.clone();
            event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(new Request(url.origin + url.pathname), clone)));
          }
          return response;
        })
        .catch(() => caches.match(event.request, { ignoreSearch: true })
          .then(cached => cached || caches.match(OFFLINE_INDEX, { ignoreSearch: true })))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request, { ignoreSearch: true })
      .then(cached => cached || fetch(event.request).then(response => {
        if (response.ok && url.pathname.startsWith(APP_BASE)) {
          const clone = response.clone();
          event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(new Request(url.origin + url.pathname), clone)));
        }
        return response;
      }))
  );
});
