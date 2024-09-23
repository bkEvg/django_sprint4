from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.http import Http404
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, DeleteView)
from django.urls import reverse
from django.utils import timezone
from typing import Any

from .mixins import SuccessURLMixin, PostViewMixin, CommentViewMixin
from .models import Post, Category, Comment
from .forms import PostForm, CommentsForm
from core.helpers import filter_queryset
from core.constants import MAX_POSTS_COUNT


User = get_user_model()


class PostListView(ListView):
    """Main List View for page containing all posts"""

    template_name = "blog/index.html"
    queryset = filter_queryset(Post.objects)
    paginate_by = MAX_POSTS_COUNT


class PostCreateView(PostViewMixin, LoginRequiredMixin, CreateView):
    """Post create view"""

    template_name = "blog/create.html"
    form_class = PostForm

    def form_valid(self, form) -> HttpResponse:
        """Redefine method to add author to the post"""
        object = form.save(commit=False)
        object.author = self.request.user
        object.save()
        return super().form_valid(form)


class PostUpdateView(PostViewMixin, UpdateView):
    """Update post view"""

    template_name = "blog/create.html"
    form_class = PostForm

    def form_valid(self, form) -> HttpResponse:
        """
        Redifine form valid method
        validate form only if current user is the author
        """
        post = self.get_object()
        if self.is_author(post):
            return super().form_valid(form)
        return redirect("blog:post_detail", post_pk=post.pk)

    def get_success_url(self) -> str:
        """Generate URL dymanically based on post ID"""
        return reverse("blog:post_detail", args=[self.kwargs['post_pk']])


class PostDetailView(PostViewMixin, DetailView):
    """Detail View for post"""

    template_name = "blog/detail.html"

    def get_object(self, queryset: QuerySet[Any] = None) -> Model:
        """Get post if its parameters is valid"""
        post = super().get_object()
        now = timezone.now()
        if self.is_author(post) or (post.is_published and post.pub_date < now
                                    and post.category.is_published):
            return post
        raise Http404("Пост не найден, или недоступен")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add extra data to context"""
        context = super().get_context_data(**kwargs)
        context["form"] = CommentsForm(self.request.POST or None)
        context["comments"] = self.object.comments.all()
        context["post"] = self.object
        return context


class PostDeleteView(PostViewMixin, LoginRequiredMixin, DeleteView):
    """Delete post view"""

    template_name = "blog/create.html"

    def get_object(self) -> Model:
        """Delete post only if current user is author and post exists"""
        object = super().get_object()
        if self.is_author(object) or self.request.user.is_staff:
            return object
        raise Http404("Вам нельзя удалять не свои публикации")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add form to the context to access it in the template"""
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class CategoryPostsView(ListView):
    """Posts of concrete category"""

    template_name = "blog/category.html"
    model = Post
    paginate_by = MAX_POSTS_COUNT
    category = None

    def get_queryset(self) -> QuerySet:
        """Override get_queryset method to filter post by category"""
        queryset = Post.objects.all()
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return filter_queryset(queryset, category=self.category)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add custom filter to a paginator"""
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProfileView(ListView):
    """View for displayin Profile page
    Profile page simply is a TemplateView but we need to display
    related to it posts. That is why we use ListView and custom
    get_queryset() method
    """

    model = Post
    template_name = "blog/profile.html"
    paginate_by = MAX_POSTS_COUNT
    profile = None

    def get_queryset(self) -> QuerySet:
        """Get post by username kwarg"""
        self.profile = get_object_or_404(
            User, username=self.kwargs["username"])
        valid_objects = self.request.user != self.profile
        posts = filter_queryset(
            self.model.objects,
            author__id=self.profile.id,
            valid_objects=valid_objects)
        return posts

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add profile context data to response"""
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update profile view"""

    model = User
    template_name = "blog/user.html"
    fields = ("username", "email", "first_name", "last_name")

    def get_object(self) -> Model:
        """Edit current user"""
        return self.request.user

    def get_success_url(self) -> str:
        """Success url to the profile when profile updated"""
        return reverse("blog:profile", args=[self.request.user.username])


class CommentCreateView(LoginRequiredMixin, SuccessURLMixin, CreateView):
    """Create comment view"""

    model = Comment
    form_class = CommentsForm
    template_name = "blog/detail.html"

    def form_valid(self, form) -> HttpResponse:
        """When comment form has perform post request
        we add extra data to it as:
            author - current user
            post - current post
        """
        post = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        object = form.save(commit=False)
        object.author, object.post = self.request.user, post
        object.save()
        return super().form_valid(form)


class CommentUpdateView(CommentViewMixin, UpdateView):
    """Update comment only by its owner"""

    fields = ("text",)


class CommentDeleteView(CommentViewMixin, DeleteView):
    """Delete comment"""
