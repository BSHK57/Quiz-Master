from django.shortcuts import render
from django.db.models import Avg
from django.http import HttpResponse
import csv
from .models import StudentQuizAttempt, Quiz
import json


def quiz_dashboard(request):
    if not request.user.is_authenticated:
        return render(request, 'quiz_app/login.html', {"error": "Please log in first."})

    student = request.user.student

    # Total Quizzes Attempted
    total_quizzes = StudentQuizAttempt.objects.filter(student=student).count()

    # Average Score
    average_score = StudentQuizAttempt.objects.filter(student=student).aggregate(Avg('score'))['score__avg']
    if average_score is None:
        average_score = 0

    # Progress Chart Data (Last 5 Quiz Scores)
    attempts = StudentQuizAttempt.objects.filter(student=student).order_by('-completed_at')[:5]
    labels = [attempt.quiz.title for attempt in attempts]
    scores = [attempt.score for attempt in attempts]
    print(labels,scores)
    # Subject-Wise Performance
    subject_labels = []
    subject_scores = []
    subjects = Quiz.objects.values_list('subject', flat=True).distinct()

    for subject in subjects:
        subject_labels.append(subject)
        avg_score = StudentQuizAttempt.objects.filter(student=student, quiz__subject=subject).aggregate(Avg('score'))['score__avg']
        subject_scores.append(avg_score if avg_score is not None else 0)

    # Leaderboard (Top 5 Students)
    leaderboard = StudentQuizAttempt.objects.values_list('student__user__username', 'score').order_by('-score')[:5]

    # Personalized Recommendations
    recommendations = []
    if average_score < 50:
        recommendations.append("Try reviewing concepts and taking more practice quizzes.")
    elif 50 <= average_score < 75:
        recommendations.append("You're doing well! Focus on weaker subjects.")
    else:
        recommendations.append("Excellent work! Keep maintaining your progress.")

    context = {
        "total_quizzes": total_quizzes,
        "average_score": round(average_score, 2),
        "labels": labels,
        "scores": scores,
        "subject_labels": subject_labels,
        "subject_scores": subject_scores,
        "leaderboard": leaderboard,
        "recommendations": recommendations,
        "user":request.user,
    }
    context['scores'] = json.dumps(scores if scores else [])
    context['labels'] = json.dumps(labels if labels else [])
    context['subject_labels'] = json.dumps(subject_labels if subject_labels else [])
    context['subject_scores'] = json.dumps(subject_scores if subject_scores else [])



    return render(request, "quiz/dashboard.html", context)



def leaderboard(request):
    leaderboard = StudentQuizAttempt.objects.values_list('student__user__username', 'score').order_by('-score')[:10]
    return render(request, "quiz/leaderboard.html", {"leaderboard": leaderboard})


def download_report(request):
    if not request.user.is_authenticated:
        return HttpResponse("You need to log in to download the report.")

    student = request.user.student
    attempts = StudentQuizAttempt.objects.filter(student=student)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="quiz_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Quiz Title', 'Score', 'Completed At'])

    for attempt in attempts:
        writer.writerow([attempt.quiz.title, attempt.score, attempt.completed_at])

    return response
