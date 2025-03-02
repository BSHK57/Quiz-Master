from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentForm
from django.contrib.auth.decorators import login_required
from Educators.models import Educator
from Students.models import Subject,Student
from Quizzes.models import Quiz,Question,Option,StudentQuizAttempt
import random
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
    subject_name = request.GET.get('subject')
    difficulty = request.GET.get('difficulty')
    question_count = int(request.GET.get('count', 10))
    # Fetch all quizzes directly related to this subject name
    quizzes = Quiz.objects.filter(title__icontains=subject_name)

    # Get all questions linked to these quizzes
    questions = Question.objects.filter(quiz__in=quizzes)

    # Randomly select requested number of questions
    questions_list = list(questions)
    random.shuffle(questions_list)
    selected_questions = questions_list[:question_count]

    if not selected_questions:
        return render(request, 'students/quiz_questions.html', {
            'message': "No new questions available for the selected subject."
        })

    if request.method == 'POST':
        correct_count = 0
        wrong_count = 0

        for question in selected_questions:
            selected_option_id = request.POST.get(f'question_{question.id}')
            if selected_option_id:
                selected_option = Option.objects.get(id=selected_option_id)
                if selected_option.is_correct:
                    correct_count += 1
                else:
                    wrong_count += 1
            else:
                wrong_count += 1  # Unanswered questions count as wrong

        total_questions = len(selected_questions)
        score = (correct_count / total_questions) * 100

        # Assume all questions belong to the same quiz (you could enhance this logic if needed)
        quiz = selected_questions[0].quiz

        # Save the attempt
        StudentQuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=score
        )

        return redirect('quiz_result', correct=correct_count, wrong=wrong_count, score=round(score, 2))

    return render(request, 'students/quiz_questions.html', {
        'questions': selected_questions
    })
    
def quiz_result(request, correct, wrong, score):
    score=float(score)
    return render(request, 'students/quiz_result.html', {
        'correct_count': correct,
        'wrong_count': wrong,
        'score': score
    })

