from django.db import transaction

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamDeployment


def update_deployment_status(deployment_id: int, status_value: str) -> ExamDeployment:
    with transaction.atomic():
        try:
            deployment = ExamDeployment.objects.select_for_update().get(id=deployment_id)
        except ExamDeployment.DoesNotExist as exc:
            raise_error(ErrorMessages.DEPLOYMENT_NOT_FOUND)

        new_status = (
            ExamDeployment.StatusChoices.ACTIVATED
            if status_value == "activated"
            else ExamDeployment.StatusChoices.DEACTIVATED
        )
        deployment.status = new_status
        try:
            deployment.save(update_fields=["status"])
        except Exception as exc:
            raise_error(ErrorMessages.DEPLOYMENT_CONFLICT)

    return deployment
