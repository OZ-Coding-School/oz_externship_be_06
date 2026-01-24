from django.db import transaction

from apps.exams.models import ExamDeployment


class ExamDeploymentStatusNotFoundError(Exception):
    """배포 정보를 찾지 못했을 때 발생."""


class ExamDeploymentStatusConflictError(Exception):
    """배포 상태 변경 중 충돌 발생 시."""


def update_deployment_status(deployment_id: int, status: str) -> ExamDeployment:
    try:
        with transaction.atomic():
            try:
                deployment = ExamDeployment.objects.select_for_update().get(id=deployment_id)
            except ExamDeployment.DoesNotExist as exc:
                raise ExamDeploymentStatusNotFoundError from exc

            new_status = (
                ExamDeployment.StatusChoices.ACTIVATED
                if status == "activated"
                else ExamDeployment.StatusChoices.DEACTIVATED
            )
            deployment.status = new_status
            deployment.save(update_fields=["status"])
    except ExamDeploymentStatusNotFoundError:
        raise
    except Exception as exc:
        raise ExamDeploymentStatusConflictError from exc

    return deployment
