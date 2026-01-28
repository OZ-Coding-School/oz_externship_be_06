from typing import Any

from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer[Any]):
    """에러 응답 스키마."""

    error_detail = serializers.CharField()

