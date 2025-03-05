from django.db import models
from Admin.models import User  # Import the custom User model
import Admin.models as Admin
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    educational_level = models.CharField(max_length=20, choices=Admin.EDUCATION_LEVEL_CHOICES)
    subjects = models.ManyToManyField('Subject', related_name='students')
    def __str__(self):
        return self.user.email
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    