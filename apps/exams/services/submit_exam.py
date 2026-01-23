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
        q_type = q.get("type", "")
        sub = by_id[qid]
        val = sub.get("submitted_answer") or sub.get("answer_input") or ""
        if ans is None:
            continue

        # 타입별 채점 로직
        ok = False

        # OX 문제
        if q_type == "OX":
            ok = str(val).strip().upper() == str(ans).strip().upper()

        # 주관식 단답형
        elif q_type == "SHORT_ANSWER":
            ok = str(val).strip().lower() == str(ans).strip().lower()

        # 다지선다 (MULTI_SELECT)
        elif q_type == "MULTI_SELECT":
            # 정답이 리스트인 경우
            if isinstance(ans, list):
                # 제출 답안도 리스트로 변환
                if isinstance(val, (str, int)):
                    val = [val]
                if isinstance(val, list):
                    # 집합으로 변환하여 순서 무관 비교
                    ok = set(val) == set(ans)
                else:
                    ok = False
            # 정답이 단일 값인 경우
            else:
                # 제출 답안이 리스트인 경우
                if isinstance(val, list):
                    ok = ans in val
                # 제출 답안이 단일 값인 경우
                else:
                    ok = str(val).strip() == str(ans).strip()

        # 순서 정렬 (ORDERING)
        elif q_type == "ORDERING":
            if isinstance(ans, list):
                if isinstance(val, list):
                    # 순서가 중요하므로 리스트 비교
                    ok = list(val) == list(ans)
                else:
                    ok = False
            else:
                # 정답이 단일 값인 경우 리스트로 변환
                if isinstance(val, list):
                    ok = len(val) == 1 and val[0] == ans
                else:
                    ok = str(val).strip() == str(ans).strip()

        # 빈칸 채우기 (FILL_IN_BLANK)
        elif q_type == "FILL_IN_BLANK":
            # 정답이 리스트인 경우
            if isinstance(ans, list):
                if isinstance(val, list):
                    # 각 빈칸을 순서대로 비교
                    if len(val) == len(ans):
                        ok = all(str(v).strip().lower() == str(a).strip().lower() for v, a in zip(val, ans))
                    else:
                        ok = False
                else:
                    # 제출 답안이 단일 값인 경우, 정답이 1개인 경우만 비교
                    ok = len(ans) == 1 and str(val).strip().lower() == str(ans[0]).strip().lower()
            # 정답이 단일 값인 경우
            else:
                if isinstance(val, list):
                    # 제출 답안이 리스트인 경우, 정답이 1개인 경우만 비교
                    ok = len(val) == 1 and str(val[0]).strip().lower() == str(ans).strip().lower()
                else:
                    ok = str(val).strip().lower() == str(ans).strip().lower()

        # 기본값: 단순 문자열 비교
        else:
            if isinstance(ans, list):
                # 정답이 리스트인 경우
                if isinstance(val, list):
                    ok = set(val) == set(ans)
                else:
                    ok = val in ans
            else:
                # 정답이 단일 값인 경우
                if isinstance(val, list):
                    ok = ans in val
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

    # 이미 제출된 시험 체크
    if submission.answers_json is not None and len(submission.answers_json) > 0:
        raise ValidationError({"error_detail": "이미 제출된 시험입니다."})

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
