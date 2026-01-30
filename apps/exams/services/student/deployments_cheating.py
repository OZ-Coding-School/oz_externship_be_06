from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.exams.constants import ErrorMessages, ExamStatus
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamDeployment, ExamSubmission
from apps.exams.services.answers_json import normalize_answers_json
from apps.exams.services.grading import grade_submission
from apps.exams.services.student.deployments_status import ensure_deployment_active


@dataclass(frozen=True)
class CheatingUpdateResult:
    cheating_count: int
    exam_status: str
    force_submit: bool


def update_cheating_count(
    *,
    deployment: ExamDeployment,
    user_id: int,
    answers_json: Any | None = None,
) -> CheatingUpdateResult:
    ensure_deployment_active(deployment)

    cheating_key = f"exam:cheating:{deployment.id}:{user_id}"
    submit_lock_key = f"exam:submit-lock:{deployment.id}:{user_id}"

    if ExamSubmission.objects.filter(submitter_id=user_id, deployment=deployment).exists():
        raise ErrorDetailException(ErrorMessages.SUBMISSION_ALREADY_SUBMITTED.value, 409)

    current_count = cache.get(cheating_key)
    ttl_seconds = max(1, deployment.duration_time * 60)
    if current_count is None:
        cheating_count = 1
        cache.set(cheating_key, 1, timeout=ttl_seconds)
    elif current_count >= 3:
        cheating_count = int(current_count)
    else:
        cheating_count = cache.incr(cheating_key)

    is_closed = cheating_count >= 3
    if is_closed:
        normalized_answers = normalize_answers_json(answers_json or [])

        if cache.add(submit_lock_key, "1", timeout=5):
            with transaction.atomic():
                submission, created = ExamSubmission.objects.select_for_update().get_or_create(
                    submitter_id=user_id,
                    deployment=deployment,
                    defaults={
                        "started_at": timezone.now(),
                        "cheating_count": cheating_count,
                        "answers_json": normalized_answers,
                    },
                )
                if not created:
                    submission.cheating_count = cheating_count
                    submission.answers_json = normalized_answers
                    submission.save(update_fields=["cheating_count", "answers_json"])
                grade_submission(submission)
            cache.delete(submit_lock_key)

    status_value = ExamStatus.CLOSED.value if is_closed else ExamStatus.ACTIVATED.value

    return CheatingUpdateResult(
        cheating_count=cheating_count,
        exam_status=status_value,
        force_submit=is_closed,
    )
