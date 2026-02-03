from typing import Any, cast

from rest_framework import serializers

from apps.users.models import Withdrawal


# 회원가입 추세 분석 요청
class SignupTrendsRequestSerializer(serializers.Serializer[Any]):
    INTERVAL_CHOICES = [
        ("monthly", "monthly"),
        ("yearly", "yearly"),
    ]

    interval = serializers.ChoiceField(choices=INTERVAL_CHOICES, required=True)
    year = serializers.IntegerField(required=False, min_value=2000, max_value=2100)


# 추세 분석 항목
class TrendsItemSerializer(serializers.Serializer[Any]):
    period = serializers.CharField()
    count = serializers.IntegerField()


# 회원가입 추세 분석
class SignupTrendsResponseSerializer(serializers.Serializer[Any]):
    interval = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total = serializers.IntegerField()
    items = TrendsItemSerializer(many=True)


# 화원탈퇴 추세 분석 요청
class WithdrawalTrendsRequestSerializer(serializers.Serializer[Any]):
    INTERVAL_CHOICES = [
        ("monthly", "monthly"),
        ("yearly", "yearly"),
    ]

    interval = serializers.ChoiceField(choices=INTERVAL_CHOICES, required=True)


# 회원탈퇴 추세 분석
class WithdrawalTrendsResponseSerializer(serializers.Serializer[Any]):
    interval = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total = serializers.IntegerField()
    items = TrendsItemSerializer(many=True)


# 수강 등록 추세 분석 요청
class StudentEnrollmentTrendsRequestSerializer(serializers.Serializer[Any]):
    INTERVAL_CHOICES = [
        ("monthly", "monthly"),
        ("yearly", "yearly"),
    ]

    interval = serializers.ChoiceField(choices=INTERVAL_CHOICES, required=True)
    year = serializers.IntegerField(required=False, min_value=2000, max_value=2100)


# 수강 등록 추세 분석 응답
class StudentEnrollmentTrendsResponseSerializer(serializers.Serializer[Any]):
    interval = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total = serializers.IntegerField()
    items = TrendsItemSerializer(many=True)


class AdminWithdrawalReasonCountItemSerializer(serializers.Serializer[Any]):
    reason = serializers.ChoiceField(choices=cast(Any, Withdrawal.Reason.choices))
    reason_label = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class AdminWithdrawalReasonCountsResponseSerializer(serializers.Serializer[Any]):
    from_date = serializers.DateField(allow_null=True)
    to_date = serializers.DateField(allow_null=True)
    total = serializers.IntegerField()
    items = AdminWithdrawalReasonCountItemSerializer(many=True)
