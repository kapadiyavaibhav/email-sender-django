from django.contrib import admin
from .models import UserProfile, EmailHistory, Contact

admin.site.register(UserProfile)
admin.site.register(EmailHistory)
admin.site.register(Contact)
