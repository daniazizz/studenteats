from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
@login_required
def map(request):
    return render(request, 'mapservice/map.html', {'title': 'Map'})
