from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from mapservice.models import EatingPlace


@login_required
def map(request):
    restaurants = EatingPlace.objects.all()
    return render(request, 'mapservice/map.html', {'title': 'Map', 'restaurants' : restaurants})