from __future__ import annotations

from rest_framework import serializers


class CheckCodeRequestSerializer(serializers.Serializer):
    code = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="참가코드(Base62 인코딩된 값)",
    )


class TakeExamRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=64,
        help_text="참가코드(Base62 인코딩된 값)",
    )


class QuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    number = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    point = serializers.IntegerField()
    prompt = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    blank_count = serializers.IntegerField(allow_null=True, required=False)
    options = serializers.ListField(child=serializers.CharField(), allow_null=True, required=False)
    answer_input = serializers.CharField(allow_null=True, required=False)


class TakeExamResponseSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    exam_name = serializers.CharField()
    duration_time = serializers.IntegerField()
    elapsed_time = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    questions = QuestionSerializer(many=True)
