from typing import Any, Dict

from rest_framework import serializers


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
