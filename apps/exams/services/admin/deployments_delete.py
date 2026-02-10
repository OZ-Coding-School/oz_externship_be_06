from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamDeployment, ExamSubmission


def delete_exam_deployment(deployment_id: int) -> dict[str, int | bool]:
    # 404
    try:
        deployment = ExamDeployment.objects.get(id=deployment_id)
    except ExamDeployment.DoesNotExist:
        raise_error(ErrorMessages.DEPLOYMENT_DELETE_NOT_FOUND)

    # 관련 제출 데이터 먼저 삭제 (응시 데이터도 즉시 삭제)
    # 하나라도 실패하면 전부 롤백
    try:
        with transaction.atomic():
            ExamSubmission.objects.filter(deployment=deployment).delete()
            deployment.delete()
    # 409
    except (ProtectedError, IntegrityError):
        raise_error(ErrorMessages.DEPLOYMENT_DELETE_CONFLICT)

    return {
        "deployment_id": deployment_id,
    }
