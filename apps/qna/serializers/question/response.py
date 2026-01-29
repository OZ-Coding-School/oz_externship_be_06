from typing import Any

from rest_framework import serializers

from apps.qna.models import Question, QuestionImage
from apps.qna.serializers.answer.response import AnswerCreateResponseSerializer
from apps.qna.serializers.base import QnaValidationMixin
from apps.qna.serializers.question.common import (
    QuestionAuthorSerializer,
    QuestionCategoryListSerializer,
)
from apps.qna.utils.content_parser import ContentParser


# ==============================================================================
# [GET] Question List
# /api/v1/qna/questions
# ==============================================================================
class QuestionQuerySerializer(QnaValidationMixin, serializers.Serializer[Any]):
    """
    질문 목록 조회를 위한 쿼리 파라미터 시리얼라이저
    """

    search_keyword = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False)
    answer_status = serializers.ChoiceField(choices=["waiting", "answered"], required=False)
    sort = serializers.ChoiceField(choices=["latest", "oldest", "most_views"], default="latest")
    page = serializers.IntegerField(default=1)
    size = serializers.IntegerField(default=10)

    default_error_message = "유효하지 않은 목록 조회 요청입니다."


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
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    def get_thumbnail_img_url(self, obj: Question) -> Any:
        """본문 내용에서 첫 번째 이미지 URL을 파싱하여 반환"""
        return ContentParser.extract_thumbnail_img_url(obj.content)


# ==============================================================================
# [GET] Question Detail
# /api/v1/qna/questions/{question_id}
# ==============================================================================
class QuestionImageSerializer(serializers.ModelSerializer[QuestionImage]):
    """
    질문 이미지 시리얼라이저
    """

    class Meta:
        model = QuestionImage
        fields = ["id", "img_url"]


class QuestionDetailSerializer(serializers.ModelSerializer[Question]):
    """
    질문 상세 조회 응답 시리얼라이저
    """

    category = QuestionCategoryListSerializer(read_only=True)
    author = QuestionAuthorSerializer(read_only=True)
    images = QuestionImageSerializer(many=True, read_only=True)
    answers = AnswerCreateResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "title",
            "content",
            "category",
            "images",
            "view_count",
            "created_at",
            "author",
            "answers",
        ]


# ==============================================================================
# [ACTION RESPONSES] POST Success
# [POST] Question Create
# /api/v1/qna/questions/
# ==============================================================================
class QuestionCreateResponseSerializer(QnaValidationMixin, serializers.Serializer[Any]):
    """
    질문 등록 응답 시리얼라이저
    """

    message = serializers.CharField(default="질문이 성공적으로 등록되었습니다.")
    question_id = serializers.IntegerField(source="id")
