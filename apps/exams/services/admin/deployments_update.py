from typing import Any

from apps.exams.models import ExamDeployment


class ExamDeploymentUpdateNotFoundError(Exception):
    """수정할 배포 정보를 찾지 못했을 때 발생."""


def update_exam_deployment(deployment_id: int, validated_data: dict[str, Any]) -> ExamDeployment:
    try:
        deployment = ExamDeployment.objects.get(id=deployment_id)
    except ExamDeployment.DoesNotExist as exc:
        raise ExamDeploymentUpdateNotFoundError from exc

    deployment.open_at = validated_data["open_at"]
    deployment.close_at = validated_data["close_at"]
    deployment.duration_time = validated_data["duration_time"]
    deployment.save(update_fields=["open_at", "close_at", "duration_time", "updated_at"])

    return deployment
