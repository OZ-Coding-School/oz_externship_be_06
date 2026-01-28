from __future__ import annotations

from typing import Any, Dict, List, cast

from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from .post_serializers import AuthorSimpleSerializer

AUTH_MSG = "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."


class TaggedUserSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """댓글 태그된 사용자 응답용 시리얼라이저."""
    id = serializers.IntegerField(source="tagged_user.id")
    nickname = serializers.CharField(source="tagged_user.nickname")


class PostCommentListSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """댓글 목록 조회 응답 시리얼라이저"""
    author = AuthorSimpleSerializer(read_only=True)
    tagged_users = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ("id", "author", "tagged_users", "content", "created_at", "updated_at")

    def get_tagged_users(self, obj: PostComment) -> List[Dict[str, Any]]:
        tags = obj.tags.select_related("tagged_user").all()
        return TaggedUserSerializer(tags, many=True).data  # type: ignore[return-value]


class PostCommentCreateSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """댓글 생성 시리얼라이저 (요청 바디: content)"""

    content = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = PostComment
        fields = ("content",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 입력 데이터(필드)만 검증
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> PostComment:
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if request is None or not user or not user.is_authenticated:
            # 테스트 기대 문구로 통일
            raise NotAuthenticated(detail=AUTH_MSG)

        context_post = self.context.get("post")
        if context_post is None or not isinstance(context_post, Post):
            raise NotFound(detail="해당 게시글을 찾을 수 없습니다.")

        # perform_create/save(author=..., post=...)로 들어오는 케이스 방어
        author = validated_data.pop("author", user)
        post = validated_data.pop("post", context_post)

        return PostComment.objects.create(author=author, post=post, **validated_data)


class PostCommentUpdateSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """댓글 수정 시리얼라이저
    - content만 수정 가능
    - 작성자만 수정 가능
    """

    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = PostComment
        fields = ("id", "content", "updated_at")
        read_only_fields = ("updated_at",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if request is None or not user or not user.is_authenticated:
            # 테스트 기대 문구로 통일
            raise NotAuthenticated(detail=AUTH_MSG)

        if self.instance is not None and cast(PostComment, self.instance).author != user:
            raise PermissionDenied(detail="권한이 없습니다.")

        return attrs

    def update(self, instance: PostComment, validated_data: Dict[str, Any]) -> PostComment:
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


class PostCommentDeleteResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """댓글 삭제 응답 스펙용 시리얼라이저"""
    detail = serializers.CharField()
