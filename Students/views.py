from django.shortcuts import render, redirect
from .forms import StudentForm
from django.contrib.auth.decorators import login_required
from Educators.models import Educator
from .models import Subject
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