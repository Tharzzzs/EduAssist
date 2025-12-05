from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=15)
    program = models.CharField(max_length=100)
    year_level = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.user.username}'s Profile"
