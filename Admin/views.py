from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, LoginForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from Students.models import Student
from Educators.models import Educator
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.contrib import messages


User = get_user_model()

# @login_required
# def student_dashboard(request):
#     return render(request, 'admin_app/student_dashboard.html')

# @login_required
# def educator_dashboard(request):
#     return render(request, 'admin_app/educator_dashboard.html')

@login_required
def admin_dashboard(request):
    users_count = User.objects.count()
    return render(request, 'admin_app/admin_dashboard.html', {'users_count': users_count})

def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save to DB yet
            user.set_password(form.cleaned_data['password1'])  # Hash password
            user.save()
            role = form.cleaned_data['role']
            # Save user in the appropriate app model with form data
            if role == 'student':
                educational_level = form.cleaned_data['educational_level']
                Student.objects.create(user=user, educational_level=educational_level)
                login(request, user)
                return redirect('student_dashboard')
            elif role == 'educator':
                subject_specialization = form.cleaned_data['subject_specialization']
                experience = form.cleaned_data['experience']
                Educator.objects.create(user=user, subject_specialization=subject_specialization, experience=experience)
                login(request, user)
                return redirect('educator_dashboard')
            else:
                login(request, user)
                return redirect('admin_dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'admin_app/register.html', {'form': form})

def login_user(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'educator':
                return redirect('educator_dashboard')
            else:
                return redirect('admin_dashboard')
    else:
        form = LoginForm()
    return render(request, 'admin_app/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('home')
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
def home(request):
    return render(request, 'admin_app/home.html')
