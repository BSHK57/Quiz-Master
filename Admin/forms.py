from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from . import models as Admin
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    name=forms.CharField(required=True,max_length=100)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES)
    address = forms.CharField(required=False)
    educational_level = forms.ChoiceField(required=False, choices=Admin.EDUCATION_LEVEL_CHOICES)
    subject_specialization = forms.CharField(required=False, max_length=100)
    experience = forms.IntegerField(required=False, min_value=0)

    class Meta:
        model = User
        fields = ['username', 'name','email', 'password1', 'password2', 'dob', 'gender',
                   'address', 'role','educational_level', 'subject_specialization',
                     'experience']

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
