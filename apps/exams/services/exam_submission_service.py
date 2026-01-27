from datetime import datetime
from typing import Any, Dict, List

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException

from apps.exams.models import ExamSubmission
from apps.users.models import User


class InvalidSubmissionError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "유효하지 않은 시험 응시 세션입니다."


class AlreadySubmittedError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "이미 제출된 시험입니다."


#
@transaction.atomic
# 답안 저장, started_at과 cheating_count 갱신
# 시험 제출
def submit_exam(
    *,
    user: User,
    deployment_id: int,
    started_at: datetime,
    cheating_count: int,
    answers: List[Dict[str, Any]],
) -> ExamSubmission:
    """
    시험 제출 비즈니스 로직
    """
    try:
        # 동시 제출 방지
        submission = ExamSubmission.objects.select_for_update().get(
            submitter=user,
            deployment_id=deployment_id,
        )
    except ExamSubmission.DoesNotExist:
        raise InvalidSubmissionError()

    # 시험 마감 후 제출
    if timezone.now() > submission.deployment.close_at:
        raise InvalidSubmissionError()

    # 이미 제출됨
    if submission.answers_json:
        raise AlreadySubmittedError()

    # 답안 저장
    submission.answers_json = answers
    submission.started_at = started_at
    submission.cheating_count = cheating_count
    submission.save(update_fields=["answers_json", "started_at", "cheating_count"])

    return submission
