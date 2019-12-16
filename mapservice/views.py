from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView

from blog.models import Post
from mapservice.models import EatingPlace

# Create your views here.

@login_required
def map(request, name='##undefined##', address='##undefined##'):

    restaurants = EatingPlace.objects.all()
    selected_place = EatingPlace.objects.filter(name__icontains=name, address__icontains=address)
    posts = Post.objects.all()
    
    if  selected_place:
        selected_place = selected_place.first()
        posts = selected_place.posts.all()
        return render(request, 'mapservice/map.html', {'title' : 'Map', 'restaurants' : restaurants, 'posts' : posts,'show_posts' : True, 'selected_place': selected_place})
    else:
        return render(request, 'mapservice/map.html', {'title' : 'Map', 'restaurants' : restaurants, 'show_posts' : False})


   # return render(request, 'mapservice/map.html', {'title': 'Map', 'restaurants' : restaurants})##'restaurants' : restaurants, 'posts': posts})
