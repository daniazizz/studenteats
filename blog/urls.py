from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView, SearchResultListView
from . import views


urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-post'),
    path('search/', SearchResultListView.as_view(), name='search-result'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'), ## variable inside url (primary key)
    path('post/new/', PostCreateView.as_view(), name='post-create'), ## post creation
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('map', views.map, name='blog-map'),
]
