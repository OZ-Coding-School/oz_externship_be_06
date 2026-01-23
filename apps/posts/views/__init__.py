from .post_comment_views import (
    PostCommentListCreateAPIView,
    PostCommentRetrieveUpdateDestroyAPIView,
)

# Backward/legacy import name: point to the same view implementation.
PostCommentListAPIView = PostCommentListCreateAPIView

__all__ = [
    "PostCommentListAPIView",
    "PostCommentListCreateAPIView",
    "PostCommentRetrieveUpdateDestroyAPIView",
]
