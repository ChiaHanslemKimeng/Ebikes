from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views

app_name = 'accounts'

from accounts.forms import StrictPasswordResetForm, StyledSetPasswordForm

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_edit_view, name='profile_edit'),
    path('password-change/', views.password_change_view, name='password_change'),

    # Password Reset flow using customized templates & strict email validation
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             form_class=StrictPasswordResetForm,
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             html_email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/account/password-reset/done/'
         ),
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             form_class=StyledSetPasswordForm,
             template_name='accounts/password_reset_confirm.html',
             success_url='/account/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Web Push Notification Endpoints
    path('save-push-subscription/', views.save_push_subscription, name='save_push_subscription'),
    path('vapid-public-key/', views.get_vapid_public_key, name='vapid_public_key'),
    path('test-push/', views.send_test_push, name='test_push'),
]
