from typing import Any

from rest_framework import serializers

from apps.courses.models import Cohort


# 수강생 등록 신청
class EnrollStudentRequestSerializer(serializers.Serializer[Any]):

    cohort_id = serializers.IntegerField(required=True)

    def validate_cohort_id(self, value: int) -> int:
        if not Cohort.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 기수입니다.")
        return value


# 수강생 등록 신청 응답
class EnrollStudentResponseSerializer(serializers.Serializer[Any]):

    detail = serializers.CharField()
