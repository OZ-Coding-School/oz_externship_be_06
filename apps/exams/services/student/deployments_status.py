from datetime import datetime

from django.utils import timezone

from apps.exams.constants import ExamStatus
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
