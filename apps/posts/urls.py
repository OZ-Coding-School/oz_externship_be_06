from django.urls import path

from apps.posts.views.category_views import CategoryListView
from apps.posts.views.post_like_views import PostLikeAPIView
from apps.posts.views.post_views import PostDetailView, PostListCreateView

from .views import (
    PostCategoryListAPIView,
    PostCommentListCreateAPIView,
    PostCommentRetrieveUpdateDestroyAPIView,
)

app_name = "posts"

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:post_id>", PostDetailView.as_view(), name="post-detail"),
    path("categories", CategoryListView.as_view(), name="category-list"),
    # 댓글 목록 / 생성
    path(
        "<int:post_id>/comments/",
        PostCommentListCreateAPIView.as_view(),
        name="post-comment-list-create",
    ),
    # 댓글 상세 / 수정 / 삭제
    path(
        "<int:post_id>/comments/<int:comment_id>/",
        PostCommentRetrieveUpdateDestroyAPIView.as_view(),
        name="post-comment-rud",
    ),
    path("categories/", CategoryListView.as_view(), name="post-category-list"),
    path("categories/", PostCategoryListAPIView.as_view(), name="post-category-list"),
    path("<int:post_id>/like/", PostLikeAPIView.as_view(), name="post-like"),
]
