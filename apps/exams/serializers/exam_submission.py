from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.exams.models import ExamQuestion, ExamSubmission


class ExamAnswerSerializer(serializers.Serializer[Any]):
    # 개별 문제 답안 구조를 정의, 검증
    question_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=ExamQuestion.TypeChoices.choices)
    submitted_answer = serializers.JSONField()  # 답의 자료형이 제각각이라 JSONField


class ExamSubmissionCreateSerializer(serializers.Serializer[Any]):
    """
    쪽지시험 제출용 Serializer
    - 응시 api에서 started_at, cheating_count를 받은 ExamSubmission 기준
    - 답안 저장
    """

    deployment_id = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    cheating_count = serializers.IntegerField(default=0)
    answers = ExamAnswerSerializer(many=True, allow_empty=False)  # 아예 하나도 안푼것에 대한 방지

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # 이 제출 요청이 유효한 시험에 대해 유효한 시간 안에 들어온 요청인지 검사
        submission: ExamSubmission = self.context["submission"]

        # 400에러
        if timezone.now() > submission.deployment.close_at:
            raise serializers.ValidationError("유효하지 않은 시험 응시 세션입니다.")

        return data

    def save(self, **kwargs: Any) -> ExamSubmission:
        submission: ExamSubmission = self.context["submission"]

        submission.answers_json = self.validated_data["answers"]
        submission.started_at = self.validated_data.get("started_at", submission.started_at)
        submission.cheating_count = self.validated_data.get("cheating_count", submission.cheating_count)

        submission.save(update_fields=["answers_json", "started_at", "cheating_count"])

        return submission


class ExamSubmissionCreateResponseSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField()
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    redirect_url = serializers.CharField()
