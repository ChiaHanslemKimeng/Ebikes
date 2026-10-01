from django.urls import path
from reviews import views

app_name = 'reviews'

urlpatterns = [
    path('', views.review_list_view, name='review_list'),
    path('add/<int:product_id>/', views.add_review_view, name='add_review'),
]
