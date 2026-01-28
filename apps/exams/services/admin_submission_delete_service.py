from django.db import IntegrityError, OperationalError, transaction

from apps.exams.models import ExamSubmission


class ExamSubmissionDeleteNotFoundError(Exception):
    """삭제 대상 응시내역을 찾지 못했을 때 발생."""


class ExamSubmissionDeleteConflictError(Exception):
    """응시내역 삭제 중 충돌 발생 시."""


def delete_exam_submission(submission_id: int) -> int:
    try:
        submission = ExamSubmission.objects.get(id=submission_id)
    except ExamSubmission.DoesNotExist as exc:
        raise ExamSubmissionDeleteNotFoundError from exc

    try:
        with transaction.atomic():
            submission.delete()
    except (IntegrityError, OperationalError) as exc:
        raise ExamSubmissionDeleteConflictError from exc

    return submission_id
