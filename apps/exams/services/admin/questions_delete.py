from django.db import transaction
from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamQuestion


def delete_exam_question(question_id: int) -> dict[str, int]:
    question = ExamQuestion.objects.filter(id=question_id).first()
    if not question:
        raise ErrorDetailException(ErrorMessages.QUESTION_NOT_FOUND.value, status.HTTP_404_NOT_FOUND)

    try:
        with transaction.atomic():
            question.delete()
    except Exception as exc:
        raise ErrorDetailException(ErrorMessages.QUESTION_DELETE_CONFLICT.value, status.HTTP_409_CONFLICT) from exc

    return {"exam_id": question.exam_id, "question_id": question_id}
