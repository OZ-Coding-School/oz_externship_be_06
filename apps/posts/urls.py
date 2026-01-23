from django.urls import path

from .views import (
    PostCommentListAPIView,
    PostCommentListCreateAPIView,
    PostCommentRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    # 댓글 목록 / 생성
    path(
        "<int:post_id>/comments/",
        PostCommentListCreateAPIView.as_view(),
        name="post-comment-list-create",
    ),
    # 댓글 수정 / 삭제 (mock 유지)
    path(
        "<int:post_id>/comments/<int:comment_id>/",
        PostCommentRetrieveUpdateDestroyAPIView.as_view(),
        name="post-comment-rud",
    ),
]
