from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.posts.models import Post, PostCategory

if TYPE_CHECKING:
    from apps.users.models import User as UserType
else:
    UserType = Any

User = get_user_model()


class PostAuthorSerializer(serializers.ModelSerializer[UserType]):
    profile_img_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_img_url"]

    def get_profile_img_url(self, obj: UserType) -> Optional[str]:
        return getattr(obj, "profile_img_url", None)


class PostListSerializer(serializers.ModelSerializer[Post]):
    author = PostAuthorSerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    thumbnail_img_url = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(source="category.id", read_only=True)

    class Meta:
        model = Post
        fields = [
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
        ]

    def get_content_preview(self, obj: Post) -> str:
        if obj.content:
            return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        return ""

    def get_thumbnail_img_url(self, obj: Post) -> Optional[str]:
        return None


class PostDetailSerializer(serializers.ModelSerializer[Post]):
    author = PostAuthorSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author",
            "category",
            "content",
            "view_count",
            "like_count",
            "comment_count",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj: Post) -> Dict[str, Any]:
        return {"id": obj.category.id, "name": obj.category.name}


class PostCreateUpdateSerializer(serializers.ModelSerializer[Post]):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=PostCategory.objects.filter(status=True), source="category"
    )

    class Meta:
        model = Post
        fields = ["id", "title", "content", "category_id", "is_notice", "is_visible"]
        read_only_fields = ["id"]
