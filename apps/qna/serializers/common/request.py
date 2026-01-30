import os
from typing import Any

from rest_framework import serializers

from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.serializers.base import QnaValidationMixin
from apps.qna.utils.constants import ErrorMessages


class PresignedUrlRequestSerializer(QnaValidationMixin, serializers.Serializer):
    """
    Presigned URL 발급 요청 시리얼라이저
    """

    file_name = serializers.CharField(max_length=255, help_text="원본 파일명 (예: error_screenshot.png)")
    default_error_message = ErrorMessages.INVALID_REQUEST

    def validate_file_name(self, value: str) -> str:
        """파일 확장자 검증 (jpg, jpeg, png, gif)"""
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
        _, ext = os.path.splitext(value.lower())
        if ext not in allowed_extensions:
            raise QnaBaseException(detail=ErrorMessages.UNSUPPORTED_FILE_FORMAT)

        return value
