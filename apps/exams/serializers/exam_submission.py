from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.exams.models import ExamSubmission


class ExamAnswerSerializer(serializers.Serializer[Any]):
    # 개별 문제 답안 구조를 정의, 검증
    question_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=["OX", "MULTI_SELECT", "SHORT_ANSWER", "FILL_IN_BLANK", "ORDERING"])
    submitted_answer = serializers.JSONField()  # 답의 자료형이 제각각이라 JSONField


class ExamSubmissionCreateSerializer(serializers.Serializer[Any]):
    """
    쪽지시험 제출용 Serializer
    - 응시 api에서 started_at, cheating_count를 받은 ExamSubmission 기준
    - 답안 저장
    """

    answers = ExamAnswerSerializer(many=True, allow_empty=False)  # 아예 하나도 안푼것에 대한 방지

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # 이 제출 요청이 유효한 시험에 대해 유효한 시간 안에 들어온 요청인지 검사
        submission: ExamSubmission = self.context["submission"]

        # 400에러
        if timezone.now() > submission.deployment.close_at:
            raise serializers.ValidationError("유효하지 않은 시험 응시 세션입니다.")

        return data

    # def create(self, validated_data: Dict[str, Any]) -> ExamSubmission:
    #     # 검증된 시험 제출 데이터를 기반으로 ExamSubmission을 실제로 생성하고 저장
    #     deployment: ExamDeployment = self.context["deployment"]
    #     user = self.context["request"].user  # 보안 문제로 context로 받음
    #     # 이미 응시 시작 기록이 있는지 확인
    #     submission = ExamSubmission.objects.get_or_create(
    #         submitter=user,
    #         deployment=deployment,
    #         started_at=validated_data["started_at"],
    #         cheating_count=validated_data["cheating_count"],
    #         answers_json=validated_data["answers"],
    #     )
    #
    #     return submission

    def save(self, **kwargs: Any) -> ExamSubmission:
        submission: ExamSubmission = self.context["submission"]

        submission.answers_json = self.validated_data["answers"]
        submission.cheating_count = self.validated_data.get("cheating_count", submission.cheating_count)

        submission.save(update_fields=["answers_json", "cheating_count"])

        return submission


class ExamSubmissionCreateResponseSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField()
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    redirect_url = serializers.CharField()
