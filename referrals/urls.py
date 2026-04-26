from django.urls import path
from . import views
app_name = 'referrals'
urlpatterns = [
    path('', views.referral_home, name='home'),
]
