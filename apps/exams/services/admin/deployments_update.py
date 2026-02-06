from typing import Any

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamDeployment


def update_exam_deployment(deployment_id: int, validated_data: dict[str, Any]) -> ExamDeployment:
    try:
        deployment = ExamDeployment.objects.get(id=deployment_id)
    except ExamDeployment.DoesNotExist as exc:
        raise_error(ErrorMessages.DEPLOYMENT_UPDATE_NOT_FOUND)

    deployment.open_at = validated_data["open_at"]
    deployment.close_at = validated_data["close_at"]
    deployment.duration_time = validated_data["duration_time"]
    deployment.save(update_fields=["open_at", "close_at", "duration_time", "updated_at"])

    return deployment
