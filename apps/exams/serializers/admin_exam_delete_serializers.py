from typing import Any

from rest_framework import serializers


class AdminExamDeleteResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 삭제 응답 스키마."""

    id = serializers.IntegerField()
