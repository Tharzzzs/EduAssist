from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['contact', 'program', 'year_level']

class SearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search')