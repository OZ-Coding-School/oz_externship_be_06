import json
from typing import Any

from django.db import transaction
from django.db.models import Count, Sum

from apps.exams.models import Exam, ExamQuestion


class ExamNotFoundError(Exception):
    """쪽지시험 정보가 없을 때 발생."""


class ExamQuestionLimitError(Exception):
    """문항 수/총점 제한을 초과했을 때 발생."""


def create_exam_question(exam_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    with transaction.atomic():
        try:
            exam = Exam.objects.select_for_update().get(id=exam_id)
        except Exam.DoesNotExist as exc:
            raise ExamNotFoundError from exc

        stats = exam.questions.aggregate(count=Count("id"), total=Sum("point"))
        question_count = stats["count"] or 0
        total_points = stats["total"] or 0
        if question_count >= 20:
            raise ExamQuestionLimitError
        point = payload["point"]
        if total_points + point > 100:
            raise ExamQuestionLimitError

        options = payload.get("options")
        blank_count = payload.get("blank_count")
        prompt = payload.get("prompt")
        explanation = payload.get("explanation") or ""

        exam_question = ExamQuestion.objects.create(
            exam=exam,
            type=payload["model_type"],
            question=payload["question"],
            prompt=prompt,
            blank_count=blank_count or 0,
            options_json=json.dumps(options) if options is not None else None,
            answer=payload["correct_answer"],
            point=point,
            explanation=explanation,
        )

    return {
        "exam_id": exam.id,
        "type": payload["type"],
        "question": exam_question.question,
        "prompt": prompt,
        "options": options if options is not None else None,
        "blank_count": blank_count if blank_count is not None else 0,
        "correct_answer": payload["correct_answer"],
        "point": exam_question.point,
        "explanation": explanation,
    }
