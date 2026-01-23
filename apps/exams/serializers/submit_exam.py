from __future__ import annotations

from rest_framework import serializers


class AnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=True)
    type = serializers.CharField(required=False, allow_blank=True)
    submitted_answer = serializers.JSONField(required=False, allow_null=True)
    answer_input = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SubmitExamRequestSerializer(serializers.Serializer):
    deployment_id = serializers.IntegerField(required=True)
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    answers = AnswerItemSerializer(many=True, required=True)
