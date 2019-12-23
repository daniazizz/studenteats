from django import forms
from blog.models import PostImage, Post, Comment

# Class based forms for posts and post-images:

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image']
