from django.urls import path

from apps.posts.views.category_views import CategoryListView
from apps.posts.views.post_like_views import PostLikeAPIView
from apps.posts.views.post_views import PostDetailView, PostListCreateView

app_name = "posts"

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:post_id>", PostDetailView.as_view(), name="post-detail"),
    path("categories", CategoryListView.as_view(), name="category-list"),
    path("<int:post_id>/like/", PostLikeAPIView.as_view(), name="post-like"),
]
