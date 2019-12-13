from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def map(request):
    return render(request, 'map.html')