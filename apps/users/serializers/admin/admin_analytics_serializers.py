from typing import Any

from rest_framework import serializers


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
