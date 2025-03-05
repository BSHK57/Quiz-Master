

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

EDUCATION_LEVEL_CHOICES = (
    ('High School', 'High School'),
    ('Undergraduate', 'Undergraduate'),
    ('Postgraduate', 'Postgraduate'),
    ('Doctorate', 'Doctorate'),
)

class User(AbstractUser):
    GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
    )
    email = models.EmailField(unique=True)
    name= models.CharField(max_length=100,default="")
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=[('student', 'Student'), ('educator', 'Educator'), ('admin', 'Admin')])

    USERNAME_FIELD = 'email'  # Use email for login instead of username
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class AdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
