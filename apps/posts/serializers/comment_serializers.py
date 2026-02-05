# Renamed from post_comment.py to comment_serializers.py
from typing import Any, Dict

from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated, NotFound

from apps.posts.constants.post_const import PostErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from apps.posts.models.post_comment_tags import PostCommentTag
from apps.posts.serializers.post_serializers import PostAuthorSerializer
from apps.posts.services.comment_services import PostCommentService


class TaggedUserSerializer(serializers.ModelSerializer[PostCommentTag]):
    """
    댓글에 태그된 사용자 정보를 반환하는 시리얼라이저입니다.
    """

    id = serializers.IntegerField(source="tagged_user.id")
    nickname = serializers.CharField(source="tagged_user.nickname")

    class Meta:
        model = PostCommentTag
        fields = ("id", "nickname")


class PostCommentListSerializer(serializers.ModelSerializer[PostComment]):
    """
    댓글 목록을 조회할 때 사용하는 시리얼라이저입니다.
    """

    author = PostAuthorSerializer(read_only=True)
    tagged_users = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ("id", "author", "tagged_users", "content", "created_at", "updated_at")

    def get_tagged_users(self, obj: PostComment) -> Any:
        tags = obj.tags.all()
# ...existing code...
