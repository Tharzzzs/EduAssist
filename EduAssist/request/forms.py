from django import forms
from accounts.models import Profile



class SearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search')