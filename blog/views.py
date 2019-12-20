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

from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from geopy.geocoders import Bing
import json
from django.http import JsonResponse


def apipageview(request):
    return render(request, 'blog/api-page.html')
    

class PostListView(LoginRequiredMixin, ListView): 
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts' 
    paginate_by = 5

    # Filtering out the posts to the ones that are related to the users following and his own posts
    def get_queryset(self):
        user = self.request.user
        following = user.profile.following.all()
        return Post.objects.filter(Q(author=user) | Q(author__profile__in=following)).order_by('-date_posted')


# View handeling eating place profile:
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

        # Checks wether or not there are posts related to the place.
        if posts:
            # Calculates the average
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

class ToggleAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  # differnce with ToeknAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        type_ = request.GET.get('type')
        id = request.GET.get('id')
        c_user = self.request.user

        toggled = 'error'
        count = 'error'

        if c_user.is_authenticated:
            if type_ == 'like':
                selected_post = get_object_or_404(Post, id=id)
                if c_user in selected_post.likes.all():
                    selected_post.likes.remove(c_user)
                    toggled = False
                else:
                    selected_post.likes.add(c_user)
                    toggled = True
                count = selected_post.likes.count()

            elif type_ == 'follow':
                selected_user = get_object_or_404(User, id=id)
                if c_user != selected_user and selected_user.profile in c_user.profile.following.all():
                    c_user.profile.following.remove(selected_user.profile)
                    toggled = False
                else:
                    c_user.profile.following.add(selected_user.profile)
                    toggled = True

                count = selected_user.profile.followers.count()


        data = {
            "toggled": toggled,
            "count": count
        }

        return Response(data)
       
class SearchAutocompleteAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        q = request.GET.get('query', '')
        posts = Post.objects.filter(title__startswith=q)
        users = User.objects.filter(username__startswith=q)
        places = EatingPlace.objects.filter(name__startswith=q)
        locations = EatingPlace.objects.filter(address__icontains=q)

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


class EatingPlacesAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  # difference with TokenAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        q = request.GET.get('query', '')
        queryset = EatingPlace.objects.filter(name__startswith=q)
        results = []

        for r in queryset:
            results.append(r.name)

        data = {
            "results": results,
        }
        return JsonResponse(data)


class CommentAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  # difference with TokenAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        post_id = request.GET.get('post_id')
        content = request.GET.get('content')
        author_name = request.GET.get('author')

        author = User.objects.get(username=author_name)
        post = Post.objects.get(id=post_id)
        new_comment = Comment(author=author, content=content, post=post)
        new_comment.save()

        data= {
            "comment_id": new_comment.id
        }

        return Response(data)

class DeleteCommentAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  # difference with TokenAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        comment_id = request.GET.get('comment_id')
        print(comment_id)
        
        comment = Comment.objects.get(id=comment_id)
        comment.delete()

        return Response()



class GetEatingPlaceAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  # difference with TokenAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        q = request.GET.get('query', '')
        queryset = EatingPlace.objects.filter(name=q)
        serializer = EatingPlaceSerializer(queryset, many=True)
        print(q)

        return Response(serializer.data)

class EPAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  # difference with TokenAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        queryset = EatingPlace.objects.all()
        serializer = EatingPlaceSerializer(queryset, many=True)

        return Response(serializer.data)


class PostsAPI(APIView):
    authentication_classes = [authentication.SessionAuthentication]  # difference with TokenAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset, many=True)

        return Response(serializer.data)


class SearchResultListView(LoginRequiredMixin, ListView):  # A class based view
    model = Post
    template_name = 'blog/search_result.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'  # This makes it so that the list of objects is called posts.

    # as default, the name is ObjectList
    # paginate_by = 5

    def get_context_data(self, **kwargs):  ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['title'] = 'Search results'
        return context

    def get_queryset(self):  ## filters posts list to the ones from user
        query = self.request.GET.get('q')
        if query == None:  ## If the query is empty, return all posts
            return Post.objects.all().order_by('-date_posted')
        else:
            return Post.objects.filter(Q(title__icontains=query) | Q(author__username__icontains=query) | Q(
                place__name__icontains=query) | Q(place__address__icontains=query)).order_by('-date_posted')


class PostDetailView(LoginRequiredMixin, DetailView):  # A class based view
    model = Post

    def get_context_data(self, **kwargs):  ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['title'] = 'Post Detail'
       #s context['comments'] = 'Post Detail'
        return context


# Reference: https://stackoverflow.com/questions/34006994/how-to-upload-multiple-images-to-a-blog-post-in-django
@login_required
def postCreate(request, p_name=None):
    PostImageFormSet = modelformset_factory(PostImage,
                                            form=PostImageForm, extra=3)

    if request.method == 'POST':

        p_form = PostForm(request.POST)
        pi_formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())
        rating = request.POST.get('rating')
        cost = request.POST.get('cost')
        place_name = request.POST.get('place-name')
        place_address = request.POST.get('place-address')

        locator = Bing(api_key="AozreVUVlwxpZVbVcf6FErTup90eXr3DFSdlltU6m5JHLRuVh0Cp3A5PGh1OzVZC")
        location = locator.geocode(place_address)
        

        if p_form.is_valid() and pi_formset.is_valid():
            if location!=None:
                # EatingPlace
                print(location)
                latitude = location.latitude
                longitude = location.longitude

                # Can use default to ignore some fields in get
                eating_place, _ = EatingPlace.objects.get_or_create(address=place_address, defaults={'name': place_name, 'latitude': latitude, 'longitude': longitude})

                # Post
                post_form = p_form.save(commit=False)
                post_form.author = request.user
                post_form.place = eating_place
                post_form.rating = rating
                post_form.cost = cost
                post_form.save()

                # Post Images
                for form in pi_formset.cleaned_data:
                    if form:
                        image = form['image']
                        photo = PostImage(post=post_form, image=image)
                        photo.save()

                messages.success(request, f'Posted "{post_form}"')
                return redirect("/")
            else:
                messages.warning(request, f'Invalid address "{place_address}"')
        else:
            print(p_form.errors, pi_formset.errors)
    else:
        p_form = PostForm()
        pi_formset = PostImageFormSet(queryset=PostImage.objects.none())
    
    place = None

    if p_name:
        place = EatingPlace.objects.get(name=p_name)

    context = {
        'p_form': p_form,
        'pi_formset': pi_formset,
        'title': 'New post',
        'place': place
    }

    return render(request, 'blog/post_create.html', context)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_update.html'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):  ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        return context

    def form_valid(self, form):
        rating = self.request.POST.get('rating')
        cost = self.request.POST.get('cost')
        form.instance.author = self.request.user  ## Setting the author to the current logged in user
        form.instance.cost = cost
        form.instance.rating = rating
        return super().form_valid(form)


# Uses UserPassesTestMixin to check if the user requesting a post deletion is the author of that post
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author