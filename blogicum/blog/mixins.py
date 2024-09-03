from django.urls import reverse


class SuccessURLMixin:
    """Mixin to generate url dynamically based on post's ID"""

    def get_success_url(self) -> str:
        """Generate URL dymanically based on post ID"""
        return reverse("blog:post_detail", args=[self.kwargs["pk"]])
