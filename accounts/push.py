"""
Web Push Notification Service using pywebpush and VAPID.
Handles delivering native web push notifications to subscribed devices,
including iOS Safari (PWA) and PC/Mobile browsers.
"""
import json
import logging
import threading
import time
from django.conf import settings
from pywebpush import webpush, WebPushException
from accounts.models import PushSubscription

logger = logging.getLogger(__name__)


def _deliver_web_push_to_subscription(sub, payload_json, vapid_private_key, vapid_claims):
    """
    Delivers a web push payload to a single subscription.
    Deletes the subscription if it has expired (HTTP 404 or 410).
    """
    subscription_info = {
        "endpoint": sub.endpoint,
        "keys": {
            "p256dh": sub.p256dh,
            "auth": sub.auth,
        }
    }

    try:
        response = webpush(
            subscription_info=subscription_info,
            data=payload_json,
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims,
            ttl=86400  # 24 hours TTL so sleeping devices receive push when awakened
        )
        logger.info(f"Web push successfully sent to subscription {sub.id} (user: {sub.user})")
        return True
    except WebPushException as ex:
        status_code = getattr(ex.response, 'status_code', None) if ex.response is not None else None
        # Handle expired subscriptions (HTTP 404 or 410)
        if status_code in (404, 410):
            logger.warning(f"Subscription {sub.id} expired or unregistered (HTTP {status_code}). Removing from database.")
            sub.delete()
        else:
            logger.error(f"WebPushException for subscription {sub.id}: {ex} (Status: {status_code})")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending web push to subscription {sub.id}: {e}", exc_info=True)
        return False


def _send_web_push_thread(title, body, url, badge=None, icon=None):
    """Worker function executed in background thread."""
    vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
    vapid_admin_email = getattr(settings, 'VAPID_ADMIN_EMAIL', 'mailto:admin@surronbikesandparts.shop')

    if not vapid_private_key:
        logger.warning("VAPID_PRIVATE_KEY is not set in settings/environment. Web push aborted.")
        return

    # Ensure admin email starts with mailto: or https: as required by RFC 8292
    if not vapid_admin_email.startswith('mailto:') and not vapid_admin_email.startswith('https:'):
        vapid_admin_email = f"mailto:{vapid_admin_email}"

    vapid_claims = {"sub": vapid_admin_email}

    # Fetch all registered admin/device push subscriptions
    subscriptions = list(PushSubscription.objects.all())
    if not subscriptions:
        logger.info("No active push subscriptions found. Push skipped.")
        return

    # Construct rich payload tailored for WhatsApp-like high-priority alert
    full_url = url or '/admin/'
    if not full_url.startswith('http://') and not full_url.startswith('https://'):
        site_url = getattr(settings, 'SITE_URL', 'https://surronbikesandparts.shop').rstrip('/')
        full_url = f"{site_url}{full_url}" if full_url.startswith('/') else f"{site_url}/{full_url}"

    payload = {
        "title": title,
        "body": body,
        "icon": icon or "/static/images/icon-192x192.png",
        "badge": badge or "/static/images/badge-72x72.png",
        "vibrate": [200, 100, 200, 100, 200, 100, 200],
        "requireInteraction": True,
        "tag": f"admin-alert-{int(time.time())}",
        "renotify": True,
        "timestamp": int(time.time() * 1000),
        "data": {
            "url": full_url,
            "dateOfArrival": int(time.time() * 1000)
        }
    }
    payload_json = json.dumps(payload)

    logger.info(f"Broadcasting web push to {len(subscriptions)} subscription(s): '{title}'")
    for sub in subscriptions:
        _deliver_web_push_to_subscription(sub, payload_json, vapid_private_key, vapid_claims)


def send_web_push(title, body, url=None, sync=False):
    """
    Broadcasts a native Web Push Notification to all subscribed admin devices.
    Executes in a background thread by default so it does not block HTTP requests.
    """
    if sync:
        _send_web_push_thread(title, body, url)
    else:
        thread = threading.Thread(
            target=_send_web_push_thread,
            args=(title, body, url),
            daemon=True
        )
        thread.start()
