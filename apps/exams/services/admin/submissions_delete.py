from django.db import transaction
from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamSubmission


def delete_exam_submission(submission_id: int) -> dict[str, int]:
    submission = ExamSubmission.objects.filter(id=submission_id).first()
    if not submission:
        raise ErrorDetailException(ErrorMessages.SUBMISSION_DELETE_NOT_FOUND.value, status.HTTP_404_NOT_FOUND)

    try:
        with transaction.atomic():
            submission.delete()
    except Exception as exc:
        raise ErrorDetailException(ErrorMessages.SUBMISSION_DELETE_CONFLICT.value, status.HTTP_409_CONFLICT) from exc

    return {"submission_id": submission_id}
