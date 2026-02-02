from typing import Any

from rest_framework import serializers


class PresignedUrlResponseSerializer(serializers.Serializer[Any]):
    """
    Presigned URL 발급 성공 응답 시리얼라이저
    """

    presigned_url = serializers.CharField(help_text="S3 업로드용 임시 URL")
    img_url = serializers.CharField(help_text="이미지 접근용 Public URL")
    key = serializers.CharField(help_text="S3 객체 키")
