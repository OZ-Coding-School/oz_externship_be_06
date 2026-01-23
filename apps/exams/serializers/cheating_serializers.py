from typing import Any

from rest_framework import serializers

from apps.exams.serializers.status_serializers import ExamBaseResponseSerializer


class ExamCheatingResponseSerializer(ExamBaseResponseSerializer):
    """부정행위 카운트 응답 스키마."""

    cheating_count = serializers.IntegerField()


class ExamCheatingRequestSerializer(serializers.Serializer[Any]):
    """부정행위 카운트 요청 스키마."""

    answers_json = serializers.JSONField(required=False)
