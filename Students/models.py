from django.db import models
from Admin.models import User  # Import the custom User model
import Admin.models as Admin
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    education_level = models.CharField(max_length=20, choices=Admin.EDUCATION_LEVEL_CHOICES)

    def __str__(self):
        return self.user.email
