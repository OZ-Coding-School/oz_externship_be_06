from rest_framework import serializers

from apps.users.models.withdrawal import Withdrawal


class WithdrawalRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    reason = serializers.ChoiceField(choices=Withdrawal.Reason.choices)
    reason_detail = serializers.CharField(allow_blank=False, trim_whitespace=True)
