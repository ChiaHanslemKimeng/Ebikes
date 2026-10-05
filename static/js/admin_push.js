/**
 * Surron Bikes & Parts - High-Priority Web Push Notification Handler
 * Specialized for iOS Safari (PWA Standalone), Android Chrome, and Desktop Browsers.
 */

(function () {
    'use strict';

    // Helper: Convert URL-safe base64 string to Uint8Array for PushManager
    function urlB64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    // Detection helpers
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
        (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    const isStandalone = window.navigator.standalone === true ||
        window.matchMedia('(display-mode: standalone)').matches;

    // Show step-by-step modal guide for iOS Safari users
    function showIOSInstallModal() {
        let modal = document.getElementById('ios-pwa-guide-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'ios-pwa-guide-modal';
            modal.innerHTML = `
                <div style="position:fixed; inset:0; background:rgba(0,0,0,0.75); z-index:99999; display:flex; align-items:center; justify-content:center; padding:16px; backdrop-filter:blur(4px);">
                    <div style="background:#0f172a; color:#f8fafc; border:1px solid #334155; border-radius:18px; max-width:440px; width:100%; padding:24px; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5); font-family:system-ui, -apple-system, sans-serif;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px;">
                            <div>
                                <h3 style="margin:0 0 4px 0; font-size:1.25rem; font-weight:700; color:#38bdf8;">⚠️ Setup iOS Push Alerts</h3>
                                <p style="margin:0; font-size:0.85rem; color:#94a3b8;">Required for Apple background notifications</p>
                            </div>
                            <button id="close-ios-modal-btn" style="background:#1e293b; border:none; color:#cbd5e1; width:32px; height:32px; border-radius:50%; cursor:pointer; font-size:16px;">✕</button>
                        </div>
                        <div style="font-size:0.92rem; line-height:1.55; color:#cbd5e1;">
                            <p style="margin:0 0 12px 0;">Apple requires web apps to be installed to your iPhone/iPad Home Screen before push alerts with sound and vibration can function in the background:</p>
                            <ol style="margin:0 0 18px 0; padding-left:22px; display:flex; flex-direction:column; gap:8px;">
                                <li>Tap the <strong style="color:#38bdf8;">Share button</strong> (<span style="font-size:1.1rem;">⎋</span> or square with arrow up) at the bottom of Safari.</li>
                                <li>Scroll down the menu and tap <strong style="color:#00e599;">Add to Home Screen</strong> (<span style="font-size:1.1rem;">➕</span>).</li>
                                <li>Tap <strong style="color:#38bdf8;">Add</strong> in the top-right corner.</li>
                                <li>Open the new <strong style="color:#00e599;">Surron Admin</strong> app from your Home Screen.</li>
                                <li>Tap <strong style="color:#00e599;">Turn on Push Alerts</strong> inside the app.</li>
                            </ol>
                            <div style="background:#1e293b; padding:12px; border-radius:10px; font-size:0.82rem; color:#94a3b8; border-left:4px solid #38bdf8;">
                                💡 Once installed, alerts will arrive natively with sound and vibration even when the app is completely closed, exactly like WhatsApp!
                            </div>
                        </div>
                        <div style="margin-top:20px; text-align:right;">
                            <button id="ok-ios-modal-btn" style="background:#0284c7; color:#fff; border:none; padding:10px 20px; border-radius:10px; font-weight:600; cursor:pointer; font-size:0.9rem;">Got It</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            document.getElementById('close-ios-modal-btn').onclick = function () {
                modal.remove();
            };
            document.getElementById('ok-ios-modal-btn').onclick = function () {
                modal.remove();
            };
        }
    }

    // Retrieve VAPID Public Key
    async function getVapidPublicKey() {
        if (window.VAPID_PUBLIC_KEY && window.VAPID_PUBLIC_KEY.length > 20) {
            return window.VAPID_PUBLIC_KEY;
        }
        try {
            const resp = await fetch('/vapid-public-key/');
            const data = await resp.json();
            if (data.publicKey) {
                window.VAPID_PUBLIC_KEY = data.publicKey;
                return data.publicKey;
            }
        } catch (e) {
            console.error('Failed to fetch VAPID key:', e);
        }
        return '';
    }

    // Save push subscription to Django backend
    async function sendSubscriptionToBackend(subscription) {
        const subData = subscription.toJSON();
        const response = await fetch('/save-push-subscription/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(subData)
        });

        if (!response.ok) {
            throw new Error(`Failed to save subscription (HTTP ${response.status})`);
        }
        return await response.json();
    }

    // Main subscription routine
    async function subscribeToPushManager(btn, testBtn) {
        try {
            btn.disabled = true;
            btn.innerHTML = '⏳ Requesting Permission...';

            // 1. Request user permission
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                btn.disabled = false;
                if (permission === 'denied') {
                    btn.className = 'push-action-btn push-btn-denied';
                    btn.innerHTML = '🚫 Alerts Blocked in Settings';
                    alert('Push notifications are blocked in your browser settings. Please allow notifications for this site to receive background alerts.');
                } else {
                    btn.className = 'push-action-btn push-btn-default';
                    btn.innerHTML = '🔔 Turn on Push Alerts';
                }
                return;
            }

            btn.innerHTML = '⏳ Registering Worker...';

            // 2. Register Service Worker with root scope
            const registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
            await navigator.serviceWorker.ready;

            // 3. Get VAPID public key
            const vapidKey = await getVapidPublicKey();
            if (!vapidKey) {
                throw new Error('VAPID public key not found. Check settings.py and .env.');
            }

            const applicationServerKey = urlB64ToUint8Array(vapidKey);

            // 4. Subscribe with PushManager
            btn.innerHTML = '⏳ Activating Push...';
            let subscription = await registration.pushManager.getSubscription();
            if (!subscription) {
                subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: applicationServerKey
                });
            }

            // 5. Save to backend database
            await sendSubscriptionToBackend(subscription);

            // 6. Update UI
            btn.disabled = false;
            btn.className = 'push-action-btn push-btn-active';
            btn.innerHTML = '✅ Push Alerts Active';
            btn.title = 'Active on this device! Click to re-verify';

            if (testBtn) {
                testBtn.style.display = 'inline-flex';
            }

            console.log('Push notification subscription complete!');
        } catch (error) {
            console.error('Subscription error:', error);
            btn.disabled = false;
            btn.className = 'push-action-btn push-btn-default';
            btn.innerHTML = '🔔 Retry Push Setup';
            alert('Could not enable push alerts: ' + error.message);
        }
    }

    // Send instant test push alert
    async function triggerTestPush(testBtn) {
        if (!testBtn) return;
        const originalText = testBtn.innerHTML;
        try {
            testBtn.disabled = true;
            testBtn.innerHTML = '⏳ Sending...';

            const resp = await fetch('/test-push/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    title: '⚡ Surron Admin: Test Alert',
                    body: 'High-priority alert received with sound & vibration! Ready for live orders.',
                    url: '/admin/'
                })
            });

            const result = await resp.json();
            testBtn.innerHTML = '🚀 Dispatched!';
            setTimeout(() => {
                testBtn.disabled = false;
                testBtn.innerHTML = originalText;
            }, 3000);
        } catch (e) {
            console.error('Test push failed:', e);
            testBtn.disabled = false;
            testBtn.innerHTML = '❌ Failed';
            setTimeout(() => { testBtn.innerHTML = originalText; }, 3000);
        }
    }

    function ensurePushWidgetInNav() {
        if (document.getElementById('push-sub-btn')) return;
        const nav = document.querySelector('#jazzy-navbar .navbar-nav.ms-auto') || 
                    document.querySelector('.navbar-nav.ms-auto') || 
                    document.querySelector('#user-tools');
        if (!nav) return;
        const li = document.createElement('li');
        li.className = 'nav-item d-flex align-items-center me-2';
        li.innerHTML = `
            <span class="push-widget-container">
                <button id="push-sub-btn" type="button" class="push-action-btn push-btn-default" title="Activate instant background sound & vibration alerts">
                    🔔 Turn on Push Alerts
                </button>
                <button id="push-test-btn" type="button" class="push-test-btn" style="display:none;" title="Send a live test sound & vibration push alert">
                    ⚡ Test Alert
                </button>
            </span>
        `;
        nav.insertBefore(li, nav.firstChild);
    }

    // Initialize UI and Service Worker check on page load
    async function initPushNotificationUI() {
        ensurePushWidgetInNav();
        const btn = document.getElementById('push-sub-btn');
        const testBtn = document.getElementById('push-test-btn');
        if (!btn) return;

        // Register Service Worker in background if supported
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch((e) => {
                console.warn('ServiceWorker registration error:', e);
            });
        }

        // CRUCIAL iOS Safari Logic:
        // Do NOT hide the button if !('Notification' in window).
        // On iOS Safari browser tab, Notification is undefined until installed as PWA to Home Screen.
        if (!('Notification' in window)) {
            btn.style.display = 'inline-flex';
            btn.className = 'push-action-btn push-btn-ios-warning';
            btn.innerHTML = '⚠️ Setup iOS Push Alerts';
            btn.title = 'Tap to view instructions for iOS push alerts';
            btn.onclick = function (e) {
                e.preventDefault();
                showIOSInstallModal();
            };
            return;
        }

        // Standard PushManager support in browser or standalone PWA
        btn.style.display = 'inline-flex';

        // Check current permission
        if (Notification.permission === 'denied') {
            btn.className = 'push-action-btn push-btn-denied';
            btn.innerHTML = '🚫 Alerts Blocked';
            btn.title = 'Notifications are blocked in your browser settings';
            btn.onclick = function (e) {
                e.preventDefault();
                alert('Notifications are blocked. Please enable permissions for this site in your browser settings.');
            };
            return;
        }

        if (Notification.permission === 'granted') {
            try {
                const reg = await navigator.serviceWorker.ready;
                const existingSub = await reg.pushManager.getSubscription();
                if (existingSub) {
                    btn.className = 'push-action-btn push-btn-active';
                    btn.innerHTML = '✅ Push Alerts Active';
                    btn.title = 'Active on this device! Tap to refresh';
                    if (testBtn) testBtn.style.display = 'inline-flex';

                    // Resend to backend in background to guarantee current session link
                    sendSubscriptionToBackend(existingSub).catch(() => {});
                } else {
                    btn.className = 'push-action-btn push-btn-default';
                    btn.innerHTML = '🔔 Enable Push Alerts';
                }
            } catch (err) {
                btn.className = 'push-action-btn push-btn-default';
                btn.innerHTML = '🔔 Turn on Push Alerts';
            }
        } else {
            btn.className = 'push-action-btn push-btn-default';
            btn.innerHTML = '🔔 Turn on Push Alerts';
        }

        // Attach click listeners
        btn.onclick = function (e) {
            e.preventDefault();
            subscribeToPushManager(btn, testBtn);
        };

        if (testBtn) {
            testBtn.onclick = function (e) {
                e.preventDefault();
                triggerTestPush(testBtn);
            };
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPushNotificationUI);
    } else {
        initPushNotificationUI();
    }
})();
