from rest_framework import serializers

from apps.qna.models import Answer
from apps.qna.serializers.base import QnaValidationMixin
from apps.qna.utils.constants import ErrorMessages


# ==============================================================================
# [POST] Answer Create
# /api/v1/qna/questions/{question_id}/answers
# ==============================================================================
class AnswerCreateSerializer(QnaValidationMixin, serializers.ModelSerializer[Answer]):
    """
    답변 등록 시리얼라이저
    """

    content = serializers.CharField(required=True, help_text="답변 내용 (마크다운)")
    image_urls = serializers.ListField(
        child=serializers.URLField(), required=False, allow_empty=True, default=list, help_text="첨부 이미지 URL 목록"
    )

    default_error_message = ErrorMessages.INVALID_ANSWER_CREATE

    class Meta:
        model = Answer
        fields = ["content", "image_urls"]
