from django.urls import path
from .views import (
    PostListView,
    PostDetailView, 
    PostDeleteView, 
    ProfileListView, 
    SearchResultListView, 
    PostUpdateView, 
    ProfileFollowToggle,
    ProfileFollowAPIToggle,
    PostLikeToggle,
    PostLikeAPIToggle,
    EatingPlaceListView,
    EatingPlacesAPI,
    autocompletePlaceName
    ) 
from . import views


urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('profile/<str:username>', ProfileListView.as_view(), name='profile'),
    # Eating place profile:
    path('place/<str:name>', EatingPlaceListView.as_view(), name='place-profile'),
    path('search/', SearchResultListView.as_view(), name='search-result'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'), ## variable inside url (primary key)
    #path('post/new/', PostCreateView.as_view(), name='post-create'), ## post creation
    path('post/new/', views.postCreate, name='post-create'), ## post creation
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('follow/<int:su_pk>/', ProfileFollowToggle.as_view(), name='follow'),
    path('api/follow/<int:su_pk>/', ProfileFollowAPIToggle.as_view(), name='api-follow'),
    path('like/<int:sp_pk>/', PostLikeToggle.as_view(), name='post-like'),
    path('api/like/<int:sp_pk>/', PostLikeAPIToggle.as_view(), name='api-post-like'),
    #path('api/Eatingplaces/', EatingPlacesAPI.as_view(), name='api-eatingplaces'),
    path(r'^api/Eatingplaces/', autocompletePlaceName, name='api-eatingplaces')
]
