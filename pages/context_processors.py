from django.conf import settings


def site_settings(request):
    marquee_messages = [
        "FREE SHIPPING ON ORDERS OVER $500",
        "NEW 2026 E-BIKE MODELS IN STOCK",
        "GENUINE OEM SPARE PARTS & BATTERIES",
        "2-YEAR COMPREHENSIVE WARRANTY ON ALL E-BIKES",
        "EXPERT TECHNICAL SUPPORT & CONSULTATION",
        "SECURE CHECKOUT GUARANTEED"
    ]
    return {
        'SITE_NAME': 'VoltRide',
        'SITE_TAGLINE': 'Ride Smarter. Go Further.',
        'SUPPORT_EMAIL': getattr(settings, 'SUPPORT_EMAIL', 'support@surronbikesandparts.shop'),
        'SUPPORT_PHONE': getattr(settings, 'SUPPORT_PHONE', '+1 (716) 501-5867'),
        'VAPID_PUBLIC_KEY': getattr(settings, 'VAPID_PUBLIC_KEY', ''),
        'MARQUEE_MESSAGES': marquee_messages,
    }
