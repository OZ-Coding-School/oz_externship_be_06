from typing import Any

from rest_framework import serializers


class AdminExamSubmissionDeleteResponseSerializer(serializers.Serializer[Any]):
    """응시내역 삭제 응답 스키마."""

    submission_id = serializers.IntegerField()
