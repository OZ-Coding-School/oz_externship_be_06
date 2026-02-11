from typing import Any, Optional

from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory
from apps.qna.serializers.admin.question.common import (
    AdminAnswerSerializer,
    AdminQuestionAuthorSerializer,
)
from apps.qna.serializers.question.response import QuestionImageSerializer


# ==============================================================================
# [GET] Admin Question List
# /api/v1/admin/qna/questions
# ==============================================================================
class AdminQuestionListResponseSerializer(serializers.ModelSerializer[Question]):
    """
    어드민 질의응답 목록 응답 시리얼라이저
    """

    question_id = serializers.IntegerField(source="id")
    category_path = serializers.SerializerMethodField()
    content_preview = serializers.CharField()
    nickname = serializers.CharField(source="author.nickname")
    has_answer = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Question
        fields = [
            "question_id",
            "title",
            "category_path",
            "content_preview",
            "nickname",
            "view_count",
            "has_answer",
            "created_at",
            "updated_at",
        ]

    def get_category_path(self, obj: Question) -> str:
        """대분류 > 중분류 > 소분류 형태의 카테고리 경로 반환"""
        names: list[str] = []
        category: Optional[QuestionCategory] = obj.category
        while category:
            names.append(category.name)
            category = category.parent
        return " > ".join(reversed(names))

    def get_has_answer(self, obj: Question) -> bool:
        """답변 존재 여부 반환 (annotated answer_count 활용)"""
        return getattr(obj, "answer_count", 0) > 0


# ==============================================================================
# [GET] Admin Question Detail
# /api/v1/admin/qna/questions/{question_id}
# ==============================================================================
class AdminQuestionDetailResponseSerializer(serializers.ModelSerializer[Question]):
    """
    어드민 질문 상세 조회 응답 시리얼라이저
    """

    question_id = serializers.IntegerField(source="id")
    author = AdminQuestionAuthorSerializer(read_only=True)
    images = QuestionImageSerializer(many=True, read_only=True)
    has_answer = serializers.SerializerMethodField()
    answers = AdminAnswerSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Question
        fields = [
            "question_id",
            "title",
            "content",
            "images",
            "author",
            "view_count",
            "has_answer",
            "created_at",
            "updated_at",
            "answers",
        ]

    def get_has_answer(self, obj: Question) -> bool:
        return len(obj.answers.all()) > 0


# ==============================================================================
# [DELETE] Admin Question Delete
# /api/v1/admin/qna/questions/{question_id}
# ==============================================================================
class AdminQuestionDeleteResponseSerializer(serializers.Serializer[Any]):
    """
    어드민 질의응답 삭제 응답 시리얼라이저
    """

    question_id = serializers.IntegerField()
    deleted_answer_count = serializers.IntegerField()
    deleted_comment_count = serializers.IntegerField()
