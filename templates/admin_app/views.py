from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required
from Students.models import Subject, Faculty,Student
from Educators.models import Educator
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
                faculty_list = Educator.objects.filter(subjects__icontains=selected_subject)

                # If no faculty found, set message
                if not faculty_list:
                    error_message = f"No faculty exists for {selected_subject_obj.name}."
            except Subject.DoesNotExist:
                error_message = "The selected subject does not exist."

    return render(request, 'admin_app/student_dashboard.html', {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'faculty_list': faculty_list,
        'error_message': error_message,
    })
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

    return render(request, 'admin_app/educator_dashboard.html', {
        'subjects': subjects,
        'selected_subject_names': selected_subject_names
    })

@login_required
def admin_dashboard(request):
    users_count = User.objects.count()
    return render(request, 'admin_app/admin_dashboard.html', {'users_count': users_count})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            # Check if user already exists (by username or email)
            if User.objects.filter(username=username).exists():
                messages.error(request, "User with this username already registered.")
                return redirect('register')  # Redirect back to registration page

            if User.objects.filter(email=email).exists():
                messages.error(request, "User with this email already registered.")
                return redirect('register')

            # Save user to User table
            user = form.save()

            # Automatically log the user in
            login(request, user)

            # Based on role, save to Student or Faculty table
            if user.role == 'student':
                Student.objects.create(user=user, education_level='school')  # Set a default or get from form if present
                messages.success(request, "Student registered successfully.")
                return redirect('student_dashboard')

            elif user.role == 'educator':
                Faculty.objects.create(user=user, subjects='')  # You can later update subjects
                messages.success(request, "Educator registered successfully.")
                return redirect('educator_dashboard')

            else:
                messages.success(request, "Admin registered successfully.")
                return redirect('admin_app_dashboard')

        else:
            # Print form errors to console (for debugging during development)
            print(form.errors)

    else:
        form = UserRegistrationForm()

    return render(request, 'admin_app/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'educator':
                return redirect('educator_dashboard')
            else:
                return redirect('admin_app_dashboard')
    else:
        form = LoginForm()
    return render(request, 'admin_app/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login')

def forgot_password_step1(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            return redirect(reverse('forgot_password_step2', kwargs={'email': email}))
        except User.DoesNotExist:
            messages.error(request, "This email is not registered.")
            return redirect('forgot_password_step1')
    return render(request, 'admin_app/forgot_password_step1.html')

def forgot_password_step2(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "Invalid email.")
        return redirect('forgot_password_step1')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse('forgot_password_step2', kwargs={'email': email}))

        user.password = make_password(password1)
        user.save()

        messages.success(request, "Your password has been reset successfully.")
        return redirect('login')
    return render(request, 'admin_app/forgot_password_step2.html', {'email': email})
