from django.db import transaction
from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamDeployment


def update_deployment_status(deployment_id: int, status: str) -> ExamDeployment:
    with transaction.atomic():
        try:
            deployment = ExamDeployment.objects.select_for_update().get(id=deployment_id)
        except ExamDeployment.DoesNotExist as exc:
            raise ErrorDetailException(ErrorMessages.DEPLOYMENT_NOT_FOUND.value, status.HTTP_404_NOT_FOUND) from exc

        new_status = (
            ExamDeployment.StatusChoices.ACTIVATED
            if status == "activated"
            else ExamDeployment.StatusChoices.DEACTIVATED
        )
        deployment.status = new_status
        try:
            deployment.save(update_fields=["status"])
        except Exception as exc:
            raise ErrorDetailException(ErrorMessages.DEPLOYMENT_CONFLICT.value, status.HTTP_409_CONFLICT) from exc

    return deployment
