from django.utils import timezone
from rest_framework import serializers
from typing import Any, Dict

from apps.exams.models import ExamDeployment


class ExamSubmitSerializer(serializers.Serializer):  # type: ignore
    answers = serializers.DictField(child=serializers.JSONField())

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        deployment = self.context.get("deployment")
        if deployment is None:
            raise serializers.ValidationError("시험 정보가 없습니다.")

        now = timezone.now()

        if deployment.status != ExamDeployment.StatusChoices.ACTIVATED:
            raise serializers.ValidationError("비활성화된 시험입니다.")

        if not (deployment.open_at <= now <= deployment.close_at):
            raise serializers.ValidationError("시험 시간이 아닙니다.")

        return data
