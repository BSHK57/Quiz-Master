from django.db import models
from Admin.models import User  # Import the custom User model

class Educator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expertise = models.CharField(max_length=255, blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
