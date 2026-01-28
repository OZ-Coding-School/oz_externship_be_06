from django.urls import path

from .views import PostCommentListCreateAPIView, PostCommentRetrieveUpdateDestroyAPIView
from apps.posts.views.post_category_views import PostCategoryListAPIView

from .views import PostCommentListCreateAPIView, PostCommentRetrieveUpdateDestroyAPIView

urlpatterns = [
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
from apps.posts.views.post_category_views import PostCategoryListAPIView

urlpatterns = [
    path("categories/", PostCategoryListAPIView.as_view(), name="post-category-list"),
]
