from __future__ import annotations

from typing import Any, Dict

from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment

from .post_serializers import AuthorSimpleSerializer


class TaggedUserSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id = serializers.IntegerField(source="tagged_user.id")
    nickname = serializers.CharField(source="tagged_user.nickname")


class PostCommentListSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    author = AuthorSimpleSerializer(read_only=True)
    tagged_users = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ("id", "author", "tagged_users", "content", "created_at", "updated_at")

    def get_tagged_users(self, obj: PostComment) -> list[dict[str, Any]]:
        tags = obj.tags.select_related("tagged_user").all()
        return TaggedUserSerializer(tags, many=True).data


class PostCommentDetailSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """댓글 상세 조회용 시리얼라이저"""
    author = AuthorSimpleSerializer(read_only=True)
    tagged_users = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ("id", "author", "tagged_users", "content", "created_at", "updated_at")

    def get_tagged_users(self, obj: PostComment) -> list[dict[str, Any]]:
        tags = obj.tags.select_related("tagged_user").all()
        return TaggedUserSerializer(tags, many=True).data


class PostCommentCreateSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    content = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = PostComment
        fields = ("content",)

    def create(self, validated_data: Dict[str, Any]) -> PostComment:
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if request is None or not user or user.is_anonymous:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")

        # View에서 post를 context로 전달해야 함
        post = self.context.get("post")
        if post is None or not isinstance(post, Post):
            raise serializers.ValidationError({"detail": "게시글 정보가 필요합니다."})

        return PostComment.objects.create(author=user, post=post, **validated_data)


class PostCommentUpdateSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = PostComment
        fields = ("id", "content", "updated_at")
        read_only_fields = ("updated_at",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if request is None or not user or user.is_anonymous:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")

        if self.instance is not None and self.instance.author != user:
            raise PermissionDenied(detail="권한이 없습니다.")

        return attrs

    def update(self, instance: PostComment, validated_data: Dict[str, Any]) -> PostComment:
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


# 삭제 응답 스펙은 로컬에 유지
class PostCommentDeleteResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    detail = serializers.CharField()
