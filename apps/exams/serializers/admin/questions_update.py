import json
from typing import Any
from rest_framework import serializers

from apps.exams.models import ExamQuestion
from apps.exams.constants import ErrorMessages


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
    correct_answer = serializers.JSONField(required=False)
    point = serializers.IntegerField(min_value=1, required=False)
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
    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if "options_json" in ret and isinstance(ret["options_json"], list):
            ret["options_json"] = json.dumps(ret["options_json"])
        return ret

    # 최소 한 필드 이상은 들어왔는지 확인
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if not data:
            raise serializers.ValidationError(
                ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST.value
            )
        return data

        # 여긴 서비스에 넣을것
        # 문제 유형에 따라 options / blank_count 필수 여부 검사
        # q_type = data.get("type") or getattr(self.instance, "type", None)
        #
        # if q_type in [ExamQuestion.TypeChoices.MULTIPLE, ExamQuestion.TypeChoices.ORDERING]:
        #     if not data.get("options") and not getattr(self.instance, "options", None):
        #         raise serializers.ValidationError(
        #             "선택형 또는 순서형 문제는 options가 필요합니다."
        #         )
        #
        # if q_type == ExamQuestion.TypeChoices.FILL:
        #     if data.get("blank_count") is None and getattr(self.instance, "blank_count", None) is None:
        #         raise serializers.ValidationError(
        #             "빈칸 문제는 blank_count가 필요합니다."
        #         )
        #
        # return data

class AdminExamQuestionUpdateResponseSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source="id")

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
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.options_json:
            try:
                ret["options"] = json.loads(instance.options_json)
            except Exception:
                ret["options"] = []
        else:
            ret["options"] = []
        return ret
