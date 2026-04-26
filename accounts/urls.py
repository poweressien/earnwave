from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),

    # Password Reset
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('reset-password/confirm/', views.reset_password_confirm_view, name='reset_password_confirm'),

    # Notifications API
    path('notifications/count/', views.notification_count, name='notification_count'),

    # Change password (when logged in)
    path('change-password/', views.change_password_view, name='change_password'),
]
