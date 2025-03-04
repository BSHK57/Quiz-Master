from django.urls import path
from .views import student_dashboard
from Quizzes.views import quiz_dashboard
from . import views

urlpatterns = [
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/quiz_setup/', views.quiz_setup, name='quiz_setup'),
    path('student/quiz_questions/', views.quiz_questions, name='quiz_questions'),
    path('student/quiz_result/<int:correct>/<int:wrong>/<str:score>/', views.quiz_result, name='quiz_result'),
    path('quiz_dashboard/', quiz_dashboard, name='quiz_dashboard')

]
