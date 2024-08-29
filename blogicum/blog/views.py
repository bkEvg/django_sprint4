from django.shortcuts import render, get_object_or_404

from .models import Post, Category
from core.helpers import filter_queryset
from core.constants import MAX_POSTS_COUNT


def index(request):
    """Main page containing all posts"""
    template_name = 'blog/index.html'
    posts = filter_queryset(Post.objects, limit=MAX_POSTS_COUNT)
    context = {
        'post_list': posts
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    """Detail page of post"""
    template_name = 'blog/detail.html'
    post = get_object_or_404(filter_queryset(
        Post.objects, user_id=request.user.id), pk=post_id
    )

    context = {
        'post': post
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    """Posts of concrete category"""
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)

    # Filtered posts must be:
    #   * published, category is puslished and pub_date in the past
    posts = filter_queryset(category.posts)

    context = {
        'post_list': posts,
        'category': category,
    }
    return render(request, template_name, context)
