from django.contrib import admin

from mapservice.models import EatingPlace
from .models import Profile
from blog.models import PostImage

admin.site.register(Profile)
admin.site.register(PostImage)
admin.site.register(EatingPlace)