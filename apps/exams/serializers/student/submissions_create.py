from typing import Any

from rest_framework import serializers

from apps.exams.models import ExamQuestion


class ExamAnswerSerializer(serializers.Serializer[Any]):
    # 개별 문제 답안 구조를 정의, 검증
    question_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=ExamQuestion.TypeChoices.choices)
    submitted_answer = serializers.JSONField()  # 답의 자료형이 제각각이라 JSONField


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
