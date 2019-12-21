from django.urls import path
from blog.views import (
    PostListView,
    PostDetailView, 
    PostDeleteView, 
    ProfileListView, 
    SearchResultListView, 
    PostUpdateView, 
    ProfileFollowToggle,
    PostLikeToggle,
    EatingPlaceListView,
    EatingPlaceAutocompleteAPI,
    GetEatingPlaceAPI,
    PostsAPI,
    SearchAutocompleteAPI,
    CommentAPI,
    EPAPI,
    apipageview,
    ToggleAPI
    ) 
from blog import views


urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('profile/<str:username>', ProfileListView.as_view(), name='profile'),
    # Eating place profile:
    path('place/<str:name>', EatingPlaceListView.as_view(), name='place-profile'),
    path('search/', SearchResultListView.as_view(), name='search-result'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'), ## variable inside url (primary key)
    #Post create:
    path('post/new/', views.postCreate, name='post-create'), ## post creation
    path('post/new/<str:p_name>/', views.postCreate, name='post-create-w-name'), ## post creation with name

    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    
    path('comment/', CommentAPI.as_view(), name='comment'),
    path('follow/<int:su_pk>/', ProfileFollowToggle.as_view(), name='follow'),
    path('like/<int:sp_pk>/', PostLikeToggle.as_view(), name='post-like'),

    path('api', apipageview, name='api-page'),
    path('replace', apipageview, name='api-page'),


    # APIs
    path('api/toggle/', ToggleAPI.as_view(), name='api-toggle'),
    path('api/Eatingplaces/', EatingPlaceAutocompleteAPI.as_view(), name='api-eatingplace-autocomplete'),
    path('api/SearchAutocomplete/', SearchAutocompleteAPI.as_view(), name='api-search-autocomplete'),
    path('api/GetEatingplace/', GetEatingPlaceAPI.as_view(), name='api-get-eatingplace'),

    # Public APIs
    path('api/Posts/', PostsAPI.as_view(), name='api-posts'),
    path('api/EPS/', EPAPI.as_view(), name='api-ep')
]
