from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    path('', views.rewards_home, name='home'),
    path('redeem/', views.redeem_airtime, name='redeem'),
    path('watch-ad/', views.watch_ad, name='watch_ad'),
    path('spin/', views.spin_wheel, name='spin'),
    path('daily-challenge/', views.daily_challenge, name='daily_challenge'),
    path('notifications/read/', views.mark_notifications_read, name='notifications_read'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]
