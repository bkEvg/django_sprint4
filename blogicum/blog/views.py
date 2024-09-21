from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, Http404
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, DeleteView)
from django.urls import reverse
from django.utils import timezone
from typing import Any

from .mixins import SuccessURLMixin
from .models import Post, Category, Comment
from .forms import PostForm, CommentsForm
from core.helpers import filter_queryset
from core.constants import MAX_POSTS_COUNT


User = get_user_model()


class BasePost:
    """Base class for Post model"""

    model = Post

    def is_author(self, obj) -> bool:
        """Return 'True' if current user is author of the obj, 'False'
        otherwise
        """
        return self.request.user == obj.author


class PostListView(ListView):
    """Main List View for page containing all posts"""

    template_name = "blog/index.html"
    queryset = filter_queryset(Post.objects)
    paginate_by = MAX_POSTS_COUNT


class PostCreateView(LoginRequiredMixin, CreateView):
    """Post create view"""

    model = Post
    template_name = "blog/create.html"
    form_class = PostForm

    def form_valid(self, form) -> HttpResponse:
        """Redefine method to add author to the post"""
        self.object = form.save(commit=False)
        self.object.author = get_object_or_404(
            User, username=self.request.user.username
        )
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Generate URL dymanically based on post ID"""
        return reverse("blog:profile", args=[self.request.user.username])


class PostUpdateView(BasePost, UpdateView):
    """Update post view"""

    template_name = "blog/create.html"
    form_class = PostForm

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Post can be updated only by its author"""
        object = self.get_object()
        if self.is_author(object):
            return super().get(request, *args, **kwargs)
        else:
            raise Http404("Вам нельзя редактировать не свои публикации")

    def post(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        object = self.get_object()
        if self.is_author(object):
            return super().post(request, *args, **kwargs)
        return redirect("blog:post_detail", pk=object.pk)

    def get_success_url(self) -> str:
        """Generate URL dymanically based on post ID"""
        return reverse("blog:post_detail", args=[self.kwargs['pk']])


class PostDetailView(BasePost, DetailView):
    """Detail View for post"""

    template_name = "blog/detail.html"

    def get_post(self):
        """Retrieve the post considering the current user"""
        post = self.get_object()
        now = timezone.now()
        if self.is_author(post) or (post.is_published and post.pub_date < now
                                    and post.category.is_published):
            return post
        raise Http404("Пост не найден, или недоступен")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add extra data to context"""
        context = super().get_context_data(**kwargs)
        context["form"] = CommentsForm(self.request.POST or None)
        context["comments"] = self.get_object().comments.all()
        context["post"] = self.get_post()
        return context


class PostDeleteView(BasePost, LoginRequiredMixin, DeleteView):
    """Delete post view"""

    template_name = "blog/create.html"

    def get_object(self) -> Model:
        """Delete post only if current user is author and post exists"""
        queryset = self.get_queryset()

        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        if self.is_author(obj) or self.request.user.is_staff:
            return obj
        else:
            raise Http404("Вам нельзя удалять не свои публикации")

    def get_context_data(self, **kwargs):
        """Add the object to the context to access it in the template"""
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self) -> str:
        """Success url to the profile when profile updated"""
        return reverse("blog:profile", args=[self.request.user.username])


class CategoryPostsView(ListView):
    """Posts of concrete category"""

    template_name = "blog/category.html"
    model = Post
    paginate_by = MAX_POSTS_COUNT

    def get_queryset(self) -> QuerySet[Any]:
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

    def get_queryset(self) -> QuerySet:
        """Get post by username kwarg"""
        username = self.kwargs.get("username", "")
        if not username:
            username = self.request.user.username
        self.user = get_object_or_404(User, username=username)
        valid_objects = self.request.user.username != self.user.username
        posts = filter_queryset(
            self.model.objects,
            author__id=self.user.id,
            valid_objects=valid_objects)
        return posts

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add profile context data to response"""
        context = super().get_context_data(**kwargs)
        context["profile"] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update profile view"""

    model = User
    template_name = "blog/user.html"
    fields = ("username", "email", "first_name", "last_name")

    def get_object(self):
        """Edit current user"""
        # username = self.request.user.username
        # user = get_object_or_404(User, username=username)
        return self.request.user

    def get_success_url(self) -> str:
        """Success url to the profile when profile updated"""
        return reverse("blog:profile", args=[self.request.user.username])


class CommentBaseView(LoginRequiredMixin, SuccessURLMixin):
    """Base set of views for comment handling"""

    model = Comment
    template_name = "blog/detail.html"

    def get_object(self) -> Model:
        """Get object by comment_id kwarg"""
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["comment_id"])
        return obj

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add post context data to response"""
        context = super().get_context_data(**kwargs)
        context["post"] = get_object_or_404(Post, pk=self.kwargs["pk"])
        return context


class CommentCreateView(LoginRequiredMixin, SuccessURLMixin, CreateView):
    """Create comment view"""

    model = Comment
    form_class = CommentsForm
    template_name = "blog/detail.html"

    def form_valid(self, form):
        """When comment form has perform post request
        we add extra data to it as:
            author - current user
            post - current post
        """
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        self.object = form.save(commit=False)
        self.object.author = get_object_or_404(
            User, username=self.request.user.username
        )
        self.object.post = post
        self.object.save()
        return super().form_valid(form)


class CommentUpdateView(CommentBaseView, UpdateView):
    """Update comment"""

    fields = ("text",)
    template_name = "blog/comment.html"

    def get_object(self) -> Model:
        """Method allow delete comment only if current user is the author"""
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["comment_id"])
        if obj.author.username == self.request.user.username:
            return obj
        else:
            raise Http404("Вам нельзя редактировать не свои комментарии")


class CommentDeleteView(CommentBaseView, DeleteView):
    """Delete comment"""

    template_name = "blog/comment.html"

    def get_object(self) -> Model:
        """Method allow delete comment only if current user is the author"""
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["comment_id"])
        if obj.author.username == self.request.user.username:
            return obj
        else:
            raise Http404("Вам нельзя удалять не свои комментарии")
