from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Educator
from Students.models import Subject

@login_required
def educator_dashboard(request):
    if request.user.role != 'educator':
        return redirect('login')  # Ensure only educators access this

    subjects = Subject.objects.all()

    if request.method == 'POST':
        selected_subject_names = request.POST.getlist('subjects')

        # Create any missing subjects in the Subject table
        for name in selected_subject_names:
            Subject.objects.get_or_create(name=name)

        # Save selected subjects to Educator model as a comma-separated string
        educator, created = Educator.objects.get_or_create(user=request.user)
        educator.set_subject_list(selected_subject_names)
        educator.save()

        messages.success(request, "Subjects have been updated successfully.")
    else:
        # Preload previously selected subjects (split stored string into list)
        try:
            educator = Educator.objects.get(user=request.user)
            selected_subject_names = educator.get_subject_list()
        except Educator.DoesNotExist:
            selected_subject_names = []

    return render(request, 'educators/dashboard.html', {
        'subjects': subjects,
        'selected_subject_names': selected_subject_names
    })
    # return render(request, 'educators/dashboard.html')
