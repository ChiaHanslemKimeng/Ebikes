// Surron Bikes & Parts - High Priority Native Web Push Service Worker
// Designed for iOS Safari (PWA) and Desktop/Mobile Web Push alerts

self.addEventListener('install', (event) => {
    // Force immediate activation without waiting for existing clients to close
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    // Take immediate control of all open pages/clients
    event.waitUntil(self.clients.claim());
});

// Push Event: triggers system alert even when browser/app is closed or in background
self.addEventListener('push', (event) => {
    let payload = {
        title: '⚡ Surron Admin Alert',
        body: 'New urgent store notification received.',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        url: '/admin/',
        vibrate: [200, 100, 200, 100, 200, 100, 200],
        requireInteraction: true,
        tag: 'surron-admin-alert'
    };

    if (event.data) {
        try {
            const data = event.data.json();
            payload = {
                title: data.title || payload.title,
                body: data.body || payload.body,
                icon: data.icon || payload.icon,
                badge: data.badge || payload.badge,
                url: (data.data && data.data.url) || data.url || payload.url,
                vibrate: data.vibrate || payload.vibrate,
                requireInteraction: data.requireInteraction !== undefined ? data.requireInteraction : true,
                tag: data.tag || 'surron-admin-alert-' + Date.now(),
                data: data.data || { url: data.url || payload.url }
            };
        } catch (e) {
            // Fallback for plain text push messages
            payload.body = event.data.text();
        }
    }

    const notificationOptions = {
        body: payload.body,
        icon: payload.icon,
        badge: payload.badge,
        // High-priority WhatsApp-like vibration pattern: buzz-pause-buzz-pause-longbuzz
        vibrate: payload.vibrate,
        // Keeps the notification visible on screen until user dismisses or clicks it
        requireInteraction: payload.requireInteraction,
        tag: payload.tag,
        renotify: true,
        data: {
            url: payload.url,
            dateOfArrival: Date.now()
        },
        actions: [
            { action: 'open', title: '👁️ Open View' },
            { action: 'dismiss', title: '✖ Dismiss' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(payload.title, notificationOptions)
    );
});

// Notification Click Event: Focus or Open Window to the target URL
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    const targetUrl = (event.notification.data && event.notification.data.url)
        ? event.notification.data.url
        : '/admin/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
            // If an admin window is already open, focus it and navigate
            for (let i = 0; i < windowClients.length; i++) {
                const client = windowClients[i];
                if (client.url.includes('/admin') && 'focus' in client) {
                    if ('navigate' in client && targetUrl) {
                        client.navigate(targetUrl);
                    }
                    return client.focus();
                }
            }
            // Otherwise open a new window/app view
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
