from django.urls import path, include

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('auth/', include('users.urls')),

    # Posts url part
    path('posts/<int:post_pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:post_pk>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:post_pk>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),

    # Comments url part
    path('posts/<int:post_pk>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_pk>/edit_comment/<int:comment_pk>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_pk>/delete_comment/<int:comment_pk>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),

    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(),
         name='category_posts'),
    path('profile/edit/', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(),
         name='profile'),
]
