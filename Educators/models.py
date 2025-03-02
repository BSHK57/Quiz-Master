from django.db import models
from Admin.models import User  # Import the custom User model

class Educator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject_specialization = models.CharField(default="",max_length=255)
    experience = models.IntegerField(default=0)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
    def get_subject_list(self):
        if self.subject_specialization:
            return self.subject_specialization.split(',')
        return []
    def set_subject_list(self, subject_list):
        self.subject_specialization = ','.join(subject_list)