from django.urls import path
from .views import register_user, login_user, logout_user, admin_dashboard
from . import views
urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('forgot-password/', views.forgot_password_step1, name='forgot_password_step1'),
    path('reset-password/<str:email>/', views.forgot_password_step2, name='forgot_password_step2'),
    # Dashboards
    # path('student/dashboard/', student_dashboard, name='student_dashboard'),
    # path('educator/dashboard/', educator_dashboard, name='educator_dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
]
