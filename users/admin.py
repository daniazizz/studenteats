from django.contrib import admin
from .models import Profile
from blog.models import PostImage

admin.site.register(Profile)
admin.site.register(PostImage)