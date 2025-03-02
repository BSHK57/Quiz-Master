from django.urls import path
from .views import educator_dashboard

urlpatterns = [
    path('educator/dashboard/', educator_dashboard, name='educator_dashboard'),
]
