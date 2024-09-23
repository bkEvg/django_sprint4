from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import Http404
from typing import Any

from blog.models import Post, Comment


class SuccessURLMixin:
    """Mixin to generate url dynamically based on post's ID"""

    def get_success_url(self) -> str:
        """Generate URL dymanically based on post ID"""
        return reverse("blog:post_detail", args=[self.kwargs["post_pk"]])


class PostViewMixin:
    """Base class for Post model"""

    model = Post
    pk_url_kwarg = "post_pk"

    def is_author(self, obj) -> bool:
        """Return 'True' if current user is author of the obj, 'False'
        otherwise
        """
        return self.request.user == obj.author

    def get_success_url(self) -> str:
        """Default url to be reversed"""
        return reverse("blog:profile", args=[self.request.user.username])


class CommentViewMixin(LoginRequiredMixin, SuccessURLMixin):
    """Base set of views for comment handling"""

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_pk"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add post context data to response"""
        context = super().get_context_data(**kwargs)
        context["post"] = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        return context

    def get_object(self) -> Model:
        """
        Method allow delete/update comment only if current user is
        the author
        """
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["comment_pk"])
        if obj.author.username == self.request.user.username:
            return obj
        raise Http404("Вам нельзя редактировать не свои комментарии")
