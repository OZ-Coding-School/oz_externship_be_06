from rest_framework import serializers
from apps.posts.models.post_category import PostCategory

class CategoryListSerializer(serializers.ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ['id', 'name']