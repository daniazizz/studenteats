from django.contrib.auth.models import User
from mapservice.models import EatingPlace
from .models import Post

from rest_framework import serializers



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', ]


# Post serializer
class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    class Meta:
        model = Post
        fields = ['author', 'title', 'content', 'date_posted', 'rating', 'cost']      

class EatingPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EatingPlace
        fields = ['name', 'address']