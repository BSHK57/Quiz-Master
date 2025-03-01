from django.contrib import admin

# Register your models here.
from .models import User,AdminUser
# Register your models here.
admin.site.register(User)
admin.site.register(AdminUser)