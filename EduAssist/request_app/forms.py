from django import forms
from accounts.models import Profile
from .models import Request, Tag, Category  # Import Category model

class SearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search requests...'})
    )

class RequestForm(forms.ModelForm):
    # Tags field stays the same
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control tagging-field',
            'data-api-url': '/api/tags/autosuggest/'
        }),
        help_text="Select one or more tags. (Note: Auto-suggest requires JS widget.)"
    )

    # Category field now comes from the database
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,  # optional
        empty_label="Select a category",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Request
        fields = ['title', 'priority', 'category', 'tags', 'description', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter request title'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your request...', 'rows': 5}),
        }

    # Validation for attachments
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            allowed_types = [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            max_size = 5 * 1024 * 1024  # 5 MB

            if attachment.content_type not in allowed_types:
                raise forms.ValidationError(
                    "File type not allowed. Upload PDF, JPG, PNG, DOC/DOCX only."
                )
            if attachment.size > max_size:
                raise forms.ValidationError("File size exceeds 5 MB limit.")
        return attachment
