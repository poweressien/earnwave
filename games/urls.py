from django.urls import path
from . import views
app_name = 'games'
urlpatterns = [
    path('', views.games_list, name='list'),
    path('<uuid:pk>/play/', views.game_play, name='play'),
    path('session/<uuid:session_id>/complete/', views.game_complete, name='complete'),
]
