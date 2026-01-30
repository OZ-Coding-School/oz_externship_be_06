import json
from typing import Any
from django.db import transaction

from apps.exams.models import ExamQuestion
from apps.exams.constants import ErrorMessages

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

    # 1. 최종 상태 계산 (요청 + 기존값)
    q_type = update_data.get("type", instance.type)
    question = update_data.get("question", instance.question)
    prompt = update_data.get("prompt", instance.prompt)
    options_json = update_data.get("options_json", instance.options_json)
    blank_count = update_data.get("blank_count", instance.blank_count)
    correct_answer = update_data.get("correct_answer", instance.correct_answer)
    point = update_data.get("point", instance.point)

    # 2. 공통 필수 정책
    if not question:
        raise BusinessRuleError("문제(question)는 필수입니다.")

    if point is None:
        raise BusinessRuleError("배점(point)은 필수입니다.")

    if correct_answer in [None, ""]:
        raise BusinessRuleError("정답(correct_answer)은 필수입니다.")

    # 3. 유형별 정책
    # 다지선다 / 순서정렬
    if q_type in [
        ExamQuestion.TypeChoices.MULTIPLE,
        ExamQuestion.TypeChoices.ORDERING,
    ]:
        if not options_json:
            raise BusinessRuleError("선택형/순서형 문제는 options가 필요합니다.")

        try:
            options = (
                json.loads(options_json)
                if isinstance(options_json, str)
                else options_json
            )
        except Exception:
            raise BusinessRuleError("options 형식이 올바르지 않습니다.")

        # 순서정렬: 보기 최소 2개
        if q_type == ExamQuestion.TypeChoices.ORDERING and len(options) < 2:
            raise BusinessRuleError(
                "순서 정렬형 문제는 보기 2개 이상이 필요합니다."
            )

    # 빈칸 채우기
    if q_type == ExamQuestion.TypeChoices.FILL:
        if not prompt:
            raise BusinessRuleError(
                "빈칸 채우기 문제는 지문(prompt)이 필요합니다."
            )

        if blank_count is None or blank_count < 1:
            raise BusinessRuleError(
                "빈칸 채우기 문제는 blank_count가 1 이상이어야 합니다."
            )

    # 단답형 / OX 는 공통 필수만으로 충분

    # 4. 총점 100점 제한 정책
    deployment = instance.deployment
    questions = ExamQuestion.objects.filter(deployment=deployment)

    current_total = sum(q.point for q in questions)

    # 기존 문제 point 제거
    current_total -= instance.point

    # 새 point 반영
    current_total += point

    if current_total > 100:
        raise ConflictRuleError(
            ErrorMessages.EXAM_QUESTION_SCORE_OVER.value
        )

    # 5. 실제 업데이트 반영
    for field, value in update_data.items():
        setattr(instance, field, value)

    instance.save()

    return instance