from django import forms
# accounts.models import Profile is unused in this file and can be removed, 
# but I will leave it if it's used elsewhere in your project
from accounts.models import Profile 
from .models import Request, Category, Tag 


class SearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search requests...'})
    )


class RequestForm(forms.ModelForm):
    # Overriding the default tags field to use CheckboxSelectMultiple for simplicity 
    # in standard forms, but a custom widget is needed for Auto-Suggest
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control tagging-field', 
                                           'data-api-url': '/api/tags/autosuggest/'}),
        help_text="Select one or more tags. (Note: A custom JavaScript widget is required for auto-suggest functionality to work fully.)"
    )

    class Meta:
        model = Request
        # Including category and tags now
        # Removed 'date' and 'status' as they are often system/staff-controlled on creation/user submission
        fields = ['title', 'priority', 'category', 'tags', 'description', 'attachment']
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter request title'}),
            # Priority is a ChoiceField, handled by Select
            'priority': forms.Select(attrs={'class': 'form-select'}), 
            # Category is a ForeignKey, handled by Select
            'category': forms.Select(attrs={'class': 'form-select'}), 
            'description': forms.Textarea(attrs={'placeholder': 'Describe your request...', 'rows': 5}),
        }

    # Validation for attachments (kept original logic)
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')

        if attachment:
            # Added DOCX MIME type for completeness
            allowed_types = [
                'application/pdf', 
                'image/jpeg', 
                'image/png', 
                'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            max_size = 5 * 1024 * 1024  # 5 MB limit

            if attachment.content_type not in allowed_types:
                raise forms.ValidationError("File type not allowed. Upload PDF, JPG, PNG, or DOC/DOCX only.")
            if attachment.size > max_size:
                raise forms.ValidationError("File size exceeds 5 MB limit.")
        return attachment