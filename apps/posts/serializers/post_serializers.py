from typing import Any, Dict, Optional

from rest_framework import serializers

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory

# PostCategorySerializer 임포트는 사용하지 않음 (모듈 누락 회피)


class PostCreateSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=PostCategory.objects.filter(status=True),
        write_only=True,
    )

    class Meta:
        model = Post
        fields = ("title", "content", "category_id")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError({"detail": "자격 인증 데이터가 제공되지 않았습니다."})
        user = getattr(request, "user", None)
        if not user or user.is_anonymous:
            raise serializers.ValidationError({"detail": "자격 인증 데이터가 제공되지 않았습니다."})
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Post:
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError({"detail": "자격 인증 데이터가 제공되지 않았습니다."})
        user = getattr(request, "user", None)
        if not user or user.is_anonymous:
            raise serializers.ValidationError({"detail": "자격 인증 데이터가 제공되지 않았습니다."})
        author = user
        return Post.objects.create(author=author, **validated_data)


class AuthorSimpleSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id = serializers.IntegerField()
    nickname = serializers.CharField()
    profile_img_url = serializers.CharField(allow_null=True)


class PostListSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    author = AuthorSimpleSerializer(source="author", read_only=True)
    thumbnail_img_url = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "thumbnail_img_url",
            "content_preview",
            "comment_count",
            "view_count",
            "like_count",
            "created_at",
            "updated_at",
            "category_id",
        )

    def get_thumbnail_img_url(self, obj: Post) -> Optional[str]:
        first_image = getattr(obj, "images", None)
        if first_image is None:
            return None
        # images는 RelatedManager이므로 첫 번째 이미지를 가져옵니다
        first = obj.images.first()
        return first.img_url if first else None

    def get_content_preview(self, obj: Post) -> str:
        preview = (obj.content or "")[:100]
        return preview

    def get_comment_count(self, obj: Post) -> int:
        return obj.comments.count()

    def get_like_count(self, obj: Post) -> int:
        return obj.likes.filter(is_liked=True).count()


class DeleteResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    detail = serializers.CharField()


class PostDetailSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    author = AuthorSimpleSerializer(source="author", read_only=True)
    # PostCategorySerializer 모듈이 없을 수 있으므로
    # SerializerMethodField로 처리합니다
    category = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "category",
            "content",
            "view_count",
            "like_count",
            "created_at",
            "updated_at",
        )

    def get_like_count(self, obj: Post) -> int:
        return obj.likes.filter(is_liked=True).count()


class PostUpdateSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    id = serializers.IntegerField(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=PostCategory.objects.filter(status=True),
        write_only=False,
    )

    class Meta:
        model = Post
        fields = ("id", "title", "content", "category_id")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        request = self.context.get("request")
        if request is None:
            from rest_framework.exceptions import NotAuthenticated

            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        user = getattr(request, "user", None)
        if not user or user.is_anonymous:
            from rest_framework.exceptions import NotAuthenticated

            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")

        # 수정 시 작성자 소유권을 확인합니다
        if getattr(self, "instance", None) is not None:
            if getattr(self.instance, "author", None) != request.user:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied(detail="권한이 없습니다.")

        return attrs

    def update(self, instance: Post, validated_data: Dict[str, Any]) -> Post:
        # source 매핑으로 인해 validated_data에 'category'가 포함됩니다
        category = validated_data.pop("category", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if category is not None:
            instance.category = category
        instance.save()
        return instance
