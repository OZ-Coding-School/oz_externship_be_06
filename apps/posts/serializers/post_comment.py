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

    def get_tagged_users(self, obj: PostComment) -> Any:
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

        post = self.context.get("post")
        if post is not None and not isinstance(post, Post):
            raise serializers.ValidationError({"detail": "게시글이 제공되지 않았습니다."})

        if post is None:
            view = self.context.get("view")
            post_id = None
            if view is not None:
                post_id = view.kwargs.get("post_id") or view.kwargs.get("pk")

            if post_id is None:
                raise serializers.ValidationError({"detail": "게시글이 제공되지 않았습니다."})

            try:
                post = Post.objects.get(pk=post_id)
            except Post.DoesNotExist as e:
                raise NotFound(detail="해당 게시글을 찾을 수 없습니다.") from e

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

        if getattr(self, "instance", None) is not None:
            if getattr(self.instance, "author", None) != user:
                raise PermissionDenied(detail="권한이 없습니다.")

        return attrs

    def update(self, instance: PostComment, validated_data: Dict[str, Any]) -> PostComment:
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


# 삭제 응답 스펙은 로컬에 유지
class PostCommentDeleteResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    detail = serializers.CharField()
