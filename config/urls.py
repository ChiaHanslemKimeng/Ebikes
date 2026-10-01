"""
VoltRide URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from pages.sitemaps import StaticViewSitemap, ProductSitemap, CategorySitemap, BlogSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('', include('store.urls')),
    path('', include('orders.urls')),
    path('account/', include('accounts.urls')),
    path('reviews/', include('reviews.urls')),
    path('blog/', include('blog.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'pages.views.handler404_view'
handler403 = 'pages.views.handler403_view'
handler500 = 'pages.views.handler500_view'

# Admin site customizations
admin.site.site_header = "Surron Bikes & Parts Administration"
admin.site.site_title = "Surron Admin Portal"
admin.site.index_title = "Store Management & Operations Control Panel"
