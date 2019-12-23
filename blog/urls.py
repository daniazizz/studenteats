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
    ToggleAPI,
    DiscoverView
    ) 
from blog import views


urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('profile/<str:username>', ProfileListView.as_view(), name='profile'),
    path('place/<str:name>', EatingPlaceListView.as_view(), name='place-profile'), # Eating place profile
    path('search/', SearchResultListView.as_view(), name='search-result'), # Search results 
    path('discover/', DiscoverView.as_view(), name='discover'),
    path('api', apipageview, name='api-page'),

    #Post:
    path('post/new/', views.postCreate, name='post-create'), # Post create without place name
    path('post/new/<str:p_name>/', views.postCreate, name='post-create-w-name'), # Post create with place name (place-name and place-address fields  in form are auto-filled)
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    
    # Toggling like/follow (when javascript is disabled (no ajax))
    path('follow/<int:su_pk>/', ProfileFollowToggle.as_view(), name='follow'),
    path('like/<int:sp_pk>/', PostLikeToggle.as_view(), name='post-like'),

    # APIs
    path('api/toggle/', ToggleAPI.as_view(), name='api-toggle'), # Used to toggle like/follow (ajax)
    path('api/Eatingplaces/', EatingPlaceAutocompleteAPI.as_view(), name='api-eatingplace-autocomplete'), # Autocomplete in post creation form (place name field)
    path('api/SearchAutocomplete/', SearchAutocompleteAPI.as_view(), name='api-search-autocomplete'), # Autocomplete on searchbar in navbar
    path('api/GetEatingplace/', GetEatingPlaceAPI.as_view(), name='api-get-eatingplace'), # Used to get a specific eating place (serialized data (ajax))
    path('comment/', CommentAPI.as_view(), name='comment'), # Used to post or delete comments (ajax)

    # Public APIs
    path('api/Posts/', PostsAPI.as_view(), name='api-posts'),
    path('api/EPS/', EPAPI.as_view(), name='api-ep')
]
