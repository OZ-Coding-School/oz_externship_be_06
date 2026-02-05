from typing import Any, Dict

from rest_framework import serializers

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import (
    CommentNotFoundException,
    CommentUnauthorizedException,
)
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
        return TaggedUserSerializer(tags, many=True).data


class PostCommentCreateSerializer(serializers.Serializer[PostComment]):
    """
    댓글 생성 시리얼라이저 (요청 바디: content)
    """

    content = serializers.CharField(max_length=500, required=True)

    def validate_content(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("댓글 내용은 비어 있을 수 없습니다.")
        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 추가적인 전체 유효성 검증이 필요하면 여기에 작성
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> PostComment:
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if request is None or not user or not user.is_authenticated:
            raise CommentUnauthorizedException()

        context_post = self.context.get("post")
        if context_post is None or not isinstance(context_post, Post):
            raise CommentNotFoundException()

        return PostCommentService.create_comment(author=user, post=context_post, content=validated_data["content"])


class PostCommentUpdateSerializer(serializers.Serializer[PostComment]):
    """
    댓글 수정 시리얼라이저
    - content만 수정 가능
    - 작성자만 수정 가능
    """

    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(max_length=500, required=True)

    def validate_content(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("댓글 내용은 비어 있을 수 없습니다.")
        return value

    def update(self, instance: PostComment, validated_data: Dict[str, Any]) -> PostComment:
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        return PostCommentService.update_comment(user=user, comment=instance, content=validated_data["content"])


class PostCommentDeleteResponseSerializer(serializers.Serializer[Any]):
    """
    댓글 삭제 응답 스펙용 시리얼라이저
    """

    detail = serializers.CharField()
