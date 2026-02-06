import json
from typing import Any

from django.db import transaction
from rest_framework import status

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamQuestion

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
        raise_error(ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST)

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
            raise ErrorDetailException(
                ErrorMessages.INVALID_QUESTION_REQUIRED.value,
                status.HTTP_400_BAD_REQUEST,
            )

        if "point" not in update_data or update_data.get("point") is None:
            raise ErrorDetailException(
                ErrorMessages.INVALID_QUESTION_POINT_REQUIRED.value,
                status.HTTP_400_BAD_REQUEST,
            )

        if "answer" not in update_data or update_data.get("answer") is None:
            raise ErrorDetailException(
                ErrorMessages.INVALID_QUESTION_ANSWER_REQUIRED.value,
                status.HTTP_400_BAD_REQUEST,
            )

    # 3. 유형별 정책
    # 다지선다 / 순서정렬
    if q_type in [
        ExamQuestion.TypeChoices.SINGLE_CHOICE,
        ExamQuestion.TypeChoices.MULTI_SELECT,
        ExamQuestion.TypeChoices.ORDERING,
    ]:
        if not options:
            raise ErrorDetailException(
                ErrorMessages.INVALID_QUESTION_OPTIONS_REQUIRED.value,
                status.HTTP_400_BAD_REQUEST,
            )

        # 순서정렬: 보기 최소 2개
        if q_type == ExamQuestion.TypeChoices.ORDERING and len(options) < 2:
            raise ErrorDetailException(
                ErrorMessages.INVALID_QUESTION_ORDERING_MIN_OPTIONS.value,
                status.HTTP_400_BAD_REQUEST,
            )

    # 빈칸 채우기
    if q_type == ExamQuestion.TypeChoices.FILL_IN_BLANK:
        if not prompt:
            raise ErrorDetailException(
                ErrorMessages.INVALID_QUESTION_PROMPT_REQUIRED.value,
                status.HTTP_400_BAD_REQUEST,
            )

        if blank_count is None or blank_count < 1:
            raise ErrorDetailException(
                ErrorMessages.INVALID_QUESTION_BLANK_COUNT_MIN.value,
                status.HTTP_400_BAD_REQUEST,
            )

    # 4. 총점 100점 제한 정책
    exam = instance.exam
    questions = ExamQuestion.objects.filter(exam=exam)

    current_total = sum(q.point for q in questions) - instance.point + point

    if current_total > 100:
        raise ErrorDetailException(
            ErrorMessages.QUESTION_UPDATE_CONFLICT.value,
            status.HTTP_409_CONFLICT,
        )

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
