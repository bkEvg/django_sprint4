from typing import Optional, List, ContextManager

from django.db.models.functions import Now
from django.db.models import Q, QuerySet


def filter_queryset(manager: ContextManager, related_objects: Optional[
        List[str]] = None, limit: Optional[int] = None, post_id: Optional[
            int] = None, user_id: Optional[int] = None,
        valid_objects: Optional[bool] = True, **kwargs) -> QuerySet:
    """Helper function to retrieve objects with specific filters.
    Args:
        manager (ContextManager): The manager of the model to query.
        related_objects (Optional[List[str]]): List of related objects to
        prefetch.
        limit (Optional[int]): Maximum number of objects to retrieve.
        post_id (Optional[int]): id of concrete post.
        user_id (Optional[int]): id of current user.
        valid_objects
        **kwargs: Additional filter parameters.
    Returns:
        List: A list of filtered objects.
    """
    queryset = manager.select_related('category', 'location', 'author')

    # if we have extra tables, load them in a query
    if related_objects:
        queryset = queryset.select_related(*related_objects)

    query = Q(**kwargs)

    # flag indicates return published and valid posts
    if valid_objects:
        query &= Q(is_published=True, pub_date__lte=Now(),
                   category__is_published=True)

    # two scenarios:
    # 1. got post_id and user_id optionall - return it but if its published.
    # 2. show all published posts.
    if post_id:
        query &= Q(pk=post_id)
        if user_id:
            query &= Q(author_id=user_id)
        queryset = queryset.filter(query)
    else:
        queryset = queryset.filter(query)

        # If a limit is set, slice the queryset
        if limit:
            queryset = queryset[:limit]

    return queryset
