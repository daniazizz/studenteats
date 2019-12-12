from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin ## Login required for posting,... User has to be the author for updating
from django.contrib.auth.models import User
from .models import Post, PostImage
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import PostImageForm, PostForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory


class PostListView(LoginRequiredMixin, ListView):# A class based view
    model = Post 
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts' # This makes it so that the list of objects is called posts.
                                    # as default, the name is ObjectList
    ordering = ['-date_posted'] # Minus symbol to reverse ordering
    paginate_by = 5

    def get_queryset(self): ## filters posts list to the ones from user
        user = self.request.user
        following = user.profile.following.all()
        return Post.objects.filter(Q(author=user) | Q(author__profile__in=following)).order_by('-date_posted')## Filtering out the posts to the posts of following or own posts

class ProfileListView(LoginRequiredMixin, ListView):# A class based view
    model = Post 
    template_name = 'blog/profile.html' 
    context_object_name = 'posts' # This makes it so that the list of objects is called posts.
                                    # as default, the name is ObjectList
    ordering = ['-date_posted'] # Minus symbol to reverse ordering
    paginate_by = 5
    

    def post(self, request, *args, **kwargs):
        s_user_username = request.POST.get("selected_user")
        s_user = get_object_or_404(User, username= s_user_username)
        c_user = request.user
        c_user.profile.following.add(s_user.profile)
        print(c_user, s_user)
        messages.success(request, f'You followed {s_user}') 
        return redirect('profile', s_user_username)

    def get_context_data(self, **kwargs): ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['selected_user'] = self.user
        context['following'] = self.user.profile.following.all()
        context['followers'] = self.user.profile.followers.all()
        return context

    def get_queryset(self): ## filters posts list to the ones from user
        self.user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=self.user).order_by('-date_posted')

class SearchResultListView(LoginRequiredMixin, ListView):# A class based view
    model = Post 
    template_name = 'blog/search_result.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts' # This makes it so that the list of objects is called posts.
                                    # as default, the name is ObjectList
    paginate_by = 5

    def get_queryset(self): ## filters posts list to the ones from user
        query = self.request.GET.get('q')
        if query==None: ## If the query is empty, return all posts
            return Post.objects.all().order_by('-date_posted')
        else: 
            return Post.objects.filter(Q(title__icontains=query)).order_by('-date_posted')

class PostDetailView(LoginRequiredMixin, DetailView):# A class based view
    model = Post 

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


#Reference: https://stackoverflow.com/questions/34006994/how-to-upload-multiple-images-to-a-blog-post-in-django
@login_required
def postCreate(request):
    PostImageFormSet = modelformset_factory(PostImage,
                                        form=PostImageForm, extra=3)

    if request.method == 'POST':

        p_form = PostForm(request.POST)
        pi_formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())

        if p_form.is_valid() and pi_formset.is_valid():
            post_form = p_form.save(commit=False)
            post_form.author = request.user
            post_form.save()
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

    return render(request, 'blog/post_create.html',
                  {'p_form': p_form, 'pi_formset': pi_formset})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): 
    model = Post 
    fields = ['title', 'content']
    template_name = 'blog/post_update.html'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs): ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user ## Setting the author to the current logged in user
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):# A class based view
    model = Post 
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
        
@login_required    
def map(request):
    return render(request, 'blog/map.html', {'title': 'Map'})
