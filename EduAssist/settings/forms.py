# settings/forms.py
from django import forms
from .models import UserSettings

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ['is_dark_mode', 'receive_email_notifications', 'profile_visibility']
