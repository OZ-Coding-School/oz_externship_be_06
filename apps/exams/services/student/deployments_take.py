from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils import timezone
from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamDeployment, ExamSubmission
from apps.exams.services.student.deployments_status import (
    is_deployment_activated,
    is_deployment_opened,
    is_deployment_time_closed,
)
from apps.users.models import User


@dataclass(frozen=True)
class TakeExamResult:
    submission: ExamSubmission
    deployment: ExamDeployment


def take_exam(*, user: User, deployment_id: int) -> TakeExamResult:
    if user.role != User.Role.STUDENT:
        raise ErrorDetailException(ErrorMessages.FORBIDDEN.value, status.HTTP_403_FORBIDDEN)

    try:
        deployment = ExamDeployment.objects.select_related("exam", "exam__subject").get(id=deployment_id)
    except ExamDeployment.DoesNotExist as exc:
        raise ErrorDetailException(ErrorMessages.EXAM_NOT_FOUND.value, status.HTTP_404_NOT_FOUND) from exc

    if not is_deployment_activated(deployment):
        raise ErrorDetailException(ErrorMessages.EXAM_NOT_AVAILABLE.value, status.HTTP_400_BAD_REQUEST)

    now = timezone.now()
    if not is_deployment_opened(deployment, now=now):
        raise ErrorDetailException(ErrorMessages.EXAM_NOT_AVAILABLE.value, status.HTTP_400_BAD_REQUEST)
    if is_deployment_time_closed(deployment, now=now):
        raise ErrorDetailException(ErrorMessages.EXAM_CLOSED.value, status.HTTP_410_GONE)

    submission, _created = ExamSubmission.objects.get_or_create(
        submitter=user,
        deployment=deployment,
        defaults={
            "started_at": now,
            "cheating_count": 0,
            "answers_json": {},
            "score": 0,
            "correct_answer_count": 0,
        },
    )

    # answers_json은 JSONField(null=False)라 빈 dict로라도 보장
    if not submission.answers_json:
        submission.answers_json = {}
        submission.save(update_fields=["answers_json"])

    return TakeExamResult(submission=submission, deployment=deployment)


def build_take_exam_response(*, result: TakeExamResult) -> dict[str, Any]:
    from django.utils import timezone

    deployment = result.deployment
    exam = deployment.exam
    submission = result.submission

    # elapsed_time 계산 (초 단위)
    now = timezone.now()
    elapsed_seconds = int((now - submission.started_at).total_seconds())
    elapsed_time = max(0, elapsed_seconds)

    # questions_snapshot_json을 명세서 형식에 맞게 변환
    questions = []
    if deployment.questions_snapshot_json:
        for idx, question_data in enumerate(deployment.questions_snapshot_json, start=1):
            # 타입 매핑 (모델 타입 -> 명세서 타입)
            type_mapping = {
                "MULTI_SELECT": "multiple_choice",
                "FILL_IN_BLANK": "fill_blank",
                "ORDERING": "ordering",
                "SHORT_ANSWER": "short_answer",
                "OX": "ox",
            }
            question_type = type_mapping.get(question_data.get("type", ""), question_data.get("type", "").lower())

            question = {
                "question_id": question_data.get("question_id"),
                "number": idx,
                "type": question_type,
                "question": question_data.get("question", ""),
                "point": question_data.get("point", 0),
                "prompt": question_data.get("prompt"),
                "blank_count": question_data.get("blank_count") if question_type == "fill_blank" else None,
                "options": question_data.get("options") if question_type in ["multiple_choice", "ordering"] else None,
                "answer_input": None,  # 응시자가 입력할 답안 필드 (초기값은 None)
            }
            questions.append(question)

    return {
        "exam_id": exam.id,
        "exam_name": exam.title,
        "duration_time": deployment.duration_time,
        "elapsed_time": elapsed_time,
        "cheating_count": submission.cheating_count,
        "questions": questions,
    }
