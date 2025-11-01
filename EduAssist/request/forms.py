from django import forms
from accounts.models import Profile
from .models import Request


class SearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search requests...'})
    )


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'status', 'date', 'description', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter request title'}),
            'status': forms.Select(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your request...'}),
        }

    # Validation for attachments
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')

        if attachment:
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword']
            max_size = 5 * 1024 * 1024  # 5 MB limit

            if attachment.content_type not in allowed_types:
                raise forms.ValidationError("File type not allowed. Upload PDF, JPG, PNG, or DOC only.")
            if attachment.size > max_size:
                raise forms.ValidationError("File size exceeds 5 MB limit.")
        return attachment
