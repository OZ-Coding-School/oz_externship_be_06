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
from apps.posts.services.comment.comment_create_services import create_comment
from apps.posts.services.comment.comment_delete_services import delete_comment
from apps.posts.services.comment.comment_update_services import update_comment


class TaggedUserSerializer(serializers.ModelSerializer[PostCommentTag]):
    """
    댓글에 태그된 사용자 정보를 반환하는 시리얼라이저입니다.
    """

    id = serializers.IntegerField(source="tagged_user.id")  # 태그된 사용자의 PK
    nickname = serializers.CharField(source="tagged_user.nickname")  # 태그된 사용자의 닉네임

    class Meta:
        model = PostCommentTag
        fields = ("id", "nickname")


class PostCommentListSerializer(serializers.ModelSerializer[PostComment]):
    """
    댓글 목록을 조회할 때 사용하는 시리얼라이저입니다.
    """

    author = PostAuthorSerializer(read_only=True)  # 댓글 작성자 정보
    tagged_users = serializers.SerializerMethodField()  # 태그된 사용자 목록

    class Meta:
        model = PostComment
        fields = ("id", "author", "tagged_users", "content", "created_at", "updated_at")

    def get_tagged_users(self, obj: PostComment) -> Any:
        # 댓글에 태그된 사용자 목록을 반환합니다.
        tags = obj.tags.all()
        return TaggedUserSerializer(tags, many=True).data


class PostCommentCreateSerializer(serializers.Serializer[PostComment]):
    """
    댓글 생성 시리얼라이저 (요청 바디: content)
    """

    content = serializers.CharField(max_length=300, required=True)  # 댓글 내용

    def validate_content(self, value: str) -> str:
        # 댓글 내용이 비어있는지 검증합니다.
        if not value.strip():
            raise serializers.ValidationError("댓글 내용은 비어 있을 수 없습니다.")
        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 전체 유효성 검증이 필요한 경우 사용합니다.
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> PostComment:
        # 댓글 객체를 생성합니다. request의 user와 post를 context에서 받아 사용합니다.
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None

        # user가 None이거나 인증되지 않은 경우 예외 발생
        if user is None or not user.is_authenticated:
            raise CommentUnauthorizedException()

        context_post = self.context.get("post")
        if context_post is None or not isinstance(context_post, Post):
            raise CommentNotFoundException()

        return create_comment(author=user, post=context_post, content=validated_data["content"])


class PostCommentUpdateSerializer(serializers.Serializer[PostComment]):
    """
    댓글 수정 시리얼라이저
    - content만 수정 가능
    - 작성자만 수정 가능
    """

    id = serializers.IntegerField(read_only=True)  # 댓글 PK
    content = serializers.CharField(max_length=300, required=True)  # 수정할 댓글 내용

    def validate_content(self, value: str) -> str:
        # 댓글 내용이 비어있는지 검증합니다.
        if not value.strip():
            raise serializers.ValidationError("댓글 내용은 비어 있을 수 없습니다.")
        return value

    def update(self, instance: PostComment, validated_data: Dict[str, Any]) -> PostComment:
        # 댓글 객체를 수정합니다. request의 user를 context에서 받아 사용합니다.
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        return update_comment(user=user, comment=instance, content=validated_data["content"])


class PostCommentDeleteResponseSerializer(serializers.Serializer[Any]):
    """
    댓글 삭제 응답 스펙용 시리얼라이저
    """

    detail = serializers.CharField()  # 삭제 결과 메시지
