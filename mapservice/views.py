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
def map(request):
    restaurants = EatingPlace.objects.all()
    return render(request, 'mapservice/map.html', {'title': 'Map', 'restaurants' : restaurants})

#https://stackoverflow.com/questions/24152420/pass-dynamic-javascript-variable-to-django-python
def showPost(request):
    if request.method == 'GET':
        name = request.GET['name']
        address = request.GET['address']
        latitude = request.GET['latitude']
        longitude = request.GET['longitude']

        correspondingEatingPlaceID = EatingPlace.objects.get(name__icontains=name,  address__icontains=address, latitude__exact=latitude, longitude__exact=longitude)#.values('id'))[0]['id']
        correspondingPosts = correspondingEatingPlaceID.posts.all()#Post.objects.filter(place_id__exact=correspondingEatingPlaceID).order_by('-date_posted')
        return render(request, 'mapservice/map.html', {'posts' : correspondingPosts})# HttpResponse(correspondingPosts)
