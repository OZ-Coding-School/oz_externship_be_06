import json
from typing import Any

from django.db import transaction
from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamQuestion


class BusinessRuleError(Exception):
    # 일반 비즈니스 규칙 위반 -> 400
    pass


class ConflictRuleError(Exception):
    # 리소스 충돌 / 상태 충돌 → 409
    pass


@transaction.atomic
def update_exam_question(
    *,
    instance: ExamQuestion,
    update_data: dict[str, Any],
) -> ExamQuestion:
    """
    쪽지시험 문제 수정 Service

    책임:
    - 유형별 필수 필드 정책 검증
    - options / blank_count 정책 검증
    - 총점 100점 제한 검증
    - 실제 update 수행
    """

    # 빈 payload 체크
    if not update_data:
        raise ErrorDetailException(
            detail=ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST.value,
            http_status=status.HTTP_400_BAD_REQUEST,
        )

    # 1. 최종 상태 계산 (요청 + 기존값)
    q_type = update_data.get("type", instance.type)
    question = update_data.get("question", instance.question)
    prompt = update_data.get("prompt", instance.prompt)

    options_json = update_data.get("options_json")
    if options_json is not None:
        options = json.loads(options_json)
    else:
        options = json.loads(instance.options_json) if instance.options_json else []

    blank_count = update_data.get("blank_count", instance.blank_count)
    answer = update_data.get("answer", instance.answer)
    point = update_data.get("point", instance.point)

    is_type_changed = "type" in update_data and update_data["type"] != instance.type

    # 2. 타입 변경 시 공통 필수 필드 재입력 강제
    if is_type_changed:
        if "question" not in update_data or not update_data.get("question"):
            raise BusinessRuleError("문제(question)는 필수입니다.")

        if "point" not in update_data or update_data.get("point") is None:
            raise BusinessRuleError("배점(point)은 필수입니다.")

        if "answer" not in update_data or update_data.get("answer") is None:
            raise BusinessRuleError("정답(answer)은 필수입니다.")

    # 3. 유형별 정책
    # 다지선다 / 순서정렬
    if q_type in [
        ExamQuestion.TypeChoices.SINGLE_CHOICE,
        ExamQuestion.TypeChoices.MULTI_SELECT,
        ExamQuestion.TypeChoices.ORDERING,
    ]:
        if not options:
            raise BusinessRuleError("객관식/순서정렬 문제는 options가 필요합니다.")

        # 순서정렬: 보기 최소 2개
        if q_type == ExamQuestion.TypeChoices.ORDERING and len(options) < 2:
            raise BusinessRuleError("순서 정렬 문제는 보기 2개 이상이 필요합니다.")

    # 빈칸 채우기
    if q_type == ExamQuestion.TypeChoices.FILL_IN_BLANK:
        if not prompt:
            raise BusinessRuleError("빈칸 채우기 문제는 지문(prompt)이 필요합니다.")

        if blank_count is None or blank_count < 1:
            raise BusinessRuleError("빈칸 채우기 문제는 blank_count가 1 이상이어야 합니다.")

    # 4. 총점 100점 제한 정책
    exam = instance.exam
    questions = ExamQuestion.objects.filter(exam=exam)

    current_total = sum(q.point for q in questions) - instance.point + point

    if current_total > 100:
        raise ConflictRuleError(ErrorMessages.QUESTION_UPDATE_CONFLICT.value)

    instance.type = q_type
    instance.question = question
    instance.prompt = prompt
    instance.blank_count = blank_count
    instance.answer = answer
    instance.point = point
    instance.explanation = update_data.get("explanation", instance.explanation)
    instance.options_json = json.dumps(options)

    instance.save()

    return instance
