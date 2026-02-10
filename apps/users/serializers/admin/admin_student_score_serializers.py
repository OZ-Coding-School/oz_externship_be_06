from typing import Any

from rest_framework import serializers


class AdminStudentScoreSerializer(serializers.Serializer[Any]):
    """
    어드민 페이지 학생 과목별 평균 점수 응답 시리얼라이저

    mypy [arg-type] 에러 해결을 위해 제네릭을 Any로 설정하여
    단일 dict와 list[dict] 입력을 모두 허용합니다.
    """

    subject = serializers.CharField(help_text="과목명", max_length=100)
    score = serializers.IntegerField(help_text="평균 점수", min_value=0, max_value=100)

    class Meta:
        ref_name = "AdminStudentScoreResponse"
