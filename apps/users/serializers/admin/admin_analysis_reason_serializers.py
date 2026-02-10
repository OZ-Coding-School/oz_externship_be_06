from typing import Any, Dict

from rest_framework import serializers

from apps.users.models.withdrawal import Withdrawal


class WithdrawalReasonStatsRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    """
    탈퇴 사유 통계 조회 요청 검증 시리얼라이저
    """

    reason = serializers.ChoiceField(
        choices=Withdrawal.Reason.choices,
        required=True,
        help_text="탈퇴 사유 코드",
    )


class WithdrawalMonthItemSerializer(serializers.Serializer[Dict[str, Any]]):
    """
    월별 탈퇴 건수 아이템 시리얼라이저
    """

    period = serializers.CharField(help_text="YYYY-MM 형식의 기간")
    count = serializers.IntegerField(min_value=0, help_text="탈퇴 건수")


class WithdrawalReasonStatsResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    """
    탈퇴 사유 통계 상세 응답 시리얼라이저
    """

    reason = serializers.CharField(help_text="탈퇴 사유 코드")
    reason_label = serializers.CharField(help_text="탈퇴 사유 레이블(한글)")
    from_date = serializers.CharField(help_text="조회 시작일")
    to_date = serializers.CharField(help_text="조회 종료일")
    total = serializers.IntegerField(min_value=0, help_text="전체 탈퇴 건수")
    items = WithdrawalMonthItemSerializer(many=True, help_text="월별 상세 내역 리스트")
