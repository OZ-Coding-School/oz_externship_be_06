from django.db import transaction

from apps.exams.models import ExamSubmission


class ExamSubmissionDeleteNotFoundError(Exception):
    """삭제할 응시 내역을 찾지 못했을 때 발생."""


class ExamSubmissionDeleteConflictError(Exception):
    """응시 내역 삭제 중 충돌 발생 시."""


def delete_exam_submission(submission_id: int) -> dict[str, int]:
    submission = ExamSubmission.objects.filter(id=submission_id).first()
    if not submission:
        raise ExamSubmissionDeleteNotFoundError

    try:
        with transaction.atomic():
            submission.delete()
    except Exception as exc:
        raise ExamSubmissionDeleteConflictError from exc

    return {"submission_id": submission_id}
