"""
Django settings for VoltRide project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-voltride-e-commerce-production-ready-default-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # Custom VoltRide Apps
    'store.apps.StoreConfig',
    'orders.apps.OrdersConfig',
    'accounts.apps.AccountsConfig',
    'reviews.apps.ReviewsConfig',
    'blog.apps.BlogConfig',
    'pages.apps.PagesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.store_context',
                'pages.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Default to SQLite for easy development, ready for MySQL/PostgreSQL via env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'pages:home'

# Cart session key
CART_SESSION_ID = 'voltride_cart'
WISHLIST_SESSION_ID = 'voltride_wishlist'

# Messages framework bootstrap classes mapping
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Surron Bikes & Parts Canada <support@surronbikesandparts.shop>')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@surronbikesandparts.shop')
SITE_URL = os.getenv('SITE_URL', 'https://surronbikesandparts.shop')

# Contact Settings
SUPPORT_PHONE = os.getenv('SUPPORT_PHONE', '+1 (716) 501-5867')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@surronbikesandparts.shop')

# Web Push (VAPID) Settings
VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', '')
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', '')
VAPID_ADMIN_EMAIL = os.getenv('VAPID_ADMIN_EMAIL', 'mailto:admin@surronbikesandparts.shop')

# Jazzmin Admin Theme Configuration
JAZZMIN_SETTINGS = {
    "site_title": "Surron Bikes & Parts Admin",
    "site_header": "Surron Admin",
    "site_brand": "Surron Bikes",
    "site_logo": "images/favicon.png",
    "site_logo_classes": "img-circle",
    "site_icon": "images/favicon.png",
    "welcome_sign": "Welcome to Surron Bikes & Parts Administration",
    "copyright": "Surron Bikes & Parts Canada",
    "search_model": ["store.Product", "orders.Order"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Analytics", "url": "admin:orders_analytics", "icon": "fas fa-chart-line"},
        {"name": "Live Store", "url": "/", "new_window": True, "icon": "fas fa-external-link-alt"},
        {"name": "Shop Catalog", "url": "/shop/", "new_window": True, "icon": "fas fa-bicycle"},
    ],
    "usermenu_links": [
        {"name": "View Live Store", "url": "/", "new_window": True, "icon": "fas fa-globe"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "orders",
        "orders.Order",
        "orders.OrderItem",
        "orders.Payment",
        "orders.Coupon",
        "orders.ShippingAddress",
        "orders.PushSubscription",
        "store",
        "store.Product",
        "store.Category",
        "store.Subcategory",
        "store.ProductImage",
        "store.Wishlist",
        "accounts",
        "accounts.UserProfile",
        "accounts.Address",
        "reviews",
        "reviews.ProductReview",
        "blog",
        "blog.BlogPost",
        "blog.BlogCategory",
        "blog.BlogComment",
        "pages",
        "pages.ContactMessage",
        "pages.NewsletterSubscriber",
        "pages.SiteSetting",
        "auth",
        "auth.User",
        "auth.Group",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-shield",
        "auth.Group": "fas fa-users",
        "orders": "fas fa-shopping-cart",
        "orders.Order": "fas fa-receipt",
        "orders.OrderItem": "fas fa-box-open",
        "orders.Payment": "fas fa-credit-card",
        "orders.Coupon": "fas fa-ticket-alt",
        "orders.ShippingAddress": "fas fa-truck",
        "orders.PushSubscription": "fas fa-bell",
        "store": "fas fa-store",
        "store.Product": "fas fa-bicycle",
        "store.Category": "fas fa-tags",
        "store.Subcategory": "fas fa-tag",
        "store.ProductImage": "fas fa-images",
        "store.Wishlist": "fas fa-heart",
        "accounts": "fas fa-user-circle",
        "accounts.UserProfile": "fas fa-id-card",
        "accounts.Address": "fas fa-map-marker-alt",
        "reviews": "fas fa-star",
        "reviews.ProductReview": "fas fa-comment-dots",
        "blog": "fas fa-blog",
        "blog.BlogPost": "fas fa-newspaper",
        "blog.BlogCategory": "fas fa-folder-open",
        "blog.BlogComment": "fas fa-comments",
        "pages": "fas fa-file-alt",
        "pages.ContactMessage": "fas fa-envelope-open-text",
        "pages.NewsletterSubscriber": "fas fa-paper-plane",
        "pages.SiteSetting": "fas fa-sliders-h",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle-notch",
    "related_modal_active": False,
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_push.js",
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark navbar-primary",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "default_theme_mode": "dark",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
