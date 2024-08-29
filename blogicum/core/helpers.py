from typing import Optional, List, ContextManager

from django.db.models.functions import Now
from django.db.models import Q


def filter_queryset(manager: ContextManager, related_objects: Optional[
        List[str]] = None, limit: Optional[int] = None, post_id: Optional[
            int] = None, user_id: Optional[int] = None, **kwargs) -> List:
    """Helper function to retrieve objects with specific filters.
    Args:
        manager (ContextManager): The manager of the model to query.
        related_objects (Optional[List[str]]): List of related objects to
        prefetch.
        limit (Optional[int]): Maximum number of objects to retrieve.
        post_id (Optional[int]): id of concrete post.
        user_id (Optional[int]): id of current user.
        **kwargs: Additional filter parameters.
    Returns:
        List: A list of filtered objects.
    """
    queryset = manager.select_related('category', 'location', 'author')

    # if we have extra tables, load them in a query
    if related_objects:
        queryset = queryset.select_related(*related_objects)

    query = Q(is_published=True, pub_date__lte=Now(),
              category__is_published=True, **kwargs)

    # three scenarios:
    # 1. got post_id individually - return it but if its published.
    # 2. got pair post_id and user_id - show his post if it's exists and
    # it is really his post.
    # 3. show all published posts.
    if post_id or (post_id and user_id):
        filtered_queryset = queryset.filter(
            (Q(pk=post_id) & query) | Q(pk=post_id, author__id=user_id))
    else:
        filtered_queryset = queryset.filter(query)

        # if we have limit, cut them through sql and prevent from IndexError
        if limit and (len(filtered_queryset) >= limit):
            filtered_queryset = filtered_queryset[:limit]

    return filtered_queryset
