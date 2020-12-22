from django import forms
from .models import Post, Comments

class PostModelForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows":2}))
    class Meta:
        model = Post
        fields = ('content', 'image')

class CommentsModelForm(forms.ModelForm):
    body = forms.CharField(label="",
                          widget=forms.TextInput(attrs={'placeholder':'Add a comment...'}))

    class Meta:
        model  = Comments
        fields = ('body',) 