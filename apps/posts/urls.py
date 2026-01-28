from django.urls import path

from apps.posts.views.post_category_views import PostCategoryListAPIView
from apps.posts.views.post_comment_views import PostNicknameAutocompleteAPIView

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
    path("categories/", PostCategoryListAPIView.as_view(), name="post-category-list"),
    # 닉네임 자동완성/추천 (mock)
    path("search-nickname/", PostNicknameAutocompleteAPIView.as_view(), name="search-nickname"),
]
