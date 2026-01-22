from django.urls import path

from .views import (
    PostCommentListAPIView,
    PostCommentListCreateAPIView,
    PostCommentRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("<int:post_id>/comments/", PostCommentListAPIView.as_view(), name="post-comment-list"),
    path("comments/", PostCommentListCreateAPIView.as_view(), name="post-comment-list-create"),
    path("comments/<int:comment_id>/", PostCommentRetrieveUpdateDestroyAPIView.as_view(), name="post-comment-rud"),
]
