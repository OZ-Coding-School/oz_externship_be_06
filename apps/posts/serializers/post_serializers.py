from rest_framework import serializers
from apps.posts.models.post import Post

class PostCreateSerializer(serializers.ModelSerializer[Post]):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Post
        fields = ['title', 'content', 'category_id']