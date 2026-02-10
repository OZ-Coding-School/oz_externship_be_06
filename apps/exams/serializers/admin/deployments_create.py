from typing import Any

from rest_framework import serializers

from apps.exams.constants import ErrorMessages
from apps.exams.validators import validate_duration_minutes, validate_time_range


class AdminExamDeploymentCreateRequestSerializer(serializers.Serializer[Any]):
    """쪽지시험 배포 생성 요청 스키마."""

    exam_id = serializers.IntegerField()
    cohort_id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField(input_formats=["%Y-%m-%d %H:%M:%S"])
    close_at = serializers.DateTimeField(input_formats=["%Y-%m-%d %H:%M:%S"])

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        duration_time = attrs.get("duration_time")
        validate_duration_minutes(
            duration_time,
            error_message=ErrorMessages.INVALID_DEPLOYMENT_CREATE_REQUEST,
            exc_factory=serializers.ValidationError,
        )

        validate_time_range(
            attrs.get("open_at"),
            attrs.get("close_at"),
            error_message=ErrorMessages.INVALID_DEPLOYMENT_CREATE_REQUEST,
            exc_factory=serializers.ValidationError,
        )

        return attrs


class AdminExamDeploymentCreateResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 배포 생성 응답 스키마."""

    pk = serializers.IntegerField()
