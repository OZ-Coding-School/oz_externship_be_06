import os
from typing import Any

from rest_framework import serializers
from apps.core.exceptions.base import CoreBaseException


class PresignedUrlRequestSerializer(serializers.Serializer[Any]):
    """
    Presigned URL 발급 요청 시리얼라이저
    """

    file_name = serializers.CharField(max_length=255, help_text="원본 파일명 (예: error_screenshot.png)")

    def validate_file_name(self, value: str) -> str:
        """파일 확장자 검증 (jpg, jpeg, png, gif)"""
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
        _, ext = os.path.splitext(value.lower())
        if ext not in allowed_extensions:
            raise CoreBaseException(detail="지원하지 않는 파일 형식입니다.")

        return value
