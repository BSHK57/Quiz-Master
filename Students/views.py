from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentForm
from django.contrib.auth.decorators import login_required
from Educators.models import Educator
from Students.models import Subject,Student
from Quizzes.models import Quiz,Question,Option,StudentQuizAttempt
import random
from django.db.models import Avg, Max
@login_required
def student_dashboard(request):
    subjects = Subject.objects.all()
    selected_subject = None
    faculty_list = []
    error_message=None
    if request.method == "POST":
        selected_subject = request.POST.get('subject')
        if selected_subject:
            try:
                selected_subject_obj = Subject.objects.get(name=selected_subject)
                faculty_list = Educator.objects.filter(subject_specialization__icontains=selected_subject)

                # If no faculty found, set message
                if not faculty_list:
                    error_message = f"No faculty exists for {selected_subject_obj.name}."
            except Subject.DoesNotExist:
                error_message = "The selected subject does not exist."

    return render(request, 'students/dashboard.html', {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'faculty_list': faculty_list,
        'error_message': error_message,
    })
def quiz_setup(request):
    subject = request.GET.get('subject')

    if request.method == 'POST':
        difficulty = request.POST.get('difficulty')
        question_count = request.POST.get('question_count')

        # Redirect to the page where actual questions are displayed
        return redirect(f'/student/quiz_questions/?subject={subject}&difficulty={difficulty}&count={question_count}')

    return render(request, 'students/quiz_setup.html', {
        'subject': subject,
    })
def quiz_questions(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == 'GET':
        subject_name = request.GET.get('subject')
        difficulty = request.GET.get('difficulty')
        question_count = int(request.GET.get('count', 10))

        # Fetch quizzes matching subject
        quizzes = Quiz.objects.filter(title__icontains=subject_name)

        # Get all questions from these quizzes
        questions = Question.objects.filter(quiz__in=quizzes)

        # Shuffle and select required number of questions
        questions_list = list(questions)
        random.shuffle(questions_list)
        selected_questions = questions_list[:question_count]

        if not selected_questions:
            return render(request, 'students/quiz_questions.html', {
                'message': "No new questions available for the selected subject."
            })

        # Store selected question IDs in session
        request.session['selected_question_ids'] = [q.id for q in selected_questions]

        return render(request, 'students/quiz_questions.html', {
            'questions': selected_questions
        })

    elif request.method == 'POST':
        # Retrieve questions from session (ensures grading is based on displayed questions)
        selected_question_ids = request.session.get('selected_question_ids', [])
        questions = Question.objects.filter(id__in=selected_question_ids)

        if not questions.exists():
            return redirect('some_error_page')  # Handle edge case where session expired

        correct_count = 0
        wrong_count = 0

        for question in questions:
            selected_option_id = request.POST.get(f'question_{question.id}')

            if selected_option_id:
                try:
                    # Make sure the selected option belongs to the current question
                    selected_option = Option.objects.get(id=selected_option_id, question=question)
                    if selected_option.is_correct:
                        correct_count += 1
                    else:
                        wrong_count += 1
                except Option.DoesNotExist:
                    wrong_count += 1  # Invalid option (shouldn't happen in normal case)

            else:
                wrong_count += 1  # No option selected for this question

        total_questions = len(questions)
        score = (correct_count / total_questions) * 100

        # Assume all questions are from the same quiz
        quiz = questions.first().quiz

        # Save student's attempt
        StudentQuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=score
        )

        # Clear session data after grading
        request.session.pop('selected_question_ids', None)

        # Redirect to result page with scores
        return redirect('quiz_result', correct=correct_count, wrong=wrong_count, score=round(score, 2))

    return redirect('some_error_page')  # Fallback if request method is somehow invalid
def quiz_result(request, correct, wrong, score):
    score=float(score)
    return render(request, 'students/quiz_result.html', {
        'correct_count': correct,
        'wrong_count': wrong,
        'score': score
    })

def my_quizzes(request):
    print("My Quizzes View Accessed")

    student = Student.objects.get(user=request.user)  

    # Fetch all subjects the student is enrolled in (from ManyToMany relation)
    # Fetch selected subject from dropdown filter (from GET request)
    selected_subject = request.GET.get('subject')
    
    # Fetch quiz attempts for logged-in student, optionally filtered by subject
    attempts = (
        StudentQuizAttempt.objects
        .filter(student=student)
        .select_related('quiz')
        .order_by('quiz__title', '-completed_at')
    )

    if selected_subject:
        attempts = attempts.filter(quiz__subject__name=selected_subject)

    # Total unique quizzes attempted
    total_quizzes_attempted = len(set(attempt.quiz_id for attempt in attempts))

    # Average and highest scores
    average_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
    highest_score = attempts.aggregate(Max('score'))['score__max'] or 0

    # Group attempts by quiz title
    quizzes = {}
    for attempt in attempts:
        quiz_title = attempt.quiz.title
        if quiz_title not in quizzes:
            quizzes[quiz_title] = []
        quizzes[quiz_title].append(attempt)

    # Context for the template
    context = {
        'quizzes': quizzes,
        'total_quizzes_attempted': total_quizzes_attempted,
        'average_score': round(average_score, 2),
        'highest_score': highest_score,
        # Pass all subjects for dropdown
        'selected_subject': selected_subject,  # Pass selected subject (if any)
        'no_attempts_message': 'No quizzes attempted for this subject. Start now!' if selected_subject and not attempts else None
    }

    return render(request, 'students/my_quizzes.html', context)
def achievements(request):
    student = Student.objects.get(user=request.user)

    # Query to fetch highest score for each quiz title along with subject and latest attempt time
    highest_scores = (
        StudentQuizAttempt.objects
        .filter(student=student)
        .values('quiz__title', 'quiz__subject')  # Grouping by title and subject
        .annotate(
            highest_score=Max('score'),
            latest_attempt_time=Max('completed_at')
        )
    )

    quizzes = []
    for item in highest_scores:
        quizzes.append({
            'title': item['quiz__title'],
            'subject': item['quiz__subject'],
            'highest_score': item['highest_score'],
            'latest_attempt_time': item['latest_attempt_time']
        })

    context = {
        'quizzes': quizzes,
        'no_quizzes_message': "No quizzes attended. Explore more!" if not quizzes else None
    }

    return render(request, 'students/achievements.html', context)