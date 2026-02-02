from typing import Any

from rest_framework import serializers

from apps.qna.constants import ErrorMessages
from apps.qna.models import Question


# ==============================================================================
# [POST] Question Create
# /api/v1/qna/questions
# ==============================================================================
class QuestionCreateSerializer(serializers.ModelSerializer[Question]):
    """
    질문 등록 시리얼라이저
    """

    category_id = serializers.IntegerField(required=True, help_text="카테고리 ID (소분류)")
    default_error_message = ErrorMessages.INVALID_QUESTION_CREATE

    class Meta:
        model = Question
        fields = ["title", "content", "category_id"]
