from django.urls import path

from apps.posts.views.category_views import CategoryListView
from apps.posts.views.comment.comment_create_views import PostCommentCreateAPIView
from apps.posts.views.comment.comment_delete_views import PostCommentDeleteAPIView
from apps.posts.views.comment.comment_detail_view import PostCommentDetailAPIView
from apps.posts.views.comment.comment_list_views import PostCommentListAPIView
from apps.posts.views.comment.comment_nickname_views import CommentRandomNicknameAPIView
from apps.posts.views.comment.comment_update_views import PostCommentUpdateAPIView
from apps.posts.views.post_like_views import PostLikeAPIView
from apps.posts.views.comment_nickname_views import CommentRandomNicknameAPIView
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
    # 댓글 목록
    path(
        "<int:post_id>/comments/",
        PostCommentListAPIView.as_view(),
        name="post-comment-list",
    ),
    # 댓글 랜덤 닉네임 생성
    path("comments/random-nickname/", CommentRandomNicknameAPIView.as_view(), name="comment-random-nickname"),
    # 댓글 생성
    path(
        "<int:post_id>/comments/create/",
        PostCommentCreateAPIView.as_view(),
        name="post-comment-create",
    ),
    # 댓글 상세 / 수정 / 삭제
    # 댓글 상세
    path(
        "<int:post_id>/comments/<int:comment_id>/",
        PostCommentDetailAPIView.as_view(),
        name="post-comment-detail",
    ),
    # 댓글 수정
    path(
        "<int:post_id>/comments/<int:comment_id>/update/",
        PostCommentUpdateAPIView.as_view(),
        name="post-comment-update",
    ),
    # 댓글 삭제
    path(
        "<int:post_id>/comments/<int:comment_id>/delete/",
        PostCommentDeleteAPIView.as_view(),
        name="post-comment-delete",
    ),
    path("categories/", CategoryListView.as_view(), name="post-category-list"),
    path("categories/", PostCategoryListAPIView.as_view(), name="post-category-list"),
    path("<int:post_id>/like/", PostLikeAPIView.as_view(), name="post-like"),
]
