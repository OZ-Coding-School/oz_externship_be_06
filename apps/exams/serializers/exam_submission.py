from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.exams.models import ExamDeployment, ExamSubmission


class ExamAnswerSerializer(serializers.Serializer[Any]):
    # 개별 문제 답안 구조를 정의, 검증
    question_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=["OX", "MULTI_SELECT", "SHORT_ANSWER", "FILL_IN_BLANK", "ORDERING"])
    submitted_answer = serializers.JSONField()  # 답의 자료형이 제각각이라 JSONField


class ExamSubmissionCreateSerializer(serializers.Serializer[Any]):
    """
    쪽지시험 제출용 Serializer
    - request body 전체 검증
    - 채점은 X
    """

    answers = ExamAnswerSerializer(many=True, allow_empty=False)  # 아예 하나도 안푼것에 대한 방지

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # 이 제출 요청이 유효한 시험에 대해 유효한 시간 안에 들어온 요청인지 검사
        deployment: ExamDeployment | None = self.context.get("deployment")
        now = timezone.now()

        if deployment is None:
            raise serializers.ValidationError("해당 시험 정보를 찾을 수 없습니다.")

        if now > deployment.close_at:
            raise serializers.ValidationError("유효하지 않은 시험 응시 세션입니다.")

        return data

    def create(self, validated_data: Dict[str, Any]) -> ExamSubmission:
        # 검증된 시험 제출 데이터를 기반으로 ExamSubmission을 실제로 생성하고 저장
        deployment: ExamDeployment = self.context["deployment"]
        user = self.context["request"].user  # 보안 문제로 context로 받음

        # 중복 제출 방지
        # 제출자가 현재 로그인한 유저 & 시험이 지금 활성화된 레코드 찾고 제출한 기록이 1개라도 있으면 raise
        if ExamSubmission.objects.filter(
            submitter=user,
            deployment=deployment,
        ).exists():
            raise serializers.ValidationError("이미 제출된 시험입니다.")

        # 이미 응시 시작 기록이 있는지 확인
        submission, created = ExamSubmission.objects.get_or_create(
            submitter=user,
            deployment=deployment,
            defaults={
                "started_at": timezone.now(),  # 응시 시작 기록 없으면 생성
                "answers_json": validated_data["answers"],
            },
        )

        return submission


class ExamSubmissionCreateResponseSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField()
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    redirect_url = serializers.CharField()
