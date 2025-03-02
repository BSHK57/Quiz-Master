from django.urls import path
from .views import student_dashboard

urlpatterns = [
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
]
