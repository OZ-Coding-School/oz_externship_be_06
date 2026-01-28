from .post_comment_views import (
    PostCommentListCreateAPIView,
    PostCommentRetrieveUpdateDestroyAPIView,
)

# Backward/legacy import name: point to the same view implementation.
PostCommentListAPIView = PostCommentListCreateAPIView

from .post_category_views import PostCategoryListAPIView

__all__ = [
    "PostCommentListCreateAPIView",
    "PostCommentRetrieveUpdateDestroyAPIView",
    "PostCategoryListAPIView",
]
