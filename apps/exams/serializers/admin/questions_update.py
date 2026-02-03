import json
from typing import Any, Dict, cast
from rest_framework import serializers

from apps.exams.models import ExamQuestion

class AdminExamQuestionUpdateRequestSerializer(serializers.ModelSerializer[ExamQuestion]):
    type = serializers.ChoiceField(choices=ExamQuestion.TypeChoices.choices, required=False)
    question = serializers.CharField(max_length=255, required=False,)
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

    # list -> json 변환
    def to_internal_value(self, data: Any) -> Dict[str, Any]:
        ret = cast(Dict[str, Any], super().to_internal_value(data))

        if "options_json" in ret and isinstance(ret["options_json"], list):
            ret["options_json"] = json.dumps(ret["options_json"])

        if "correct_answer" in ret:
            ret["answer"] = ret.pop("correct_answer")
        return ret

    # 최소 한 필드 이상은 들어왔는지 확인
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        return data

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
