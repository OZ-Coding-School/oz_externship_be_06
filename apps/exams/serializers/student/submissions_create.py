from typing import Any

from rest_framework import serializers

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamQuestion


class ExamAnswerSerializer(serializers.Serializer[Any]):
    # 개별 문제 답안 구조를 정의, 검증
    question_id = serializers.IntegerField()
    type = serializers.CharField()
    submitted_answer = serializers.JSONField()  # 답의 자료형이 제각각이라 JSONField

    def validate_type(self, value: str) -> str:
        type_map = {
            "multiple_choice": ExamQuestion.TypeChoices.MULTI_SELECT,
            "single_choice": ExamQuestion.TypeChoices.SINGLE_CHOICE,
            "fill_blank": ExamQuestion.TypeChoices.FILL_IN_BLANK,
            "ordering": ExamQuestion.TypeChoices.ORDERING,
            "short_answer": ExamQuestion.TypeChoices.SHORT_ANSWER,
            "ox": ExamQuestion.TypeChoices.OX,
        }

        mapped = type_map.get(value.lower())

        if mapped is None:
            raise serializers.ValidationError(ErrorMessages.INVALID_EXAM_SESSION.value)

        # 모델에 있는 값인지 검증
        valid_internal_types = {choice for choice, _ in ExamQuestion.TypeChoices.choices}
        if mapped not in valid_internal_types:
            raise serializers.ValidationError(ErrorMessages.INVALID_EXAM_SESSION.value)

        return mapped

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["type"] == ExamQuestion.TypeChoices.SHORT_ANSWER:
            submitted_answer = attrs.get("submitted_answer")
            if not isinstance(submitted_answer, str):
                raise serializers.ValidationError({"detail": ErrorMessages.INVALID_SHORT_ANSWER_TYPE.value})
            if len(submitted_answer) > 20:
                raise serializers.ValidationError({"detail": ErrorMessages.INVALID_SHORT_ANSWER_LENGTH.value})

        return attrs


class ExamSubmissionCreateSerializer(serializers.Serializer[Any]):
    # 쪽지시험 제출 API 요청 데이터 검증용 Serializer
    deployment_id = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    cheating_count = serializers.IntegerField(default=0)
    answers = ExamAnswerSerializer(many=True)

    # answer이 비었을 때
    def validate_answers(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not value:
            raise_error(ErrorMessages.INVALID_EXAM_SESSION)
        return value


class ExamSubmissionCreateResponseSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField()
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    redirect_url = serializers.CharField()
