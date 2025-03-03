from django.urls import path
from .views import educator_dashboard,create_quiz,edit_quiz,view_results

urlpatterns = [
    path('educator/dashboard/', educator_dashboard, name='educator_dashboard'),
    path('create-quiz/', create_quiz, name='create_quiz'),
    path('quiz/edit/<int:quiz_id>/', edit_quiz, name='edit_quiz'),
    path('quiz/results/<int:quiz_id>/', view_results, name='view_results'),
]
