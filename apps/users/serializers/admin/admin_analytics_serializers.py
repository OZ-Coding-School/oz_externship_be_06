from typing import Any, Dict, List

from rest_framework import serializers

from apps.users.models import Withdrawal

# --- Base Serializers (중복 코드 제거) ---


class BaseTrendsRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    """추세 분석 요청 공통 시리얼라이저"""

    INTERVAL_CHOICES = [
        ("monthly", "월별"),
        ("yearly", "연별"),
    ]

    interval = serializers.ChoiceField(choices=INTERVAL_CHOICES, required=True)
    year = serializers.IntegerField(required=False, min_value=2000, max_value=2100, allow_null=True)


class TrendsItemSerializer(serializers.Serializer[Dict[str, Any]]):
    """추세 분석 개별 항목 시리얼라이저"""

    period = serializers.CharField(help_text="기간 (YYYY-MM 또는 YYYY)")
    count = serializers.IntegerField(min_value=0)


class BaseTrendsResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    """추세 분석 응답 공통 시리얼라이저"""

    interval = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total = serializers.IntegerField(min_value=0)
    items = TrendsItemSerializer(many=True)


# --- 구현체 Serializers ---


class SignupTrendsRequestSerializer(BaseTrendsRequestSerializer):
    """회원가입 추세 분석 요청"""

    pass


class SignupTrendsResponseSerializer(BaseTrendsResponseSerializer):
    """회원가입 추세 분석 응답"""

    pass


class WithdrawalTrendsRequestSerializer(BaseTrendsRequestSerializer):
    """회원탈퇴 추세 분석 요청"""

    # 탈퇴 분석은 특정 연도 필터링이 필요 없을 경우 year를 제거하거나 유지 가능
    pass


class WithdrawalTrendsResponseSerializer(BaseTrendsResponseSerializer):
    """회원탈퇴 추세 분석 응답"""

    pass


class StudentEnrollmentTrendsRequestSerializer(BaseTrendsRequestSerializer):
    """수강 등록 추세 분석 요청"""

    pass


class StudentEnrollmentTrendsResponseSerializer(BaseTrendsResponseSerializer):
    """수강 등록 추세 분석 응답"""

    pass


# --- 탈퇴 사유 통계 Serializers ---


class AdminWithdrawalReasonCountItemSerializer(serializers.Serializer[Dict[str, Any]]):
    """탈퇴 사유별 카운트 항목"""

    reason = serializers.ChoiceField(choices=Withdrawal.Reason.choices)
    reason_label = serializers.CharField()
    count = serializers.IntegerField(min_value=0)
    percentage = serializers.FloatField(min_value=0.0, max_value=100.0)


class AdminWithdrawalReasonCountsResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    """탈퇴 사유 통계 결과 응답"""

    from_date = serializers.DateField(allow_null=True)
    to_date = serializers.DateField(allow_null=True)
    total = serializers.IntegerField(min_value=0)
    items = AdminWithdrawalReasonCountItemSerializer(many=True)
