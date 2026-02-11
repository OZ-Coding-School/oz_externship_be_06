from django.urls import path

from apps.posts.views.category_views import CategoryListView
from apps.posts.views.comment.comment_detail_view import PostCommentDetailAPIView
from apps.posts.views.comment.comment_list_views import PostCommentListAPIView
from apps.posts.views.post_like_views import PostLikeAPIView
from apps.posts.views.post_views import PostDetailView, PostListCreateView
from apps.posts.views.presigned_url_view import PostPresignedUrlAPIView

app_name = "posts"

urlpatterns = [
    # 게시글
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:post_id>", PostDetailView.as_view(), name="post-detail"),
    path("<int:post_id>/like", PostLikeAPIView.as_view(), name="post-like"),
    # 게시글 댓글
    path("<int:post_id>/comments", PostCommentListAPIView.as_view(), name="post-comment-list-create"),
    path("<int:post_id>/comments/<int:comment_id>", PostCommentDetailAPIView.as_view(), name="post-comment-detail"),
    # 카테고리
    path("categories", CategoryListView.as_view(), name="category-list"),
    # 유틸리티
    path("presigned-url", PostPresignedUrlAPIView.as_view(), name="post-presigned-url"),
]
