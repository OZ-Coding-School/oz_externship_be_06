from django.db import transaction

from apps.exams.models import ExamQuestion


class ExamQuestionDeleteNotFoundError(Exception):
    """삭제 대상 문제를 찾지 못했을 때 발생."""


class ExamQuestionDeleteConflictError(Exception):
    """문제 삭제 중 충돌 발생 시."""


def delete_exam_question(question_id: int) -> dict[str, int]:
    question = ExamQuestion.objects.filter(id=question_id).first()
    if not question:
        raise ExamQuestionDeleteNotFoundError

    try:
        with transaction.atomic():
            question.delete()
    except Exception as exc:
        raise ExamQuestionDeleteConflictError from exc

    return {"exam_id": question.exam_id, "question_id": question_id}
