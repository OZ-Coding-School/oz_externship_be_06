from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.exams.models import ExamDeployment, ExamSubmission
from apps.users.models import User


@dataclass(frozen=True)
class TakeExamResult:
    submission: ExamSubmission
    deployment: ExamDeployment


def take_exam(*, user: User, access_code: str) -> TakeExamResult:
    if user.role != User.Role.STUDENT:
        raise ValidationError({"detail": "수강생 권한이 필요합니다."})

    try:
        deployment = ExamDeployment.objects.select_related("exam", "exam__subject").get(access_code=access_code)
    except ExamDeployment.DoesNotExist as exc:
        raise ValidationError({"detail": "참가 코드가 올바르지 않습니다."}) from exc

    if deployment.status != ExamDeployment.StatusChoices.ACTIVATED:
        raise ValidationError({"detail": "현재 응시할 수 없는 시험입니다."})

    now = timezone.now()
    if now < deployment.open_at or now > deployment.close_at:
        raise ValidationError({"detail": "응시 가능 시간이 아닙니다."})

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
    deployment = result.deployment
    exam = deployment.exam
    subject = exam.subject

    return {
        "submission_id": result.submission.id,
        "started_at": result.submission.started_at,
        "deployment_id": deployment.id,
        "duration_time": deployment.duration_time,
        "open_at": deployment.open_at,
        "close_at": deployment.close_at,
        "questions_snapshot_json": deployment.questions_snapshot_json,
        "exam_id": exam.id,
        "exam_title": exam.title,
        "exam_thumbnail_img_url": exam.thumbnail_img_url,
        "subject_id": subject.id,
    }
