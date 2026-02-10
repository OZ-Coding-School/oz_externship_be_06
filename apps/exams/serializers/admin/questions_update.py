import json
from typing import Any, Dict, cast

from rest_framework import serializers

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamQuestion


class AdminExamQuestionUpdateRequestSerializer(serializers.ModelSerializer[ExamQuestion]):
    type = serializers.CharField(required=False)
    question = serializers.CharField(
        max_length=255,
        required=False,
    )
    prompt = serializers.CharField(allow_blank=True, required=False)
    options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        allow_empty=True,
        source="options_json",
    )
    blank_count = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    correct_answer = serializers.JSONField(required=False, source="answer")
    point = serializers.IntegerField(min_value=1, max_value=10, required=False)
    explanation = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ExamQuestion
        fields = [
            "type",
            "question",
            "prompt",
            "options",
            "blank_count",
            "correct_answer",
            "point",
            "explanation",
        ]

    def validate_type(self, value: str) -> str:
        type_map = {
            "multiple_choice": ExamQuestion.TypeChoices.MULTI_SELECT,
            "single_choice": ExamQuestion.TypeChoices.SINGLE_CHOICE,
            "fill_blank": ExamQuestion.TypeChoices.FILL_IN_BLANK,
            "ordering": ExamQuestion.TypeChoices.ORDERING,
            "short_answer": ExamQuestion.TypeChoices.SHORT_ANSWER,
            "ox": ExamQuestion.TypeChoices.OX,
        }

        # 프론트 요청이 문자열인지 검증
        if not isinstance(value, str):
            raise_error(ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST)

        mapped = type_map.get(value.lower())
        if mapped is None:
            raise_error(ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST)

        return mapped

    # list -> json 변환
    def to_internal_value(self, data: Any) -> Dict[str, Any]:
        ret = cast(Dict[str, Any], super().to_internal_value(data))

        if "options_json" in ret and isinstance(ret["options_json"], list):
            ret["options_json"] = json.dumps(ret["options_json"])

        return ret


class AdminExamQuestionUpdateResponseSerializer(serializers.ModelSerializer[ExamQuestion]):
    question_id = serializers.IntegerField(source="id")
    options = serializers.SerializerMethodField()
    correct_answer = serializers.JSONField(source="answer")

    class Meta:
        model = ExamQuestion
        fields = [
            "question_id",
            "type",
            "question",
            "prompt",
            "options",
            "blank_count",
            "correct_answer",
            "point",
            "explanation",
        ]

    # json -> list 변환
    def get_options(self, obj: ExamQuestion) -> list[Any]:
        if obj.options_json:
            try:
                return cast(list[Any], json.loads(obj.options_json))
            except Exception:
                return []
        return []
