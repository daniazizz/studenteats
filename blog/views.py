from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin  # Login required for posting,... User has to be the author for updating
from django.contrib.auth.models import User
from .models import Post, PostImage
from mapservice.models import EatingPlace
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from .forms import PostImageForm, PostForm
from mapservice.forms import EatingPlaceFrom
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from geopy.geocoders import Bing

class PostListView(LoginRequiredMixin, ListView):  # A class based view
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'  # This makes it so that the list of objects is called posts.
    # as default, the name is ObjectList
    ordering = ['-date_posted']  # Minus symbol to reverse ordering
    paginate_by = 5

    def get_queryset(self):  # filters posts list to the ones from user
        user = self.request.user
        following = user.profile.following.all()
        return Post.objects.filter(Q(author=user) | Q(author__profile__in=following)).order_by(
            '-date_posted')  # Filtering out the posts to the posts of following or own posts

# View handeling the eating place page:
class EatingPlaceListView(LoginRequiredMixin, ListView):  # A class based view
    model = Post
    template_name = 'blog/place_profile.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']  # Minus symbol to reverse ordering
    paginate_by = 5

    def get_context_data(self, **kwargs):  ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['selected_place'] = self.place
        context['title'] = self.place
        return context

    def get_queryset(self):  # filters posts list to the ones from user
        self.place = get_object_or_404(EatingPlace, name=self.kwargs.get('name'))
        return Post.objects.filter(place=self.place).order_by('-date_posted')



class ProfileListView(LoginRequiredMixin, ListView):  # A class based view
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'  # This makes it so that the list of objects is called posts.
    # as default, the name is ObjectList
    ordering = ['-date_posted']  # Minus symbol to reverse ordering
    paginate_by = 5

    def get_context_data(self, **kwargs):  ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['selected_user'] = self.user
        context['following'] = self.user.profile.following.all()
        context['followers'] = self.user.profile.followers.all()
        context['title'] = self.user
        return context

    def get_queryset(self):  # filters posts list to the ones from user
        self.user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=self.user).order_by('-date_posted')


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

class ProfileFollowAPIToggle(APIView):

    authentication_classes = [authentication.SessionAuthentication]# differnce with ToeknAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        s_user_id = self.kwargs['su_pk']
        s_user = get_object_or_404(User, id=s_user_id)
        c_user = self.request.user
        followed = False
        if c_user.is_authenticated and c_user != s_user: # A user cannot follow himself
            if s_user.profile in c_user.profile.following.all():
                c_user.profile.following.remove(s_user.profile)
                followed = False
            else:
                c_user.profile.following.add(s_user.profile)
                followed = True
        followersCount = s_user.profile.followers.count()
        data = {
            "followed": followed,
            "followersCount": followersCount
        }

        return Response(data)



class PostLikeAPIToggle(APIView):
    authentication_classes = [authentication.SessionAuthentication]  # difference with TokenAuthentication??
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, **kwargs):
        s_post_id = self.kwargs['sp_pk']
        s_post = get_object_or_404(Post, id=s_post_id)
        c_user = self.request.user
        liked = False

        if c_user.is_authenticated:
            if c_user in s_post.likes.all():
                s_post.likes.remove(c_user)
                liked = False
            else:
                s_post.likes.add(c_user)
                liked = True
                
        data = {
            "liked": liked,
            "likeCount": s_post.likes.count()
        }

        return Response(data)


class SearchResultListView(LoginRequiredMixin, ListView):# A class based view
    model = Post 
    template_name = 'blog/search_result.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts' # This makes it so that the list of objects is called posts.
                                    # as default, the name is ObjectList
    # paginate_by = 5

    def get_context_data(self, **kwargs): ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['title'] = 'Search results'
        return context


    def get_queryset(self):  ## filters posts list to the ones from user
        query = self.request.GET.get('q')
        if query == None:  ## If the query is empty, return all posts
            return Post.objects.all().order_by('-date_posted')
        else:
            return Post.objects.filter(Q(title__icontains=query)).order_by('-date_posted')


class PostDetailView(LoginRequiredMixin, DetailView):  # A class based view
    model = Post

    def get_context_data(self, **kwargs): ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['title'] = 'Post Detail'
        return context


# class PostCreateView(LoginRequiredMixin, CreateView):# A class based view


#     model = Post
#     fields = ['title', 'content']
#     success_url = '/'

#     def get_context_data(self, **kwargs):
#         context = super(PostCreateView, self).get_context_data(**kwargs)
#         context['post_images_form']  = PostImageForm
#         return context

#     def form_valid(self, form):
#         print(form.cleaned_data)# debugging
#         print(form)
#         form.instance.author = self.request.user ## Setting the author to the current logged in user
#         return super().form_valid(form)


# Reference: https://stackoverflow.com/questions/34006994/how-to-upload-multiple-images-to-a-blog-post-in-django
@login_required
def postCreate(request):
    PostImageFormSet = modelformset_factory(PostImage,
                                            form=PostImageForm, extra=3)

    if request.method == 'POST':

        p_form = PostForm(request.POST)
        pi_formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())
        ep_form = EatingPlaceFrom(request.POST)

        if p_form.is_valid() and pi_formset.is_valid() and ep_form.is_valid():
            # EatingPlace
            locator = Bing(api_key="AozreVUVlwxpZVbVcf6FErTup90eXr3DFSdlltU6m5JHLRuVh0Cp3A5PGh1OzVZC")
            name = ep_form.cleaned_data['name']
            address = ep_form.cleaned_data['address']
            location = locator.geocode(address)
            latitude = location.latitude
            longitude = location.longitude

            # Can use default to ignore some fields in get
            eating_place, _ = EatingPlace.objects.get_or_create(name=name, address=address, latitude=latitude, longitude=longitude)

            # Post
            post_form = p_form.save(commit=False)
            post_form.author = request.user
            post_form.place = eating_place
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
            print(p_form.errors, pi_formset.errors)
    else:
        p_form = PostForm()
        pi_formset = PostImageFormSet(queryset=PostImage.objects.none())
        ep_form = EatingPlaceFrom()

    context = {
        'p_form': p_form, 
        'pi_formset': pi_formset,
        'ep_form': ep_form,
        'title': 'New post'
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
        form.instance.author = self.request.user  ## Setting the author to the current logged in user
        return super().form_valid(form)


# Uses UserPassesTestMixin to check if the user requesting a post deletion is the author of that post
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
