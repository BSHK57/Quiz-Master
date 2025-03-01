from django.urls import path
from .views import register_user, login_user, logout_user, student_dashboard, educator_dashboard, admin_dashboard

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    # Dashboards
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('educator/dashboard/', educator_dashboard, name='educator_dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
]
