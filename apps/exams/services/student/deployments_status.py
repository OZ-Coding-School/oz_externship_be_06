from datetime import datetime

from django.utils import timezone

from apps.exams.constants import ErrorMessages, ExamStatus
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamDeployment


def is_deployment_activated(deployment: ExamDeployment) -> bool:
    return deployment.status == ExamDeployment.StatusChoices.ACTIVATED


def is_deployment_opened(deployment: ExamDeployment, *, now: datetime | None = None) -> bool:
    current = now or timezone.now()
    return current >= deployment.open_at


def is_deployment_time_closed(deployment: ExamDeployment, *, now: datetime | None = None) -> bool:
    current = now or timezone.now()
    return current > deployment.close_at


def is_deployment_active_now(deployment: ExamDeployment, *, now: datetime | None = None) -> bool:
    current = now or timezone.now()
    return (
        deployment.status == ExamDeployment.StatusChoices.ACTIVATED
        and deployment.open_at <= current <= deployment.close_at
    )


def get_exam_status(deployment: ExamDeployment, *, now: datetime | None = None) -> ExamStatus:
    return ExamStatus.ACTIVATED if is_deployment_active_now(deployment, now=now) else ExamStatus.CLOSED


def get_deployment_or_404(
    deployment_id: int,
    *,
    error_message: ErrorMessages = ErrorMessages.DEPLOYMENT_NOT_FOUND,
) -> ExamDeployment:
    try:
        return ExamDeployment.objects.select_related("exam", "cohort").get(id=deployment_id)
    except ExamDeployment.DoesNotExist as exc:
        raise ErrorDetailException(error_message.value, 404) from exc


def validate_deployment_active(deployment: ExamDeployment, *, now: datetime | None = None) -> None:
    if not is_deployment_activated(deployment):
        raise ErrorDetailException(ErrorMessages.INVALID_CHECK_CODE_REQUEST.value, 400)

    current = now or timezone.now()
    if not is_deployment_opened(deployment, now=current):
        raise ErrorDetailException(ErrorMessages.EXAM_NOT_AVAILABLE.value, 423)

    if is_deployment_time_closed(deployment, now=current):
        raise ErrorDetailException(ErrorMessages.EXAM_ALREADY_CLOSED.value, 400)


def ensure_deployment_active(deployment: ExamDeployment) -> None:
    if not is_deployment_active_now(deployment):
        raise ErrorDetailException(ErrorMessages.EXAM_ALREADY_CLOSED.value, 410)
