from typing import Any

from rest_framework import serializers


class AdminExamDeploymentUpdateRequestSerializer(serializers.Serializer[Any]):
    """쪽지시험 배포 수정 요청 스키마."""

    open_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    close_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    duration_time = serializers.IntegerField(min_value=1, required=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["open_at"] >= attrs["close_at"]:
            from apps.exams.constants import ErrorMessages

            raise serializers.ValidationError(ErrorMessages.INVALID_DEPLOYMENT_UPDATE_REQUEST.value)
        return attrs


class AdminExamDeploymentUpdateResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 배포 수정 응답 스키마."""

    deployment_id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    close_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
