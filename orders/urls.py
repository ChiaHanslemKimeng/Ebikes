from django.urls import path
from orders import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('coupon/apply/', views.apply_coupon_view, name='apply_coupon'),
    path('coupon/remove/', views.remove_coupon_view, name='remove_coupon'),
    path('account/orders/', views.order_list_view, name='order_list'),
    path('account/orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
]
