from django.db import transaction

from apps.exams.models import ExamDeployment, ExamSubmission


class ExamDeploymentDeleteNotFoundError(Exception):
    # 404
    pass


class ExamDeploymentDeleteConflictError(Exception):
    # 409
    pass


def delete_exam_deployment(deployment_id: int) -> dict[str, int | bool]:
    # 404
    try:
        deployment = ExamDeployment.objects.get(id=deployment_id)
    except ExamDeployment.DoesNotExist:
        raise ExamDeploymentDeleteNotFoundError

    # 관련 제출 데이터 먼저 삭제 (응시 데이터도 즉시 삭제)
    # 하나라도 실패하면 전부 롤백
    try:
        with transaction.atomic():
            ExamSubmission.objects.filter(deployment=deployment).delete()
            deployment.delete()
    # 409
    except Exception:
        raise ExamDeploymentDeleteConflictError()

    return {
        "deployment_id": deployment_id,
        "is_deleted": True,
    }
