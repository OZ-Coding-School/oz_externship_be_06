from django.db import transaction

from apps.exams.models import Exam


class ExamDeleteNotFoundError(Exception):
    """삭제 대상 쪽지시험을 찾지 못했을 때 발생."""


class ExamDeleteConflictError(Exception):
    """쪽지시험 삭제 중 충돌 발생 시."""


def delete_exam(exam_id: int) -> int:
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist as exc:
        raise ExamDeleteNotFoundError from exc

    try:
        with transaction.atomic():
            exam.delete()
    except Exception as exc:
        raise ExamDeleteConflictError from exc

    return exam_id
