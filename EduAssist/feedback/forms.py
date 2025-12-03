from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your feedback...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get("rating")
        comment = cleaned_data.get("comment")

        if rating == 1 and not comment:
            raise forms.ValidationError("Please provide a comment to help us improve.")
