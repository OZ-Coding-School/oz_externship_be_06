from django.db import transaction
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamQuestion


def delete_exam_question(question_id: int) -> dict[str, int]:
    question = ExamQuestion.objects.filter(id=question_id).first()
    if not question:
        raise_error(ErrorMessages.QUESTION_NOT_FOUND)

    try:
        with transaction.atomic():
            question.delete()
    except Exception as exc:
        raise_error(ErrorMessages.QUESTION_DELETE_CONFLICT)

    return {"exam_id": question.exam_id, "question_id": question_id}
