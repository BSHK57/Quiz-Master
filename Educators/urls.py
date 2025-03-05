from django.urls import path
from .views import educator_dashboard,create_quiz,edit_quiz,view_results,students_board,my_quizzes
from . import views
urlpatterns = [
    path('educator/dashboard/', educator_dashboard, name='educator_dashboard'),
    path('create-quiz/', create_quiz, name='create_quiz'),
    path('quiz/edit/<int:quiz_id>/', edit_quiz, name='edit_quiz'),
    path('quiz/results/<int:quiz_id>/', view_results, name='view_results'),
    path('educator/Student-board',students_board,name='Students_board'),
    path('educator/dashboard/my_quizzes',my_quizzes,name='edu_quizzes'),
    path('educator/dashboard/Analytics',views.educator_analytics,name='educator_analytics'),
    path('upload-questions/', views.upload_questions, name='upload_questions'),
]
