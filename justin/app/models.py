from django.db import models
from django.contrib.auth.models import User


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to the User model
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.user.email
