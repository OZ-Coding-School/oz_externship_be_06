from typing import Any, cast

from django.utils import timezone

from apps.exams.models import ExamDeployment, ExamSubmission
from apps.users.models import User


def ensure_student_role(user: User) -> bool:
    return user.role == User.Role.STUDENT


def get_submission(user: User, deployment: ExamDeployment) -> ExamSubmission | None:
    submission_model = cast(Any, ExamSubmission)
    submission = submission_model.objects.filter(submitter=user, deployment=deployment).order_by("-created_at").first()
    return cast(ExamSubmission | None, submission)


def is_exam_closed(deployment: ExamDeployment, submission: ExamSubmission) -> bool:
    now = timezone.now()
    if deployment.status != ExamDeployment.StatusChoices.ACTIVATED:
        return True
    if submission.cheating_count >= 3:
        return True
    if deployment.close_at and now >= deployment.close_at:
        return True
    elapsed = now - submission.started_at
    if elapsed.total_seconds() >= deployment.duration_time * 60:
        return True
    return False
