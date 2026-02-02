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


# ==============================================================================
# [GET] Question List
# /api/v1/qna/questions
# ==============================================================================
class QuestionQuerySerializer(serializers.Serializer[Any]):
    """
    질문 목록 조회를 위한 쿼리 파라미터 시리얼라이저
    """

    search_keyword = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False)
    answer_status = serializers.ChoiceField(choices=["waiting", "answered"], required=False)
    sort = serializers.ChoiceField(choices=["latest", "oldest", "most_views"], default="latest")
    page = serializers.IntegerField(default=1)
    size = serializers.IntegerField(default=10)

    default_error_message = ErrorMessages.INVALID_QUESTION_LIST
