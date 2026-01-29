from typing import Any

from rest_framework import serializers

from apps.exams.constants import ErrorMessages
from apps.exams.models import ExamQuestion


class ExamAnswerSerializer(serializers.Serializer[Any]):
    # 개별 문제 답안 구조를 정의, 검증
    question_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=ExamQuestion.TypeChoices.choices)
    submitted_answer = serializers.JSONField()  # 답의 자료형이 제각각이라 JSONField

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
    answers = ExamAnswerSerializer(many=True, allow_empty=False)  # 아예 하나도 안푼것에 대한 방지


class ExamSubmissionCreateResponseSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField()
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    redirect_url = serializers.CharField()
