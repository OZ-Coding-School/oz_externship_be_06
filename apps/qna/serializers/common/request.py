from rest_framework import serializers

from apps.qna.serializers.base import QnaValidationMixin
from apps.qna.utils.constants import ErrorMessages


class PresignedUrlRequestSerializer(QnaValidationMixin, serializers.Serializer):
    """
    Presigned URL 발급 요청 시리얼라이저
    """

    file_name = serializers.CharField(max_length=255, help_text="원본 파일명 (예: error_screenshot.png)")

    # Enum 상수를 활용한 에러 메시지 처리
    default_error_message = ErrorMessages.INVALID_AI_REQUEST
