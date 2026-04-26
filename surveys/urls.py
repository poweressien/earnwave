from django.urls import path
from . import views
app_name = 'surveys'
urlpatterns = [
    path('', views.survey_list, name='list'),
    path('<uuid:pk>/', views.survey_detail, name='detail'),
]
