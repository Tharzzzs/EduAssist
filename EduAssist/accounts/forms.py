from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Add 'bio' and 'address' here if you want them editable in the form
        fields = ['contact', 'program', 'year_level'] 
        
        # Define widgets to add CSS classes for styling
        widgets = {
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'program': forms.Select(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}),
        }

class SearchForm(forms.Form):
    search = forms.CharField(
        required=False, 
        label='Search',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'})
    )