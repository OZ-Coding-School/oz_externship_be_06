import os
from typing import Any

from rest_framework import exceptions, serializers, status

from apps.core.constants import ALLOWED_IMAGE_EXTENSIONS


class PresignedUrlRequestSerializer(serializers.Serializer[Any]):
    """
    Presigned URL 발급 요청 시리얼라이저
    """

    file_name = serializers.CharField(max_length=255, help_text="원본 파일명 (예: error_screenshot.png)")

    def validate_file_name(self, value: str) -> str:
        """파일 확장자 검증 (jpg, jpeg, png, gif)"""
        _, ext = os.path.splitext(value.lower())

        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            error = exceptions.APIException(detail={"error_detail": "지원하지 않는 파일 형식입니다."})
            error.status_code = status.HTTP_400_BAD_REQUEST
            raise error

        return value


class PresignedUrlResponseSerializer(serializers.Serializer[Any]):
    """
    Presigned URL 발급 성공 응답 시리얼라이저
    """

    presigned_url = serializers.CharField(help_text="S3 업로드용 임시 URL")
    img_url = serializers.CharField(help_text="이미지 접근용 Public URL")
    key = serializers.CharField(help_text="S3 객체 키")
