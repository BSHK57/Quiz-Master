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
from django.db.models import Count, Avg,F, Q
from django.db import models
from .forms import FullQuizForm,QuizForm, QuestionForm, OptionForm
from Quizzes.models import Quiz, Question, Option,StudentQuizAttempt
from django.db.models import Q
from datetime import timedelta
from django.utils.timezone import now
from django.contrib import messages
import pandas as pd
def educator_dashboard(request):
    educator = Educator.objects.get(user=request.user)
    
    # Fetch all quizzes created by the educator
    quizzes = Quiz.objects.filter(educator=educator).annotate(
        students_count1=Count('studentquizattempt__student', distinct=True),
        students_count=Count('studentquizattempt', distinct=True),
        num_questions=Count('question',distinct=True),
        
        avg_score=Avg('studentquizattempt__score')
    )
    
    # Calculate completion rate for each quiz
    for quiz in quizzes:
        print(quiz)
        total_attempts = StudentQuizAttempt.objects.filter(quiz=quiz).count()
        total_students = quiz.students_count or 1  # Avoid division by zero
        quiz.completion_rate = round((total_attempts / total_students) * 100, 2) if total_attempts else 0
        quiz.avg_score = round(quiz.avg_score or 0, 2)

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
def students_board(request):
    educator = get_object_or_404(Educator, user=request.user)
    query = request.GET.get('q', '')
    # Fetch all quiz attempts for quizzes created by this educator
    student_attempts = StudentQuizAttempt.objects.filter(quiz__educator=educator).select_related('student', 'quiz')
    if query:
        student_attempts = student_attempts.filter(
            Q(student__user__name__icontains=query) | Q(quiz__title__icontains=query)
        )
    # Organize student attempts data
    student_data = {}
    for attempt in student_attempts:
        student_name = attempt.student.user.name
        if student_name not in student_data:
            student_data[student_name] = []
        student_data[student_name].append({
            'quiz_title': attempt.quiz.title,
            'score': round(attempt.score,0),
            'completed_at': attempt.completed_at
        })

    return render(request, 'educators/students_board.html', {'student_data': student_data,'query': query,'educator':educator})


@login_required
def my_quizzes(request):
    educator = get_object_or_404(Educator, user=request.user)

    # Fetch all quizzes created by the educator
    quizzes = Quiz.objects.filter(educator=educator).annotate(
        students_count1=Count('studentquizattempt__student', distinct=True),
        students_count=Count('studentquizattempt', distinct=True),
        num_questions=Count('question',distinct=True),
        avg_score=Avg('studentquizattempt__score')
    )
    # Fetch student attempts related to the educator's quizzes
    student_attempts = StudentQuizAttempt.objects.filter(quiz__educator=educator).select_related('student__user')

    # Prepare quiz statistics
    quiz_data = []
    for quiz in quizzes:
        print(quiz.num_questions)
        attempts = student_attempts.filter(quiz=quiz)
        total_attempts = attempts.count()
        unique_students = quiz.students_count or 1  # Avoid division by zero

        quiz_data.append({
            'quiz': quiz,
            'num_questions': quiz.num_questions,
            'students_count': quiz.students_count1,
            'total_attempts': total_attempts,
            'avg_score': round(quiz.avg_score or 0, 2),
            'completion_rate': round((total_attempts / unique_students) * 100, 2) if total_attempts else 0,
            'student_attempts': [
                {
                    'student': attempt.student.user.name,
                    'attempts': student_attempts.filter(student=attempt.student, quiz=quiz).count(),
                    'success_rate': round(attempt.score, 2)
                }
                for attempt in student_attempts.filter(quiz=quiz)
            ]
        })
    print(quiz_data)
    return render(request, 'educators/my_quizzes.html', {'quiz_data': quiz_data,'educator':educator})


@login_required

def create_quiz(request):
    if request.method == "POST":
        form = FullQuizForm(request.POST)
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
from django.core.serializers.json import DjangoJSONEncoder
import json

@login_required
def educator_analytics(request):
    educator = get_object_or_404(Educator, user=request.user)

    # 1. Student Performance Overview (Bar Chart)
    student_scores = list(
        StudentQuizAttempt.objects.filter(quiz__educator=educator)
        .values(student_name=F('student__user__name'))
        .annotate(avg_score=Avg('score'))
        .order_by('-avg_score')
    )

    # 2. Quiz Performance Over Time (Line Chart)
    quiz_performance = list(
        Quiz.objects.filter(educator=educator)
        .values('created_at')
        .annotate(avg_score=Avg('studentquizattempt__score'))
        .order_by('created_at')
    )
    print(quiz_performance)
    # Convert datetime to string for JSON serialization
    for item in quiz_performance:
        item['created_at'] = item['created_at'].strftime('%Y-%m-%d')

    # 3. Subject-wise Quiz Performance (Pie Chart)
    subject_quiz_count = list(
        Quiz.objects.filter(educator=educator)
        .values('subject')
        .annotate(total=Count('id'))
    )

    # 4. Question Difficulty Analysis (Horizontal Bar Chart)
    question_difficulty = list(
        Question.objects.filter(quiz__educator=educator) \
            .annotate(correct_answers=Count('quiz__studentquizattempt', filter=Q(quiz__studentquizattempt__score__gt=0))) \
            .values('text', 'correct_answers')
    )

    # 5. Quiz Attempt Frequency (Line Chart)
    time_range = now() - timedelta(days=30)  # Last 30 days
    quiz_attempts_over_time = list(
        StudentQuizAttempt.objects.filter(quiz__educator=educator, completed_at__gte=time_range)
        .values('completed_at__date')
        .annotate(attempt_count=Count('id'))
        .order_by('completed_at__date')
    )

    # Convert datetime to string
    for item in quiz_attempts_over_time:
        item['completed_at__date'] = item['completed_at__date'].strftime('%Y-%m-%d')

    # 6. Top Performers in a Quiz (Bar Chart)
    top_performers = list(
        StudentQuizAttempt.objects.filter(quiz__educator=educator)
        .values(student_name=F('student__user__name'), quiz_title=F('quiz__title'))
        .annotate(score=Avg('score'))
        .order_by('-score')[:5]
    )

    # 7. Pass/Fail Ratio per Quiz (Doughnut Chart)
    pass_fail_ratio = list(
        StudentQuizAttempt.objects.filter(quiz__educator=educator)
        .annotate(passed=Count('id', filter=Q(score__gte=50)), failed=Count('id', filter=Q(score__lt=50)))
        .values('quiz__title', 'passed', 'failed')
    )

    # 8. Educator's Quiz Distribution (Pie Chart)
    quiz_distribution = list(
        Quiz.objects.filter(educator=educator)
        .values('subject')
        .annotate(total=Count('id'))
    )

    context = {
        "student_scores": json.dumps(student_scores, cls=DjangoJSONEncoder),
        "quiz_performance": json.dumps(quiz_performance, cls=DjangoJSONEncoder),
        "subject_quiz_count": json.dumps(subject_quiz_count, cls=DjangoJSONEncoder),
        "question_difficulty": json.dumps(question_difficulty, cls=DjangoJSONEncoder),
        "quiz_attempts_over_time": json.dumps(quiz_attempts_over_time, cls=DjangoJSONEncoder),
        "top_performers": json.dumps(top_performers, cls=DjangoJSONEncoder),
        "pass_fail_ratio": json.dumps(pass_fail_ratio, cls=DjangoJSONEncoder),
        "quiz_distribution": json.dumps(quiz_distribution, cls=DjangoJSONEncoder),
        'educator':educator,
    }

    return render(request, "educators/analytics.html", context)
def upload_questions(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('questions_file')
        quiz_id = request.POST.get('quiz_id')

        if not uploaded_file.name.endswith('.xlsx'):
            messages.error(request, "Only Excel files (.xlsx) are allowed.")
            return redirect('upload_questions')

        try:
            df = pd.read_excel(uploaded_file)

            required_columns = ['question_text', 'option1', 'option2', 'option3', 'option4', 'correct_option']
            for col in required_columns:
                if col not in df.columns:
                    messages.error(request, f'Missing column in file: {col}\nRequired Format {required_columns}')
                    return redirect('upload_questions')

            quiz = Quiz.objects.get(id=quiz_id)

            for _, row in df.iterrows():
                # Create the Question object
                question = Question.objects.create(
                    quiz=quiz,
                    text=row['question_text']
                )

                # Create options
                options = []
                correct_option_text = str(row['correct_option']).strip()

                for i in range(1, 5):
                    option_text = str(row[f'option{i}']).strip()
                    is_correct = (option_text == correct_option_text)

                    option = Option(
                        question=question,
                        text=option_text,
                        is_correct=is_correct
                    )
                    options.append(option)

                # Bulk create options (better performance)
                Option.objects.bulk_create(options)

            messages.success(request, 'Questions and options uploaded successfully!')
            return redirect('upload_questions')

        except Exception as e:
            messages.error(request, f'Error processing file: {e}')
            return redirect('upload_questions')

    quizzes = Quiz.objects.all()
    return render(request, 'educators/upload_questions.html', {'quizzes': quizzes})
