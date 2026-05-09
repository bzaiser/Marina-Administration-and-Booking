const CACHE_NAME = 'marina-pwa-v1';
const ASSETS_TO_CACHE = [
    '/offline/',
    '/static/vendor/bootstrap/bootstrap.min.css',
    '/static/vendor/bootstrap-icons/bootstrap-icons.css',
    '/static/css/base.css',
    '/static/logo-192.png',
    '/static/logo-512.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

self.addEventListener('fetch', (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request).then((response) => {
                if (response) {
                    return response;
                }
                // If it's a navigation request (HTML), return offline page
                if (event.request.mode === 'navigate') {
                    return caches.match('/offline/');
                }
            });
        })
    );
});
