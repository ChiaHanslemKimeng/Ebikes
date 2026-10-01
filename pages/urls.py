from django.urls import path
from pages import views

app_name = 'pages'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('shipping-policy/', views.shipping_policy_view, name='shipping_policy'),
    path('returns-policy/', views.returns_policy_view, name='returns_policy'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    path('search/', views.search_view, name='search'),
    path('search/autocomplete/', views.search_autocomplete_view, name='search_autocomplete'),
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
