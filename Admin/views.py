from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, LoginForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def student_dashboard(request):
    return render(request, 'admin_app/student_dashboard.html')

@login_required
def educator_dashboard(request):
    return render(request, 'admin_app/educator_dashboard.html')

@login_required
def admin_dashboard(request):
    users_count = User.objects.count()
    return render(request, 'admin_app/admin_dashboard.html', {'users_count': users_count})

def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'educator':
                return redirect('educator_dashboard')
            else:
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
    return redirect('login')
