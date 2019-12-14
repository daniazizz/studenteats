from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from mapservice.models import EatingPlace

# Create your views here.
@login_required
def map(request):
    restaurants = EatingPlace.objects.all()
    return render(request, 'mapservice/map.html', {'title': 'Map', 'restaurants' : restaurants})
