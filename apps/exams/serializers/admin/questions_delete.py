from typing import Any

from rest_framework import serializers


class AdminExamQuestionDeleteResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 문제 삭제 응답 스키마."""

    exam_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
