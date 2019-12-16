from django.urls import path
from mapservice import views


urlpatterns = [
    path('', views.map, name="blog-map"),
    path('/<str:name>/<str:address>/', views.map, name="blog-map2"),
]