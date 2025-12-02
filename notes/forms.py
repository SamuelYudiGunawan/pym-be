from django import forms
from .models import Note, Reply


class NoteForm(forms.ModelForm):
    """Form for creating new notes"""

    class Meta:
        model = Note
        fields = ['content', 'author_name']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Share your thoughts with the world...',
                'required': True
            }),
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional - leave blank to post anonymously)'
            })
        }
        labels = {
            'content': 'Your Thoughts',
            'author_name': 'Your Name (Optional)'
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 10:
            raise forms.ValidationError(
                "Please share at least 10 characters of your thoughts.")
        return content.strip()


class ReplyForm(forms.ModelForm):
    """Form for creating replies to notes"""

    class Meta:
        model = Reply
        fields = ['content', 'author_name']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your response...',
                'required': True
            }),
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional - leave blank to reply anonymously)'
            })
        }
        labels = {
            'content': 'Your Response',
            'author_name': 'Your Name (Optional)'
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 5:
            raise forms.ValidationError(
                "Please write at least 5 characters for your response.")
        return content.strip()

