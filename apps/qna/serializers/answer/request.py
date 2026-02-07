from rest_framework import serializers

from apps.qna.constants import ErrorMessages
from apps.qna.models import Answer


# ==============================================================================
# [POST] Answer Create
# /api/v1/qna/questions/{question_id}/answers
# ==============================================================================
class AnswerCreateSerializer(serializers.ModelSerializer[Answer]):
    """
    답변 등록 시리얼라이저
    """

    content = serializers.CharField(required=True, help_text="답변 내용")
    image_urls = serializers.ListField(
        child=serializers.URLField(), required=False, allow_empty=True, default=list, help_text="첨부 이미지 URL 목록"
    )

    default_error_message = ErrorMessages.INVALID_ANSWER_CREATE

    class Meta:
        model = Answer
        fields = ["content", "image_urls"]


# ==============================================================================
# [PUT] Answer Update
# /api/v1/qna/answers/{answer_id}
# ==============================================================================
class AnswerUpdateSerializer(serializers.ModelSerializer[Answer]):
    """
    답변 수정 시리얼라이저
    """

    content = serializers.CharField(required=True, help_text="답변 내용")
    image_urls = serializers.ListField(
        child=serializers.URLField(), required=False, allow_empty=True, default=list, help_text="첨부 이미지 URL 목록"
    )

    default_error_message = ErrorMessages.INVALID_ANSWER_UPDATE

    class Meta:
        model = Answer
        fields = ["content", "image_urls"]


# ==============================================================================
# [POST] Answer Comment Create
# /api/v1/qna/answers/{answer_id}/comments
# ==============================================================================
class AnswerCommentCreateSerializer(serializers.Serializer[Answer]):
    """
    답변 댓글 등록 시리얼라이저
    """

    content = serializers.CharField(
        max_length=500,
        required=True,
        error_messages={
            "max_length": ErrorMessages.INVALID_COMMENT_LENGTH_LIMIT.value,
            "blank": ErrorMessages.INVALID_COMMENT_BLANK.value,
        },
    )
