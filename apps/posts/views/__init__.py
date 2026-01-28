from .post_category_views import PostCategoryListAPIView
from .post_comment_views import (
    PostCommentListCreateAPIView,
    PostCommentRetrieveUpdateDestroyAPIView,
)

PostCommentListAPIView = PostCommentListCreateAPIView

__all__ = [
    "PostCommentListCreateAPIView",
    "PostCommentRetrieveUpdateDestroyAPIView",
    "PostCategoryListAPIView",
]
