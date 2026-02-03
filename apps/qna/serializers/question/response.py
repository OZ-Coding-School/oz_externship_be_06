from typing import Any, Optional

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from apps.qna.models import Question, QuestionCategory, QuestionImage
from apps.qna.serializers.answer.response import AnswerSerializer
from apps.qna.serializers.question.common import (
    QuestionAuthorSerializer,
    QuestionCategoryListSerializer,
)
from apps.qna.utils.content_parser import ContentParser


# ==============================================================================
# [GET] Question List
# /api/v1/qna/questions
# ==============================================================================
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
    answers = AnswerSerializer(many=True, read_only=True)

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
# [GET] Question category List
# /api/v1/qna/categories
# ==============================================================================
class QuestionCategoryTreeSerializer(serializers.Serializer[QuestionCategory]):
    """
    카테고리 계층 구조(Tree) 조회를 위한 재귀적 시리얼라이저
    """

    id = serializers.IntegerField(help_text="카테고리 ID")
    name = serializers.CharField(help_text="카테고리명")
    depth = serializers.IntegerField(help_text="계층 깊이 (0:대분류, 1:중분류, 2:소분류)")
    subcategories = serializers.SerializerMethodField(help_text="하위 카테고리 목록")

    def get_subcategories(self, obj: Any) -> ReturnList[Any]:
        """자식 노드를 재귀적으로 직렬화"""
        sub_data = getattr(obj, "subcategories", [])
        if hasattr(sub_data, "all"):
            sub_data = sub_data.all()

        return QuestionCategoryTreeSerializer(sub_data, many=True).data  # type: ignore


class QuestionCategoryTreeResponseSerializer(serializers.Serializer[Any]):
    """
    최상위 categories 키로 래핑하기 위한 응답 시리얼라이저
    """

    categories = QuestionCategoryTreeSerializer(many=True)


# ==============================================================================
# [ACTION RESPONSES] POST Success
# [POST] Question Create
# /api/v1/qna/questions/
# ==============================================================================
class QuestionCreateResponseSerializer(serializers.Serializer[Question]):
    """
    질문 등록 응답 시리얼라이저
    """

    message = serializers.CharField(default="질문이 성공적으로 등록되었습니다.")
    question_id = serializers.IntegerField(source="id")
