from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamSubmission


def get_exam_submission_detail(*, submission_id: int, user_id: int) -> ExamSubmission:

    submission = get_object_or_404(
        ExamSubmission.objects.select_related("deployment__exam").prefetch_related("deployment__exam__questions"),
        id=submission_id,
    )

    if submission.submitter_id != user_id:
        raise PermissionDenied()

    if submission.answers_json == {}:
        raise ErrorDetailException(
            ErrorMessages.INVALID_EXAM_SESSION.value,
            status.HTTP_400_BAD_REQUEST,
        )

    return submission
