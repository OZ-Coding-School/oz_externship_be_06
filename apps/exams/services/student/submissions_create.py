from datetime import datetime
from typing import Any, Dict, List

from django.db import transaction

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamSubmission
from apps.exams.services.answers_json import normalize_answers_json
from apps.exams.services.student.deployments_status import is_deployment_time_closed
from apps.users.models import User


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
        raise_error(ErrorMessages.INVALID_EXAM_SESSION)

    # 이미 제출됨
    if submission.answers_json:
        raise_error(ErrorMessages.SUBMISSION_ALREADY_SUBMITTED)

    # 답안 저장
    submission.answers_json = normalize_answers_json(answers)
    submission.started_at = started_at
    submission.cheating_count = cheating_count
    submission.save(update_fields=["answers_json", "started_at", "cheating_count", "updated_at"])

    return submission
