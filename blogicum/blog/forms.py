from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Model Form for post creating with datetime picker"""

    class Meta:
        model = Post
        widgets = {'pub_date': forms.DateTimeInput(
            attrs={'type': 'datetime-local'})}
        exclude = ('author', 'comments')


class CommentsForm(forms.ModelForm):
    """Model form for creating comments on posts"""

    class Meta:
        model = Comment
        fields = ('text',)
        # widgets = {'text': forms.Textarea(attrs={"rows": "10", "cols": "20"})}
