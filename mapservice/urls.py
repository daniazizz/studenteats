from django.urls import path
from mapservice import views
from mapservice.views import showPost

urlpatterns = [
    path('', views.map, name="blog-map"),
]