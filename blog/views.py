from django.shortcuts import render, get_object_or_404, redirect, reverse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from blog.models import Post, PostImage, Comment
from mapservice.models import EatingPlace
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
# Forms
from blog.forms import PostImageForm, PostForm
# Serializers
from blog.serializers import EatingPlaceSerializer, PostSerializer

from django.db.models import Q, Avg, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from geopy.geocoders import Bing
import json
from django.http import JsonResponse

# A very simple function-based view for the api page
def apipageview(request):
    return render(request, 'blog/api-page.html')
    
## Class-based ListView for the home page
# It provides:
# - Pagination
# - A filtered Post queryset
class PostListView(LoginRequiredMixin, ListView): 
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts' 
    paginate_by = 5

    # Filtering out the posts to the ones that are related to the users' following,  and his own posts
    def get_queryset(self):
        user = self.request.user
        following = user.profile.following.all()
        return Post.objects.filter(Q(author=user) | Q(author__profile__in=following)).order_by('-date_posted')


## Class-based ListView handeling eating place profile:
# Providing pagination, aswell as a filtered queryset of Posts and other data in context
class EatingPlaceListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/place_profile.html'
    context_object_name = 'posts'
    paginate_by = 5

    # Overriding the default get_context_data method, to add more context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avg_rating = 0
        avg_cost = 0
        posts = self.place.posts.all()

        # Checks wether or not there is atleast one post related to the place.
        if posts:
            # Calculates the average rating and cost
            avg_rating = round(posts.aggregate(Avg('rating'))['rating__avg'])
            avg_cost = round(posts.aggregate(Avg('cost'))['cost__avg'])

        context['selected_place'] = self.place
        context['average_rating'] = avg_rating
        context['average_cost'] = avg_cost
        context['title'] = self.place
        return context

    # Overriding the default get_queryset method, to only output posts related to the selected place
    def get_queryset(self):
        self.place = get_object_or_404(EatingPlace, name=self.kwargs.get('name'))
        return self.place.posts.all().order_by('-date_posted')


# View handeling user profiles
class ProfileListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 5

    # Passing extra data in the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_user'] = self.user
        context['following'] = self.user.profile.following.all()
        context['followers'] = self.user.profile.followers.all()
        context['title'] = self.user
        return context

    # Overriding the default get_queryset method, to only output posts related to the selected user
    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs.get('username'))
        return self.user.posts.all().order_by('-date_posted')


class SearchResultListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/search_result.html'  
    context_object_name = 'posts'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['title'] = 'Search results'
        return context

    def get_queryset(self):  
        query = self.request.GET.get('q')
        # If the query is empty, return all posts
        if query == None:  
            return Post.objects.all().order_by('-date_posted')
        # Else, filter the posts to the ones that contain the 'query' value in the title | author_username | place_name | place_address
        else:
            return Post.objects.filter(Q(title__icontains=query) | Q(author__username__icontains=query) | Q(
                place__name__icontains=query) | Q(place__address__icontains=query)).order_by('-date_posted')

# Simple class-based view, managing the discover page
class DiscoverView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/discover.html'  
    context_object_name = 'posts'
    paginate_by = 5


    def get_context_data(self, **kwargs):  
        context = super().get_context_data(**kwargs)
        context['title'] = 'Discover'
        return context

    # Providing a listing of all the posts, ordered by likes_count, and date_posted
    def get_queryset(self):
            return Post.objects.all().annotate(likes_count=Count('likes')).order_by('-likes_count', '-date_posted')


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Post Detail'
        return context


@login_required
def postCreate(request, p_name=None):
    # Inspiration for the multiple images ref: https://stackoverflow.com/questions/34006994/how-to-upload-multiple-images-to-a-blog-post-in-django
    PostImageFormSet = modelformset_factory(PostImage, form=PostImageForm, extra=3)

    if request.method == 'POST':
        # Fetching the information from the forms / input fields
        p_form = PostForm(request.POST)
        pi_formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())
        rating = request.POST.get('rating')
        cost = request.POST.get('cost')
        place_name = request.POST.get('place-name')
        place_address = request.POST.get('place-address')

        # Calling the Bing webservice, to locate the address
        locator = Bing(api_key="AozreVUVlwxpZVbVcf6FErTup90eXr3DFSdlltU6m5JHLRuVh0Cp3A5PGh1OzVZC")
        location = locator.geocode(place_address)
        

        if p_form.is_valid() and pi_formset.is_valid():
            # If the address is located (is valid), continue 
            if location!=None:
                # EatingPlace:
                # getting the longitude and latitude
                latitude = location.latitude
                longitude = location.longitude
                
                # Getting the Eating place object with that address, or creating a new one
                eating_place, _ = EatingPlace.objects.get_or_create(address=place_address, defaults={'name': place_name, 'latitude': latitude, 'longitude': longitude})

                # Post
                post_form = p_form.save(commit=False)
                post_form.author = request.user
                post_form.place = eating_place
                post_form.rating = rating
                post_form.cost = cost
                post_form.save()

                # Post Images
                # looping through all the images uploaded, and creating PostImage objects
                for form in pi_formset.cleaned_data:
                    if form:
                        image = form['image']
                        photo = PostImage(post=post_form, image=image)
                        photo.save()

                messages.success(request, f'Posted "{post_form}"')
                return redirect("/")
            else:
                # Address not located by webservice
                messages.warning(request, f'Invalid address "{place_address}"')
        else:
            print(p_form.errors, pi_formset.errors)
    else:
        # Providing empty forms on a get request
        p_form = PostForm()
        pi_formset = PostImageFormSet(queryset=PostImage.objects.none())
    
    place = None

    # If a place-name is provided in the url, then the related place object is provided to the template
    # Happens when a post is created for a specific place (write a review button, in place-profile)
    if p_name:
        place = EatingPlace.objects.get(name=p_name)

    context = {
        'p_form': p_form,
        'pi_formset': pi_formset,
        'title': 'New post',
        'place': place
    }

    return render(request, 'blog/post_create.html', context)

# Class based UpdateView for updating posts
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_update.html'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    ## Adding extra data in the context to pass on the template:
    def get_context_data(self, **kwargs):  
        context = super().get_context_data(**kwargs)
        # The post object is used by the template to complete the rating and cost fields
        context['post'] = self.get_object()
        return context

    def form_valid(self, form):
        # Reading the rating and cost fields from the form
        rating = self.request.POST.get('rating')
        cost = self.request.POST.get('cost')
        form.instance.author = self.request.user 
        form.instance.cost = cost
        form.instance.rating = rating
        return super().form_valid(form)


# Uses UserPassesTestMixin to check if the user requesting a post deletion, is the author of that post
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

## These two redirection toggles, are used when javascript is disabled in the user's browser: 

# Class-based RedirectView handeling the follow toggle logic in a redirection manner 
class ProfileFollowToggle(RedirectView):
    def get_redirect_url(self, *arg, **kwargs):
        s_user_id = self.kwargs['su_pk']
        s_user = get_object_or_404(User, id=s_user_id)
        c_user = self.request.user
        if c_user.is_authenticated:
            if s_user.profile in c_user.profile.following.all():
                c_user.profile.following.remove(s_user.profile)
                messages.warning(self.request, f'You unfollowed {s_user}')
            else:
                c_user.profile.following.add(s_user.profile)
                messages.success(self.request, f'You followed {s_user}')
        return reverse('profile', args=[s_user.username])

# Same as above, but for likes
class PostLikeToggle(RedirectView):
    def get_redirect_url(self, *arg, **kwargs):
        s_post_id = self.kwargs['sp_pk']
        s_post = get_object_or_404(Post, id=s_post_id)
        c_user = self.request.user
        if c_user.is_authenticated:
            if c_user in s_post.likes.all():
                s_post.likes.remove(c_user)
                messages.warning(self.request, f'You unliked {s_post}')
            else:
                s_post.likes.add(c_user)
                messages.success(self.request, f'You liked {s_post}')
        return reverse('post-detail', args=[s_post_id])


## API View handeling the 'toggling' logic (For AJAX calls)
# Used for like and follow functionalities
class ToggleAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication] 
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None, **kwargs):
        # 'type' could be 'like' or 'follow'
        type_ = request.POST.get('type')
        id_ = request.POST.get('id')
        current_user = self.request.user
        # Toggled, a boolean variable representing the state of the toggle
        toggled = 'undefined'
        # Count, a number representing the amount of objects (likes, followers) 
        count = 'undefined'

        # This method removes or adds an element to a set, depending on whether or not it is a memeber of the set.
        def toggle(el, set_):
            if el in set_.all():
                set_.remove(el)
                toggled = False
            else:
                set_.add(el)
                toggled = True

            return toggled
            
        # Uses the 'type' to trigger the correct functionality
        if current_user.is_authenticated:
            if type_ == 'like':
                selected_post = get_object_or_404(Post, id=id_)
                toggled = toggle(current_user, selected_post.likes)
                count = selected_post.likes.count()

            elif type_ == 'follow':
                selected_user = get_object_or_404(User, id=id_)
                toggled = toggle(selected_user.profile, current_user.profile.following)
                count = selected_user.profile.followers.count()

        data = {
            "toggled": toggled,
            "count": count
        }

        return Response(data)

## This api is used for the autocomplete functionality on the search field in the navigation bar.
# Returns a Json response with a listing of all post titles, usernames addresses eating place names/adresses starting with a given query
class SearchAutocompleteAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        # The query:
        q = request.GET.get('query', '')
        # Filterning out the sets:
        posts = Post.objects.filter(title__startswith=q)
        users = User.objects.filter(username__startswith=q)
        places = EatingPlace.objects.filter(name__startswith=q)
        locations = EatingPlace.objects.filter(address__icontains=q)
        # Building the result:
        results = []

        for r in posts:
            results.append(r.title)
        for r in users:
            results.append(r.username)
        for r in places:
            results.append(r.name)
        for r in locations:
            results.append(r.address)

        data = {
            "results": results,
        }
        return JsonResponse(data)


# API view handeling the comments logic
class CommentAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # Adding a comment (post request)
    def post(self, request, format=None):
        # Fetching the needed information from the request:
        post_id = request.POST.get('post_id')
        content = request.POST.get('content')
        author_name = request.POST.get('author')
        # Getting the related author and post:
        author = User.objects.get(username=author_name)
        post = Post.objects.get(id=post_id)
        # Creating the comment and saving it:
        new_comment = Comment(author=author, content=content, post=post)
        new_comment.save()
        # Returning the id of the new comment:
        data= {
            "comment_id": new_comment.id
        }
        return Response(data)

    # Deleting a comment (delete request)
    def delete(self, request, format=None):
        # Fetching the information:
        comment_id = request.POST.get('comment_id')
        # Getting the related comment:
        comment = Comment.objects.get(id=comment_id)

        # Checking if the user trying to delete the comment, is the author of the comment:
        if request.user == comment.author:
            comment.delete()

        return Response()

# API used for the eating place name field autocomplete when creating a new post
class EatingPlaceAutocompleteAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication] 
    permission_classes = [permissions.IsAuthenticated]
    # Returns a Json response with all the Eating Places names that start with a given query
    def get(self, request, format=None, **kwargs):
        # Fetching the query from the get request:
        q = request.GET.get('query', '')
        # Filtering out the set of Eating places
        queryset = EatingPlace.objects.filter(name__startswith=q)
        # Building the result:
        results = []

        for r in queryset:
            results.append(r.name)

        data = {
            "results": results,
        }
        return JsonResponse(data)

## API that provides the data of a specific eating place using a serializer
# Used for auto-completion of the address field inside a 'new-post form'.
class GetEatingPlaceAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        q = request.GET.get('query', '')
        queryset = EatingPlace.objects.filter(name=q)
        serializer = EatingPlaceSerializer(queryset, many=True)
        return Response(serializer.data)

## Public API that provides a listing of all the eating places currently inside the database.
# Makes use the EatingPlaceSerializer to serialize the data of the EatingPlace objects
class EPAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        queryset = EatingPlace.objects.all()
        serializer = EatingPlaceSerializer(queryset, many=True)

        return Response(serializer.data)

## Public API that provides a listing of all the posts currently inside the database.
# Very similair to the method above
class PostsAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication] 
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset, many=True)

        return Response(serializer.data)
