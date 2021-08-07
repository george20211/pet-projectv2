from django import forms

from posts.models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ("text", "group", "image",)
        labels = {
            "text": "текст",
            "group": "группа"
        }
        help_text = "Введите текст"


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {'text': forms.Textarea(attrs={'cols': 40, 'rows': 3})}
