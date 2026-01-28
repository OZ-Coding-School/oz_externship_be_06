from typing import Any

from rest_framework import serializers


class AdminExamDeploymentStatusRequestSerializer(serializers.Serializer[Any]):
    """쪽지시험 배포 상태 변경 요청 스키마."""

    status = serializers.CharField()

    def validate_status(self, value: str) -> str:
        if value not in {"activated", "deactivated"}:
            raise serializers.ValidationError("유효하지 않은 배포 상태 요청입니다.")
        return value


class AdminExamDeploymentStatusResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 배포 상태 변경 응답 스키마."""

    deployment_id = serializers.IntegerField()
    status = serializers.CharField()
