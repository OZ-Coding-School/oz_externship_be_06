import json
from typing import Any
from uuid import uuid4

from django.db import transaction

from apps.core.utils.base62 import Base62
from apps.courses.models.cohorts import Cohort
from apps.exams.models import Exam, ExamDeployment, ExamQuestion


class ExamDeploymentNotFoundError(Exception):
    """배포 대상 정보를 찾지 못했을 때 발생."""


class ExamDeploymentConflictError(Exception):
    """배포 생성 중 중복/충돌 발생 시."""


def _generate_access_code() -> str:
    for _ in range(5):
        code = Base62.uuid_encode(uuid4())
        if not ExamDeployment.objects.filter(access_code=code).exists():
            return code
    return Base62.uuid_encode(uuid4(), length=8)


def _build_question_snapshot(exam: Exam) -> list[dict[str, Any]]:
    snapshot: list[dict[str, Any]] = []
    questions = ExamQuestion.objects.filter(exam=exam).order_by("id")
    for question in questions:
        options = None
        if question.options_json:
            try:
                options = json.loads(question.options_json)
            except json.JSONDecodeError:
                options = None

        snapshot.append(
            {
                "question_id": question.id,
                "type": question.type,
                "question": question.question,
                "prompt": question.prompt,
                "blank_count": question.blank_count,
                "options": options,
                "answer": question.answer,
                "point": question.point,
            }
        )
    return snapshot


def create_exam_deployment(payload: dict[str, Any]) -> int:
    exam_id = payload["exam_id"]
    cohort_id = payload["cohort_id"]
    open_at = payload["open_at"]
    close_at = payload["close_at"]
    duration_time = payload["duration_time"]

    exam = Exam.objects.filter(id=exam_id).first()
    cohort = Cohort.objects.filter(id=cohort_id).first()
    if not exam or not cohort:
        raise ExamDeploymentNotFoundError

    with transaction.atomic():
        if ExamDeployment.objects.filter(
            exam_id=exam_id,
            cohort_id=cohort_id,
            open_at=open_at,
            close_at=close_at,
        ).exists():
            raise ExamDeploymentConflictError

        snapshot = _build_question_snapshot(exam)
        access_code = _generate_access_code()
        deployment = ExamDeployment.objects.create(
            exam=exam,
            cohort=cohort,
            duration_time=duration_time,
            access_code=access_code,
            open_at=open_at,
            close_at=close_at,
            questions_snapshot_json=snapshot,
        )

    return deployment.id
