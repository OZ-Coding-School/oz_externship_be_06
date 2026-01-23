from __future__ import annotations

from typing import Any, Dict, List, cast

from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment

from .post_serializers import AuthorSimpleSerializer

# 댓글 작성자 응답용 시리얼라이저.
# author은 post_serializers.py 모듈의 AuthorSimpleSerializer를 재사용한다.


class TaggedUserSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """댓글 태그된 사용자 응답용 시리얼라이저.

    - 댓글의 tags(중간 테이블/모델)를 통해 연결된 tagged_user 정보를
        프론트가 쓰기 쉬운 형태(id/nickname)로 평탄화해서 내려준다.
    """

    id = serializers.IntegerField(source="tagged_user.id")
    nickname = serializers.CharField(source="tagged_user.nickname")


class PostCommentListSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """댓글 목록 조회 응답 시리얼라이저

    - 목록 화면에서 필요한 필드만 포함한다.
    - tagged_users는 SerializerMethodField로 계산한다.
    """

    author = AuthorSimpleSerializer(read_only=True)
    tagged_users = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ("id", "author", "tagged_users", "content", "created_at", "updated_at")

    def get_tagged_users(self, obj: PostComment) -> List[Dict[str, Any]]:
        # 태그된 사용자 목록을 한 번에 로드하기 위해 select_related를 사용한다.
        tags = obj.tags.select_related("tagged_user").all()
        return TaggedUserSerializer(tags, many=True).data  # type: ignore[return-value]


class PostCommentCreateSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """댓글 생성 시리얼라이저 (요청 바디: content)"""

    content = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = PostComment
        fields = ("content",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 401: 명세 메시지
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if request is None or not user or user.is_anonymous:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")

        # 404: 명세 메시지 (게시글 없음)
        post = self.context.get("post")
        if post is None or not isinstance(post, Post):
            raise NotFound(detail="해당 게시글을 찾을 수 없습니다.")

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> PostComment:
        request = self.context["request"]
        post = self.context["post"]
        return PostComment.objects.create(
            author=request.user,
            post=post,
            **validated_data,
        )


class PostCommentUpdateSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """댓글 수정 시리얼라이저
    - content만 수정 가능하도록 제한한다.
    - 작성자만 수정할 수 있도록 validate에서 권한 체크를 수행한다.
    """

    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = PostComment
        fields = ("id", "content", "updated_at")
        read_only_fields = ("updated_at",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 수정은 인증이 필요하다.
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if request is None or not user or user.is_anonymous:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")

        # instance 타입이 Optional로 잡히는 경우가 있어 mypy 안정성을 위해 cast를 사용한다.
        if self.instance is not None and cast(PostComment, self.instance).author != user:
            raise PermissionDenied(detail="권한이 없습니다.")

        return attrs

    def update(self, instance: PostComment, validated_data: Dict[str, Any]) -> PostComment:
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


# 삭제 응답 스펙은 로컬에 유지
class PostCommentDeleteResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """댓글 삭제 응답 스펙용 시리얼라이저
    - 삭제 API 응답 바디가 필요한 경우를 대비해 detail 포맷을 고정한다.
    """

    detail = serializers.CharField()
