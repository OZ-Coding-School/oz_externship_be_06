from rest_framework import serializers

from ..models.post_category import PostCategory


class PostCategorySerializer(serializers.ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name"]
