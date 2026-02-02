from rest_framework import serializers

from apps.posts.models.post import Post
from apps.users.models import User


class PostCreateSerializer(serializers.ModelSerializer[Post]):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Post
        fields = ["title", "content", "category_id"]


class PostAuthorSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "nickname", "profile_img_url"]


class PostListSerializer(serializers.ModelSerializer[Post]):
    author = PostAuthorSerializer(read_only=True)
    thumbnail_img_url = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()

    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)

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

    def get_thumbnail_img_url(self, obj: Post) -> str | None:
        first_image = obj.images.first()
        return first_image.img_url if first_image else None

    def get_content_preview(self, obj: Post) -> str:
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
