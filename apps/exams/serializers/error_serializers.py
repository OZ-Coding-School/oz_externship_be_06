from typing import Any

from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer[Any]):
    """에러 응답 스키마."""

    error_detail = serializers.CharField()


class ErrorDetailSerializer(serializers.Serializer[Any]):
    """권한/인증 에러 응답 스키마."""

    detail = serializers.CharField()
