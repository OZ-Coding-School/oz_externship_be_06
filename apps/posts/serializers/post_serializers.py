from typing import Any, Dict, Optional

from rest_framework import serializers

from apps.posts.models import PostComment
from apps.posts.models.post import Post
from apps.posts.models.post_images import PostImage
from apps.qna.utils.content_parser import ContentParser
from apps.users.models import User


class PostCreateSerializer(serializers.ModelSerializer[Post]):
    """
    게시글 생성을 위한 시리얼라이저입니다.
    """

    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Post
        fields = ["title", "content", "category_id"]


class PostAuthorSerializer(serializers.ModelSerializer[User]):
    """
    게시글 작성자 정보를 간단히 노출하기 위한 시리얼라이저입니다.
    """

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_img_url"]


class PostListSerializer(serializers.ModelSerializer[Post]):
    """
    게시글 목록 조회 시 사용되는 최적화된 시리얼라이저입니다.
    """

    author = PostAuthorSerializer(read_only=True)
    thumbnail_img_url = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()

    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_like = serializers.BooleanField(read_only=True)

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
            "is_like",
            "created_at",
            "updated_at",
            "category_id",
        ]

    def get_thumbnail_img_url(self, obj: Post) -> Optional[str]:
        """
        N+1 문제를 방지하기 위해 Prefetch된 데이터를 메모리 상에서 조회합니다.
        """
        images = list(obj.images.all())
        if not images:
            return None
        return images[0].img_url

    def get_content_preview(self, obj: Post) -> str:
        """
        게시글 본문의 앞부분 50자만 추출하여 반환합니다.
        이미지 태그(마크다운/HTML)를 제거한 텍스트를 반환합니다.
        """
        return ContentParser.extract_content_preview(obj.content, 50) or ""


class PostFilterSerializer(serializers.Serializer[dict[str, Any]]):
    """
    게시글 목록 조회를 위한 쿼리 파라미터 검증 시리얼라이저입니다.
    """

    category_id = serializers.IntegerField(required=False)
    search = serializers.CharField(required=False, max_length=100)
    search_filter = serializers.ChoiceField(
        choices=["author", "title", "content", "title_or_content"], default="title_or_content", required=False
    )
    sort = serializers.ChoiceField(
        choices=["latest", "oldest", "most_views", "most_likes", "most_comments"], default="latest", required=False
    )


class PostCommentTagSerializer(serializers.Serializer[Dict[str, Any]]):
    """
    댓글 내 유저 태그 정보를 위한 시리얼라이저입니다.
    """

    nickname = serializers.CharField(source="tagged_user.nickname")


class PostCommentDetailSerializer(serializers.ModelSerializer[PostComment]):
    """
    게시글 상세 조회용 댓글 시리얼라이저입니다.
    """

    author_nickname = serializers.CharField(source="author.nickname", read_only=True)
    author_profile_img = serializers.URLField(source="author.profile_img_url", read_only=True)
    tagged_users = PostCommentTagSerializer(many=True, source="tags", read_only=True)

    class Meta:
        model = PostComment
        fields = [
            "id",
            "author_nickname",
            "author_profile_img",
            "content",
            "created_at",
            "tagged_users",
        ]


class PostDetailSerializer(serializers.ModelSerializer[Post]):
    """
    게시글 상세 정보를 처리하는 시리얼라이저입니다.
    """

    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    like_count = serializers.IntegerField()
    is_like = serializers.BooleanField(read_only=True)

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
            "is_like",
            "created_at",
            "updated_at",
        ]

    def get_author(self, obj: Post) -> Dict[str, Any]:
        """
        작성자 정보 추출
        """
        return {
            "id": obj.author.id,
            "nickname": obj.author.nickname,
            "profile_img_url": obj.author.profile_img_url if obj.author.profile_img_url else None,
        }

    def get_category(self, obj: Post) -> Dict[str, Any]:
        """
        카테고리 정보 추철
        """
        return {"id": obj.category.id, "name": obj.category.name}


class PostUpdateSerializer(serializers.ModelSerializer[Post]):
    """
    게시글 수정을 위한 Serializer
    """

    category_id: serializers.IntegerField = serializers.IntegerField(required=False)

    class Meta:
        model = Post
        fields: tuple[str, ...] = (
            "id",
            "title",
            "content",
            "category_id",
        )

    def validate_title(self, value: str) -> str:
        """
        제목 유효성 검사
        공백 제외 2자 이상
        """

        if len(value.strip()) < 2:
            raise serializers.ValidationError("제목은 최소 2자 이상이어야 합니다.")
        return value
