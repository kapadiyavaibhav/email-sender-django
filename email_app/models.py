from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    app_password = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.email})"


class EmailHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} → {self.recipient}"