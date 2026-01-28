from typing import Any

from rest_framework import serializers


class AdminExamDeploymentCreateRequestSerializer(serializers.Serializer[Any]):
    """쪽지시험 배포 생성 요청 스키마."""

    exam_id = serializers.IntegerField()
    cohort_id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField(input_formats=["%Y-%m-%d %H:%M:%S"])
    close_at = serializers.DateTimeField(input_formats=["%Y-%m-%d %H:%M:%S"])

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        duration_time = attrs.get("duration_time")
        if not isinstance(duration_time, int) or duration_time <= 0:
            raise serializers.ValidationError("유효하지 않은 배포 생성 요청입니다.")

        open_at = attrs.get("open_at")
        close_at = attrs.get("close_at")
        if open_at and close_at and open_at >= close_at:
            raise serializers.ValidationError("유효하지 않은 배포 생성 요청입니다.")

        return attrs


class AdminExamDeploymentCreateResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 배포 생성 응답 스키마."""

    pk = serializers.IntegerField()
