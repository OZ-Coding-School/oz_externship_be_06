from django.db import transaction

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import Exam


def delete_exam(exam_id: int) -> int:
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist as exc:
        raise_error(ErrorMessages.EXAM_DELETE_NOT_FOUND)

    try:
        with transaction.atomic():
            exam.delete()
    except Exception as exc:
        raise_error(ErrorMessages.EXAM_DELETE_CONFLICT)

    return exam_id
