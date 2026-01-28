from typing import Any

from rest_framework import serializers


class ExamBaseResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 공통 응답 스키마."""

    exam_status = serializers.CharField()
    force_submit = serializers.BooleanField()


class ExamStatusResponseSerializer(ExamBaseResponseSerializer):
    """쪽지시험 상태 응답 스키마."""
