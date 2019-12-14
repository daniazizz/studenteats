from django import forms
from .models import PostImage, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image']
