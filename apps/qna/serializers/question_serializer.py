from typing import Any

from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory
from apps.qna.serializers.question_base import QnAVersionedValidationMixin
from apps.qna.utils.content_parser import ContentParser
from apps.users.models import User


class QuestionQuerySerializer(QnAVersionedValidationMixin, serializers.Serializer[Any]):
    """
    질문 목록 조회를 위한 쿼리 파라미터 시리얼라이저
    """

    search_keyword = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False)
    answer_status = serializers.ChoiceField(choices=["waiting", "answered"], required=False)
    sort = serializers.ChoiceField(choices=["latest", "oldest", "most_views"], default="latest")
    page = serializers.IntegerField(default=1)
    size = serializers.IntegerField(default=10)


class QuestionCategoryListSerializer(serializers.ModelSerializer[QuestionCategory]):
    """
    질의응답 목록용 카테고리 시리얼라이저 (대 > 중 > 소 형태)
    """

    depth = serializers.SerializerMethodField()
    names = serializers.SerializerMethodField()

    class Meta:
        model = QuestionCategory
        fields = ["id", "depth", "names"]

    def get_depth(self, obj: QuestionCategory) -> int:
        """모델에 필드가 없으므로 부모를 거슬러 올라가며 깊이를 계산"""
        depth = 0
        curr = obj.parent
        while curr:
            depth += 1
            curr = curr.parent
        return depth

    def get_names(self, obj: QuestionCategory) -> list[str]:
        """부모 카테고리를 거슬러 올라가며 전체 경로 이름을 리스트로 생성"""
        names: list[str] = []
        curr: QuestionCategory | None = obj
        while curr:
            names.insert(0, curr.name)
            curr = curr.parent
        return names


class QuestionAuthorSerializer(serializers.ModelSerializer[User]):
    """
    질문 작성자 정보 시리얼라이저
    """

    profile_image_url = serializers.ImageField(source="profile_img_url", use_url=True)

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url"]


class QuestionListSerializer(serializers.ModelSerializer[Question]):
    """
    질의응답 목록 조회 카드 형태 항목 시리얼라이저
    """

    category = QuestionCategoryListSerializer(read_only=True)
    author = QuestionAuthorSerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()
    answer_count = serializers.IntegerField(read_only=True)
    thumbnail_img_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "category",
            "author",
            "title",
            "content_preview",
            "answer_count",
            "view_count",
            "created_at",
            "thumbnail_img_url",
        ]

    def get_content_preview(self, obj: Question) -> str:
        """본문 프리뷰 생성"""
        return obj.content[:50] + "..." if len(obj.content) > 100 else obj.content

    def get_thumbnail_img_url(self, obj: Question) -> Any:
        """본문 내용에서 첫 번째 이미지 URL을 파싱하여 반환"""
        return ContentParser.extract_thumbnail_img_url(obj.content)


class QuestionCreateSerializer(QnAVersionedValidationMixin, serializers.ModelSerializer[Question]):
    """
    질문 등록 시리얼라이저
    """

    category_id = serializers.IntegerField(required=True, help_text="카테고리 ID (소분류)")

    class Meta:
        model = Question
        fields = ["title", "content", "category_id"]


class QuestionCreateResponseSerializer(QnAVersionedValidationMixin, serializers.Serializer[Any]):
    """
    질문 등록 응답 시리얼라이저
    """

    message = serializers.CharField(default="질문이 성공적으로 등록되었습니다.")
    question_id = serializers.IntegerField(source="id")
