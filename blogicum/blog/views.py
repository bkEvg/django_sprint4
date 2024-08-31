from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView
from django.urls import reverse
from typing import Any

from .models import Post, Category, Comment
from .forms import PostForm, CommentsForm
from core.helpers import filter_queryset
from core.constants import MAX_POSTS_COUNT


User = get_user_model()


class PostListView(ListView):
    """Main List View for page containing all posts"""

    template_name = 'blog/index.html'
    queryset = filter_queryset(Post.objects, limit=MAX_POSTS_COUNT)
    paginate_by = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    """Post create view"""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = get_object_or_404(
            User, username=self.request.user.username
        )
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Get url of created post and open page with it"""
        return reverse('blog:post_detail', args=[self.object.id])


class PostUpdateView(PostCreateView, UpdateView):
    """Update post view"""

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author.username == self.request.user.username:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('blog:post_detail', pk=self.object.pk)


class PostDetailView(DetailView):
    """Detail View for post"""

    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add extra data to context"""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm(self.request.POST or None)
        context["post"] = get_object_or_404(filter_queryset(
            Post.objects, user_id=self.request.user.id, pk=self.kwargs['pk']
        ))
        return context


class CategoryPostsView(ListView):
    """Posts of concrete category"""

    template_name = 'blog/category.html'
    model = Post
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        """Override get_queryset method to filter post by category"""
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return filter_queryset(self.category.posts)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add custom filter to a paginator"""
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProfileView(ListView):
    """View for displayin Profile page"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        self.user = get_object_or_404(
            User, username=self.kwargs['username']
        )
        posts = self.model.objects.filter(author=self.user)
        return posts

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["profile"] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update profile view"""

    model = User
    template_name = 'registration/registration_form.html'
    fields = ('username', 'email', 'first_name', 'last_name')

    def get_object(self):
        """Edit current user"""
        object = get_object_or_404(User, username=self.request.user.username)
        return object

    def get_success_url(self) -> str:
        return reverse('blog:profile', args=[self.request.user.username])


class CommentCreateView(CreateView):
    """Crete comment view"""

    model = Comment
    form_class = CommentsForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = get_object_or_404(
            User, username=self.request.user.username
        )
        self.object.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Get url of created post and open page with it"""
        return reverse('blog:post_detail', args=[self.object.post.id])


class CustomErrorView(TemplateView):
    """Custom view for any page error"""

    error_code = None

    def dispatch(self, request: HttpRequest, *args: Any,
                 **kwargs: Any) -> HttpResponse:
        """Display page error in a correct way"""
        self.error_code = kwargs.get('error_code')
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self) -> list[str]:
        """Dinamic template name generation from error_code kwarg"""
        if self.error_code == 403:
            return [f'pages/{self.error_code}csrf.html']
        return [f'pages/{self.error_code}.html']
