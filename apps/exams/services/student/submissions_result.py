from __future__ import annotations

from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamSubmission


def get_exam_submission_detail(*, submission_id: int, user_id: int) -> ExamSubmission:
    submission = (
        ExamSubmission.objects.select_related("deployment__exam")
        .prefetch_related("deployment__exam__questions")
        .filter(id=submission_id)
        .first()
    )
    if submission is None:
        raise ErrorDetailException(ErrorMessages.SUBMISSION_DETAIL_NOT_FOUND.value, status.HTTP_404_NOT_FOUND)

    if submission.submitter_id != user_id:
        raise ErrorDetailException(ErrorMessages.FORBIDDEN.value, status.HTTP_403_FORBIDDEN)

    if submission.answers_json == {}:
        raise ErrorDetailException(
            ErrorMessages.INVALID_EXAM_SESSION.value,
            status.HTTP_400_BAD_REQUEST,
        )

    return submission
