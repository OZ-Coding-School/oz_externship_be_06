from __future__ import annotations

from typing import Any

from rest_framework import serializers


class AnswerItemSerializer(serializers.Serializer[Any]):
    question_id = serializers.IntegerField(required=True)
    type = serializers.CharField(required=False, allow_blank=True)
    submitted_answer = serializers.JSONField(required=False, allow_null=True)
    answer_input = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SubmitExamRequestSerializer(serializers.Serializer[Any]):
    deployment_id = serializers.IntegerField(required=True)
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    answers = AnswerItemSerializer(many=True, required=True)


class SubmitExamResponseSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField(help_text="제출 ID")
    correct_answer_count = serializers.IntegerField(help_text="정답 개수")
    score = serializers.IntegerField(help_text="획득 점수")
    redirect_url = serializers.CharField(help_text="결과 페이지 URL")
