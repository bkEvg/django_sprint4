from django.urls import path, include
from django.conf.urls import handler403, handler404, handler500

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('auth/', include('users.urls')),

    # Posts url part
    path('posts/<int:pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),

    # Comments url part
    path('posts/<int:pk>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),

    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(),
         name='category_posts'),
    path('profile/<str:username>/', views.ProfileView.as_view(),
         name='profile'),
    path('profile/', views.ProfileView.as_view(),
         name='profile'),
    path('profile/edit', views.ProfileUpdateView.as_view(),
         name='edit_profile')
]

handler403 = views.CustomErrorView.as_view(error_code=403)
handler404 = views.CustomErrorView.as_view(error_code=404)
handler500 = views.CustomErrorView.as_view(error_code=500)
