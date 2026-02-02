from django.urls import path

from apps.posts.views.category_views import CategoryListView
from apps.posts.views.post_views import PostListCreateView, PostDetailView

app_name = "posts"

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:post_id>", PostDetailView.as_view(), name="post-detail"),
    path("categories", CategoryListView.as_view(), name="category-list"),
]
