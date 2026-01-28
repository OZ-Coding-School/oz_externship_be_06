from typing import Any

from rest_framework import serializers


# 점수 응답 시리얼라이저
class AdminStudentScoreSerializer(serializers.Serializer[Any]):

    subject = serializers.CharField(help_text="과목명")
    score = serializers.IntegerField(help_text="평균 점수")
