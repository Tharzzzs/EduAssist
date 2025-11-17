from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)
    receive_email = models.BooleanField(default=True)
    receive_sms = models.BooleanField(default=False)
    receive_push = models.BooleanField(default=True)
    profile_visible = models.BooleanField(default=True)
    allow_data_sharing = models.BooleanField(default=False)
    notification_email = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Settings"
