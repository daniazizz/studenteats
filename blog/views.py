from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin ## Login required for posting,... User has to be the author for updating
from django.contrib.auth.models import User
from .models import Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import PostImageForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

class PostListView(LoginRequiredMixin, ListView):# A class based view
    model = Post 
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts' # This makes it so that the list of objects is called posts.
                                    # as default, the name is ObjectList
    ordering = ['-date_posted'] # Minus symbol to reverse ordering
    paginate_by = 5

class ProfileListView(LoginRequiredMixin, ListView):# A class based view
    model = Post 
    template_name = 'blog/profile.html' 
    context_object_name = 'posts' # This makes it so that the list of objects is called posts.
                                    # as default, the name is ObjectList
    ordering = ['-date_posted'] # Minus symbol to reverse ordering
    paginate_by = 5

    def get_context_data(self, **kwargs): ## Adding extra data in the context to pass on the template
        context = super().get_context_data(**kwargs)
        context['selected_user'] = self.user
        return context

    def get_queryset(self): ## filters posts list to the ones from user
        self.user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=self.user).order_by('-date_posted')

class SearchResultListView(LoginRequiredMixin, ListView):# A class based view
    model = Post 
    template_name = 'blog/search_result.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts' # This makes it so that the list of objects is called posts.
                                    # as default, the name is ObjectList
    ordering = ['-date_posted'] # Minus symbol to reverse ordering
    paginate_by = 5

    def get_queryset(self): ## filters posts list to the ones from user
        query = self.request.GET.get('q')
        return Post.objects.filter(Q(title__icontains=query)).order_by('-date_posted')

class PostDetailView(LoginRequiredMixin, DetailView):# A class based view
    model = Post 

class PostCreateView(LoginRequiredMixin, CreateView):# A class based view
    model = Post 
    fields = ['title', 'content']
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)
        context['post_images_form']  = PostImageForm
        return context

    def form_valid(self, form):
        print(form.cleaned_data)# debugging
        print(form)
        form.instance.author = self.request.user ## Setting the author to the current logged in user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):# A class based view
    model = Post 
    fields = ['title', 'content']

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

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
