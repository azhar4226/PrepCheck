// Service Worker to block external tracking requests
const BLOCKED_DOMAINS = [
    'events.launchdarkly.com',
    'app.launchdarkly.com',
    'client.launchdarkly.com',
    'mobile.launchdarkly.com',
    'stream.launchdarkly.com'
];

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // Block LaunchDarkly and other tracking domains
    if (BLOCKED_DOMAINS.some(domain => url.hostname.includes(domain))) {
        console.log('🚫 Blocked tracking request to:', url.hostname);
        
        // Return a successful empty response to prevent console errors
        event.respondWith(
            new Response('', {
                status: 204,
                statusText: 'Blocked by service worker'
            })
        );
        return;
    }
    
    // Allow all other requests to proceed normally - let the browser handle them
    // Don't intercept other requests to avoid issues with CORS and authentication
});

self.addEventListener('install', (event) => {
    console.log('🔧 Service worker installed - tracking blocker active');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('✅ Service worker activated - tracking protection enabled');
    event.waitUntil(self.clients.claim());
});
