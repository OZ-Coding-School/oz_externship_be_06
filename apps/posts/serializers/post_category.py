from rest_framework import serializers

from apps.posts.models.post_category import PostCategory


class PostCategorySerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = PostCategory
        fields = ("id", "name")
