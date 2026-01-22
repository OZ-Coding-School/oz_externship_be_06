from django.urls import path

from .views import (
    PostCommentListCreateAPIView,
    PostCommentRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("comments/", PostCommentListCreateAPIView.as_view(), name="post-comment-list-create"),
    path("comments/<int:comment_id>/", PostCommentRetrieveUpdateDestroyAPIView.as_view(), name="post-comment-rud"),
]
