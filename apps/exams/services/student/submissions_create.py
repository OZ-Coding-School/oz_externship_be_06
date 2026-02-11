from typing import Any, Dict, List

from django.db import transaction

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamSubmission
from apps.exams.services.answers_json import normalize_answers_json
from apps.users.models import User


@transaction.atomic
# 답안 저장, started_at과 cheating_count 갱신
# 시험 제출
def submit_exam(
    *,
    user: User,
    deployment_id: int,
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
    # started_at은 take_exam 시점에 서버에서 생성된 값을 유지한다.
    # (클라이언트 전달 시간으로 받지 않음)
    submission.answers_json = normalize_answers_json(answers)
    submission.cheating_count = cheating_count
    submission.save(update_fields=["answers_json", "cheating_count", "updated_at"])

    return submission
