from typing import Any

from rest_framework import serializers

from apps.exams.models import ExamQuestion


class AdminExamQuestionCreateRequestSerializer(serializers.Serializer[Any]):
    """쪽지시험 문제 등록 요청 스키마."""

    TYPE_MAP = {
        "multiple_choice": ExamQuestion.TypeChoices.MULTI_SELECT,
        "fill_blank": ExamQuestion.TypeChoices.FILL_IN_BLANK,
        "ordering": ExamQuestion.TypeChoices.ORDERING,
        "short_answer": ExamQuestion.TypeChoices.SHORT_ANSWER,
        "ox": ExamQuestion.TypeChoices.OX,
    }

    type = serializers.CharField()
    question = serializers.CharField()
    prompt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    options = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    correct_answer = serializers.JSONField()
    point = serializers.IntegerField()
    explanation = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        exam_type = attrs.get("type")
        if exam_type not in self.TYPE_MAP:
            raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")

        point = attrs.get("point")
        if not isinstance(point, int) or not (1 <= point <= 10):
            raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")

        options = attrs.get("options")
        blank_count = attrs.get("blank_count")
        correct_answer = attrs.get("correct_answer")
        prompt = attrs.get("prompt")

        if exam_type in {"multiple_choice", "ordering"}:
            if not options or len(options) < 2:
                raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")
            if not isinstance(correct_answer, list) or not correct_answer:
                raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")
            if exam_type == "ordering" and len(correct_answer) != len(options):
                raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")
        elif exam_type == "fill_blank":
            if not prompt:
                raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")
            if not isinstance(blank_count, int) or blank_count < 1:
                raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")
            if not isinstance(correct_answer, list) or len(correct_answer) != blank_count:
                raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")
        elif exam_type == "short_answer":
            if not isinstance(correct_answer, str):
                raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")
        elif exam_type == "ox":
            if isinstance(correct_answer, bool):
                attrs["correct_answer"] = "O" if correct_answer else "X"
            elif correct_answer not in {"O", "X"}:
                raise serializers.ValidationError("유효하지 않은 문제 등록 데이터입니다.")

        attrs["model_type"] = self.TYPE_MAP[exam_type]
        return attrs


class AdminExamQuestionCreateResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 문제 등록 응답 스키마."""

    exam_id = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    prompt = serializers.CharField(allow_null=True, allow_blank=True)
    options = serializers.ListField(child=serializers.CharField(), allow_null=True)
    blank_count = serializers.IntegerField(allow_null=True)
    correct_answer = serializers.JSONField()
    point = serializers.IntegerField()
    explanation = serializers.CharField(allow_null=True, allow_blank=True)
