/* EarnWave Service Worker — PWA Support */
const CACHE_NAME = 'earnwave-v1';
const OFFLINE_URL = '/offline/';

const PRECACHE_URLS = [
  '/',
  '/static/css/earnwave.css',
  '/static/js/earnwave.js',
  'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  // Network-first for API calls
  if (event.request.url.includes('/api/') || event.request.url.includes('/rewards/')) {
    event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
    return;
  }

  // Cache-first for static assets
  if (event.request.url.includes('/static/')) {
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      }))
    );
    return;
  }

  // Network-first for pages
  event.respondWith(
    fetch(event.request)
      .then(response => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  if (event.tag === 'sync-points') {
    event.waitUntil(syncPoints());
  }
});

async function syncPoints() {
  // Sync any offline-queued point transactions
  const cache = await caches.open('earnwave-offline-queue');
  const requests = await cache.keys();
  return Promise.all(requests.map(async req => {
    try {
      await fetch(req);
      await cache.delete(req);
    } catch (e) {
      console.log('Sync failed, will retry:', e);
    }
  }));
}
