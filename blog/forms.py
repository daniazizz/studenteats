from django import forms
from .models import PostImage


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image']
        