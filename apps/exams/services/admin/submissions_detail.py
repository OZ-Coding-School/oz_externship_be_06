from __future__ import annotations

from typing import Any

from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamSubmission
from apps.exams.services.answers_json import normalize_answers_json


def get_admin_submission_detail(submission_id: int) -> dict[str, Any]:
    submission = (
        ExamSubmission.objects.select_related(
            "submitter",
            "deployment__exam__subject",
            "deployment__cohort__course",
        )
        .filter(id=submission_id)
        .first()
    )
    if submission is None:
        raise ErrorDetailException(ErrorMessages.SUBMISSION_DETAIL_NOT_FOUND.value, status.HTTP_404_NOT_FOUND)

    deployment = submission.deployment
    exam = deployment.exam
    cohort = deployment.cohort
    course = cohort.course

    questions_snapshot = deployment.questions_snapshot_json or []
    submitted_map = _build_submitted_map(submission.answers_json)

    questions: list[dict[str, Any]] = []
    for idx, question_data in enumerate(questions_snapshot, start=1):
        raw_question_id = question_data.get("question_id")
        try:
            question_id = int(raw_question_id)
        except (TypeError, ValueError):
            continue

        submitted_answer = submitted_map.get(question_id)
        answer = question_data.get("answer")

        questions.append(
            {
                "id": question_id,
                "number": idx,
                "type": _map_question_type(question_data.get("type")),
                "question": question_data.get("question", ""),
                "prompt": question_data.get("prompt"),
                "options": question_data.get("options"),
                "point": question_data.get("point", 0),
                "answer": answer,
                "submitted_answer": submitted_answer,
                "is_correct": _is_correct(answer, submitted_answer),
                "explanation": question_data.get("explanation", ""),
            }
        )

    elapsed_time = int((submission.created_at - submission.started_at).total_seconds() // 60)

    return {
        "exam": {
            "exam_title": exam.title,
            "subject_name": exam.subject.title,
            "duration_time": deployment.duration_time,
            "open_at": deployment.open_at,
            "close_at": deployment.close_at,
        },
        "student": {
            "nickname": submission.submitter.nickname,
            "name": submission.submitter.name,
            "course_name": course.name,
            "cohort_number": cohort.number,
        },
        "result": {
            "score": submission.score,
            "correct_answer_count": submission.correct_answer_count,
            "total_question_count": len(questions_snapshot),
            "cheating_count": submission.cheating_count,
            "elapsed_time": elapsed_time,
        },
        "questions": questions,
    }


def _build_submitted_map(raw: Any) -> dict[int, Any]:
    normalized = normalize_answers_json(raw)
    submitted_map: dict[int, Any] = {}
    for item in normalized:
        qid = item.get("question_id")
        if qid is None:
            continue
        try:
            qid_int = int(qid)
        except (TypeError, ValueError):
            continue
        submitted_map[qid_int] = item.get("submitted_answer")
    return submitted_map


def _normalize_answer(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _is_correct(answer: Any, submitted_answer: Any) -> bool:
    answer_norm = sorted(_normalize_answer(answer))
    submitted_norm = sorted(_normalize_answer(submitted_answer))
    return answer_norm == submitted_norm


def _map_question_type(raw_type: Any) -> str:
    type_mapping = {
        "MULTI_SELECT": "multiple_choice",
        "MULTIPLE_CHOICE": "multiple_choice",
        "SINGLE_SELECT": "single_choice",
        "SINGLE_CHOICE": "single_choice",
        "FILL_IN_BLANK": "fill_blank",
        "ORDERING": "ordering",
        "SHORT_ANSWER": "short_answer",
        "OX": "ox",
    }
    if not raw_type:
        return ""
    return type_mapping.get(str(raw_type), str(raw_type).lower())
