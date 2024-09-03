from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.db.models.functions import Now
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (ListView, DetailView, CreateView,
                                  TemplateView, UpdateView, DeleteView)
from django.urls import reverse
from typing import Any

from .mixins import SuccessURLMixin
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


class PostCreateView(LoginRequiredMixin, CreateView):
    """Post create view"""

    model = Post
    template_name = "blog/create.html"
    form_class = PostForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = get_object_or_404(
            User, username=self.request.user.username
        )
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Generate URL dymanically based on post ID"""
        return reverse("blog:profile", args=[self.request.user.username])


class PostUpdateView(PostCreateView, UpdateView):
    """Update post view"""

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author.username == self.request.user.username:
            return super().get(request, *args, **kwargs)
        else:
            return redirect("blog:post_detail", pk=self.object.pk)


class PostDetailView(DetailView):
    """Detail View for post"""

    model = Post
    template_name = "blog/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add extra data to context"""
        context = super().get_context_data(**kwargs)
        self.user = get_object_or_404(
            User, username=self.request.user.username)
        context["form"] = CommentsForm(self.request.POST or None)
        context["comments"] = self.get_object().comments.all()
        
        if self.user.username != self.get_object().author.username:
            post = get_object_or_404(
                Post,
                pk=self.kwargs["pk"],
                is_published=True,
                pub_date__lte=Now()
            )
            context["post"] = post
        else:
            # Если это автор поста, показываем его даже если он отложен
            context["post"] = self.get_object()
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Delete post view"""

    model = Post
    template_name = "blog/detail.html"

    def get_object(self) -> Model:
        """Delete post only if current user is author and post exists"""
        queryset = self.get_queryset()

        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        if self.request.user.username == obj.author.username:
            return obj
        else:
            redirect("blog:post_detail", self.kwargs["pk"])


class CategoryPostsView(ListView):
    """Posts of concrete category"""

    template_name = "blog/category.html"
    model = Post
    paginate_by = MAX_POSTS_COUNT

    def get_queryset(self) -> QuerySet[Any]:
        """Override get_queryset method to filter post by category"""
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return filter_queryset(self.category.posts)

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

    def get_queryset(self):
        """Get post by username kwarg"""
        self.user = get_object_or_404(
            User, username=self.kwargs["username"]
        )
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
    template_name = "registration/registration_form.html"
    fields = ("username", "email", "first_name", "last_name")

    def get_object(self):
        """Edit current user"""
        object = get_object_or_404(User, username=self.request.user.username)
        return object

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
            post - current post"""
        self.object = form.save(commit=False)
        self.object.author = get_object_or_404(
            User, username=self.request.user.username
        )
        self.object.post = get_object_or_404(Post, pk=self.kwargs["pk"])
        self.object.save()
        return super().form_valid(form)


class CommentUpdateView(CommentBaseView, UpdateView):
    """Update comment"""

    fields = ("text",)
    template_name = "blog/comment.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any
            ) -> HttpResponse:
        """Update post if current user is the author"""
        if self.get_object().author.username == self.request.user.username:
            return super().get(request, *args, **kwargs)
        else:
            return redirect("blog:post_detail", self.kwargs["pk"])


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
            return redirect("blog:post_detail", self.kwargs["pk"])


class CustomErrorView(TemplateView):
    """Custom view for any page error"""

    error_code = None

    def dispatch(self, request: HttpRequest, *args: Any,
                 **kwargs: Any) -> HttpResponse:
        """Display page error in a correct way"""
        self.error_code = kwargs.get("error_code")
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self) -> list[str]:
        """Dinamic template name generation from error_code kwarg"""
        if self.error_code == 403:
            return [f"pages/{self.error_code}csrf.html"]
        return [f"pages/{self.error_code}.html"]
