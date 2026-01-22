import json
from typing import Any

from django.db.models import Sum

from apps.exams.models import Exam, ExamQuestion


def create_exam_question(exam_id: int, payload: dict[str, Any]) -> dict[str, Any] | dict[str, str]:
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return {"error_detail": "해당 쪽지시험 정보를 찾을 수 없습니다."}

    question_count = exam.questions.count()
    if question_count >= 20:
        return {"error_detail": "해당 쪽지시험에 등록 가능한 문제 수 또는 총 배점을 초과했습니다."}

    total_points = exam.questions.aggregate(total=Sum("point"))["total"] or 0
    point = payload["point"]
    if total_points + point > 100:
        return {"error_detail": "해당 쪽지시험에 등록 가능한 문제 수 또는 총 배점을 초과했습니다."}

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
