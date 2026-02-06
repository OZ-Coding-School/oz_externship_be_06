from __future__ import annotations

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamSubmission


def get_exam_submission_detail(*, submission_id: int, user_id: int) -> ExamSubmission:
    submission = (
        ExamSubmission.objects.select_related("deployment__exam")
        .prefetch_related("deployment__exam__questions")
        .filter(id=submission_id)
        .first()
    )
    if submission is None:
        raise_error(ErrorMessages.SUBMISSION_DETAIL_NOT_FOUND)

    if submission.submitter_id != user_id:
        raise_error(ErrorMessages.FORBIDDEN)

    if submission.answers_json == {}:
        raise_error(ErrorMessages.INVALID_EXAM_SESSION)

    return submission
