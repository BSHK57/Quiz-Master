from django.urls import path
from . import views

urlpatterns = [
    path('quiz_dashboard/', views.quiz_dashboard, name='quiz_dashboard'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('download_report/', views.download_report, name='download_report'),
]
