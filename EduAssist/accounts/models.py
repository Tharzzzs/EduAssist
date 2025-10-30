from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=15)
    program = models.CharField(max_length=100)
    year_level = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username}'s Profile"
class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.title