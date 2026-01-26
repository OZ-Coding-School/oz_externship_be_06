from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.posts.models import Post

User = get_user_model()

class PostAuthorSerializer(serializers.ModelSerializer):
    profile_img_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_img_url']

    def get_profile_img_url(self, obj):
        return obj.profile_img_url if hasattr(obj, 'profile_img_url') else None

class PostListSerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer(read_only=True)
    author = PostAuthorSerializer(read_only=True)  # 중첩된 작성자 정보
    content_preview = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    thumbnail_img_url = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(source='category.id', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'title',
            'thumbnail_img_url',
            'content_preview',
            'comment_count',
            'view_count',
            'like_count',
            'created_at',
            'updated_at',
            'category_id',
        ]

    def get_content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        return ""

    def get_thumbnail_img_url(self, obj):
        return None

class PostDetailSerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    # ViewSet의 annotate로 생성된 필드들을 반드시 시리얼라이저에 정의해야 합니다.
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'author', 'category', 'content',
            'view_count', 'like_count', 'comment_count', # fields에 포함
            'created_at', 'updated_at',
        ]

    def get_category(self, obj):
        return {"id": obj.category.id, "name": obj.category.name}