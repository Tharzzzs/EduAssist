from django.db import models
from django.contrib.auth.models import User
from eduassist_app.storages_backend import SupabaseStorage

# Create your models here.
class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    date = models.DateField()
    description = models.TextField()
    attachment = models.FileField(storage=SupabaseStorage(), blank=True, null=True)
    def __str__(self):
        return self.title