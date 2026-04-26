from django.urls import path
from . import views
app_name = 'quizzes'
urlpatterns = [
    path('', views.quiz_list, name='list'),
    path('<uuid:pk>/play/', views.quiz_play, name='play'),
    path('attempt/<uuid:attempt_id>/submit/', views.quiz_submit, name='submit'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]
