from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.exams.models import ExamDeployment, ExamSubmission
from apps.users.models import User


def _grade_answers(
    snapshot: list[dict[str, Any]],
    answers: list[dict[str, Any]],
) -> tuple[int, int]:
    """채점 후 (correct_count, score_earned) 반환."""
    by_id = {int(a["question_id"]): a for a in answers if "question_id" in a}
    correct = 0
    score_earned = 0
    for q in snapshot or []:
        qid = q.get("id")
        if qid is None:
            continue
        qid = int(qid) if isinstance(qid, (int, float)) else None
        if qid is None or qid not in by_id:
            continue
        point = int(q.get("point") or 0)
        ans = q.get("answer")
        sub = by_id[qid]
        val = sub.get("submitted_answer") or sub.get("answer_input") or ""
        if ans is None:
            continue
        if isinstance(ans, list):
            ok = val in ans or (isinstance(val, list) and set(val) == set(ans))
        else:
            ok = str(val).strip() == str(ans).strip()
        if ok:
            correct += 1
            score_earned += point
    return correct, score_earned


def submit_exam(
    *,
    user: User,
    deployment_id: int,
    started_at: str | None,
    answers: list[dict[str, Any]],
) -> ExamSubmission:
    if user.role != User.Role.STUDENT:
        raise ValidationError({"detail": "수강생 권한이 필요합니다."})

    try:
        deployment = ExamDeployment.objects.get(id=deployment_id)
    except ExamDeployment.DoesNotExist as exc:
        raise ValidationError({"detail": "해당 시험 정보를 찾을 수 없습니다."}) from exc

    now = timezone.now()
    if now > deployment.close_at:
        raise ValidationError({"detail": "시험이 이미 종료되었습니다."})

    submission = ExamSubmission.objects.filter(
        submitter=user,
        deployment=deployment,
    ).first()

    if not submission:
        raise ValidationError({"error_detail": "유효하지 않은 시험 응시 세션입니다."})

    answers_json = [a for a in answers]
    snapshot = deployment.questions_snapshot_json
    if not isinstance(snapshot, list):
        snapshot = []
    correct_count, score_earned = _grade_answers(snapshot, answers_json)

    submission.answers_json = answers_json
    submission.score = score_earned
    submission.correct_answer_count = correct_count
    submission.save(update_fields=["answers_json", "score", "correct_answer_count", "updated_at"])

    return submission
