from typing import Any, Dict

from rest_framework import serializers

from apps.users.models.withdrawal import Withdrawal

class WithdrawalReasonStatsRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    """탈퇴 사유 통계 조회 요청 검증 시리얼라이저"""

    reason = serializers.ChoiceField(
        choices=Withdrawal.Reason.choices,
        required=True,
        help_text="탈퇴 사유 코드",
    )

class WithdrawalMonthItemSerializer(serializers.Serializer[Dict[str, Any]]):
    period = serializers.CharField(help_text="YYYY-MM")
    count = serializers.IntegerField()


class WithdrawalReasonStatsResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    reason = serializers.CharField()
    reason_label = serializers.CharField()
    from_date = serializers.CharField()
    to_date = serializers.CharField()
    total = serializers.IntegerField()
    items = WithdrawalMonthItemSerializer(many=True)
