from django.db import transaction
from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamDeployment, ExamSubmission


def delete_exam_deployment(deployment_id: int) -> dict[str, int | bool]:
    # 404
    try:
        deployment = ExamDeployment.objects.get(id=deployment_id)
    except ExamDeployment.DoesNotExist:
        raise ErrorDetailException(
            ErrorMessages.DEPLOYMENT_DELETE_NOT_FOUND.value,
            status.HTTP_404_NOT_FOUND,
        )

    # 관련 제출 데이터 먼저 삭제 (응시 데이터도 즉시 삭제)
    # 하나라도 실패하면 전부 롤백
    try:
        with transaction.atomic():
            ExamSubmission.objects.filter(deployment=deployment).delete()
            deployment.delete()
    # 409
    except Exception as exc:
        # 409: 삭제 충돌
        raise ErrorDetailException(
            ErrorMessages.DEPLOYMENT_DELETE_CONFLICT.value,
            status.HTTP_409_CONFLICT,
        ) from exc

    return {
        "deployment_id": deployment_id,
    }
