from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from apps.exams.models import ExamDeployment, ExamQuestion, ExamSubmission
from apps.exams.services.answers_json import normalize_answers_json
from apps.exams.services.grading import grade_submission


@dataclass(frozen=True)
class AutoSubmitResult:
    submitted: bool


@transaction.atomic
def auto_submit_if_overdue(
    *,
    deployment: ExamDeployment,
    user_id: int,
    now: datetime | None = None,
    force: bool = False,
) -> AutoSubmitResult:
    current = now or timezone.now()

    submission = (
        ExamSubmission.objects.select_for_update()
        .select_related("deployment")
        .filter(submitter_id=user_id, deployment=deployment)
        .first()
    )
    if submission is None:
        return AutoSubmitResult(submitted=False)

    if submission.answers_json:
        return AutoSubmitResult(submitted=False)

    if not force:
        deadline = submission.started_at + timedelta(minutes=deployment.duration_time)
        if current <= deadline:
            return AutoSubmitResult(submitted=False)

    answers = normalize_answers_json(submission.answers_json)
    if not answers:
        questions = ExamQuestion.objects.filter(exam=deployment.exam).only("id")
        answers = [{"question_id": q.id, "submitted_answer": None} for q in questions]

    submission.answers_json = answers
    submission.save(update_fields=["answers_json", "updated_at"])
    grade_submission(submission)

    return AutoSubmitResult(submitted=True)
