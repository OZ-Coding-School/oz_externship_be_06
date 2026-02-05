from django.db import transaction
from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import Exam


def delete_exam(exam_id: int) -> int:
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist as exc:
        raise ErrorDetailException(ErrorMessages.EXAM_DELETE_NOT_FOUND.value, status.HTTP_404_NOT_FOUND) from exc

    try:
        with transaction.atomic():
            exam.delete()
    except Exception as exc:
        raise ErrorDetailException(ErrorMessages.EXAM_DELETE_CONFLICT.value, status.HTTP_409_CONFLICT) from exc

    return exam_id
