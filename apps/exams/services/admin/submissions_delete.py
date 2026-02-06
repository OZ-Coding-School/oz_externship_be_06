from django.db import transaction

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamSubmission


def delete_exam_submission(submission_id: int) -> dict[str, int]:
    submission = ExamSubmission.objects.filter(id=submission_id).first()
    if not submission:
        raise_error(ErrorMessages.SUBMISSION_DELETE_NOT_FOUND)

    try:
        with transaction.atomic():
            submission.delete()
    except Exception as exc:
        raise_error(ErrorMessages.SUBMISSION_DELETE_CONFLICT)

    return {"submission_id": submission_id}
