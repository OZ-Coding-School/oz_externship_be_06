from rest_framework import serializers

from apps.users.models.withdrawal import Withdrawal


class WithdrawalRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    reason = serializers.ChoiceField(choices=Withdrawal.Reason.choices)
    reason_detail = serializers.CharField(allow_blank=False, trim_whitespace=True)


class WithdrawalResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    message = serializers.CharField()
    due_date = serializers.DateField()
    reason = serializers.ChoiceField(choices=Withdrawal.Reason.choices)


class ErrorDetailSerializer(serializers.Serializer):  # type: ignore[type-arg]
    error_detail = serializers.CharField()
