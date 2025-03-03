# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .models import Educator
# from Students.models import Subject

# @login_required
# def educator_dashboard(request):
#     if request.user.role != 'educator':
#         return redirect('login')  # Ensure only educators access this

#     subjects = Subject.objects.all()

#     if request.method == 'POST':
#         selected_subject_names = request.POST.getlist('subjects')

#         # Create any missing subjects in the Subject table
#         for name in selected_subject_names:
#             Subject.objects.get_or_create(name=name)

#         # Save selected subjects to Educator model as a comma-separated string
#         educator, created = Educator.objects.get_or_create(user=request.user)
#         educator.set_subject_list(selected_subject_names)
#         educator.save()

#         messages.success(request, "Subjects have been updated successfully.")
#     else:
#         # Preload previously selected subjects (split stored string into list)
#         try:
#             educator = Educator.objects.get(user=request.user)
#             selected_subject_names = educator.get_subject_list()
#         except Educator.DoesNotExist:
#             selected_subject_names = []

#     return render(request, 'educators/dashboard.html', {
#         'subjects': subjects,
#         'selected_subject_names': selected_subject_names
#     })
#     # return render(request, 'educators/dashboard.html')
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Educator
from django.forms import modelformset_factory
from django.db.models import Count, Avg
from django.db import models
from .forms import FullQuizForm,QuizForm, QuestionForm, OptionForm
from Quizzes.models import Quiz, Question, Option,StudentQuizAttempt

def educator_dashboard(request):
    educator = Educator.objects.get(user=request.user)
    
    # Fetch all quizzes created by the educator
    quizzes = Quiz.objects.filter(educator=educator).annotate(
        students_count=Count('studentquizattempt', distinct=True),
        num_questions=Count('question'),
        
        avg_score=Avg('studentquizattempt__score')
    )
    
    # Calculate completion rate for each quiz
    for quiz in quizzes:
        print(quiz)
        total_attempts = StudentQuizAttempt.objects.filter(quiz=quiz).count()
        total_students = quiz.students_count or 1  # Avoid division by zero
        quiz.completion_rate = round((total_attempts / total_students) * 100, 2) if total_attempts else 0
        quiz.avg_score = round(quiz.avg_score or 0, 2)
        print(quiz.num_questions)
    for quiz in quizzes:
        quiz.avg_questions_per_student = (
        quiz.num_questions // quiz.students_count
        if quiz.students_count else 0
    )
    # Overall statistics
    students_attempts = StudentQuizAttempt.objects.filter(quiz__educator=educator)
    total_students = students_attempts.values('student').distinct().count()
    total_quizzes = quizzes.count()
    avg_completion_rate = students_attempts.exclude(score__isnull=True).count() / max(total_students * total_quizzes, 1) * 100
    avg_score = students_attempts.exclude(score__isnull=True).aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    stats = {
        'total_students': total_students,
        'total_quizzes': total_quizzes,
        'avg_completion_rate': round(avg_completion_rate, 2),
        'avg_score': round(avg_score, 2),
    }
    print(quizzes)
    return render(request, 'educators/dashboard.html', {
        'quizzes': quizzes,
        'stats': stats,
        'educator': educator
    })

@login_required

def create_quiz(request):
    if request.method == "POST":
        form = FullQuizForm(request.POST)
        print("pp")
        if form.is_valid():
            # Save the Quiz
            quiz = Quiz.objects.create(title=form.cleaned_data['quiz_title'], educator=request.user.educator)

            num_questions = int(request.POST.get('num_questions', 0))

            for i in range(1, num_questions + 1):
                # Save Question
                question_text = request.POST.get(f'question_{i}')
                question = Question.objects.create(quiz=quiz, text=question_text)
                # Save Options
                for j in range(1, 5):  # Assuming 4 options per question
                    option_text = request.POST.get(f'question_{i}_option_{j}')
                    correct_answer = request.POST.get(f'question_{i}_correct')
                    is_correct = (correct_answer == str(j))  # Compare selected option

                    Option.objects.create(question=question, text=option_text, is_correct=is_correct)

            return redirect('educator_dashboard')

    else:
        form = FullQuizForm()
    return render(request, 'educators/create_quiz.html', {'form': form})
    # return render(request, 'educators/create_quiz.html', {'form': form})
@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, educator=request.user.educator)
    questions = Question.objects.filter(quiz=quiz).prefetch_related('options')

    if request.method == "POST":
        # Update quiz title
        quiz.title = request.POST.get('quiz_title')
        quiz.save()

        # Update questions and options
        for i in range(1, len(questions) + 1):
            question_text = request.POST.get(f'question_{i}')
            question, created = Question.objects.update_or_create(
                quiz=quiz, id=request.POST.get(f'question_{i}_id'),
                defaults={'text': question_text}
            )

            for j in range(1, 5):
                option_text = request.POST.get(f'question_{i}_option_{j}')
                is_correct = request.POST.get(f'question_{i}_correct') == str(j)

                Option.objects.update_or_create(
                    question=question, id=request.POST.get(f'question_{i}_option_{j}_id'),
                    defaults={'text': option_text, 'is_correct': is_correct}
                )

        return redirect('educator_dashboard')

    return render(request, 'educators/edit_quiz.html', {'quiz': quiz, 'questions': questions})

@login_required
def view_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, educator=request.user.educator)
    
    student_attempts = StudentQuizAttempt.objects.filter(quiz=quiz).select_related('student')
    total_attempts = student_attempts.count()
    avg_score = student_attempts.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    completion_rate = round((total_attempts / max(len(student_attempts) or 1, 1)) * 100, 2) if total_attempts else 0

    return render(request, 'educators/view_results.html', {
        'quiz': quiz,
        'student_attempts': student_attempts,
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 2),
        'completion_rate': completion_rate,
    })
