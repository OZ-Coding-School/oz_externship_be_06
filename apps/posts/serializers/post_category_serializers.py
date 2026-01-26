# apps/posts/serializers/post_category_serializers.py
from rest_framework import serializers
from ..models.post_category import PostCategory

class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ['id', 'name'] # 필요한 필드만 노출

