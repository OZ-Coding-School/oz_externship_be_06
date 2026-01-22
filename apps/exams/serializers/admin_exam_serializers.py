from __future__ import annotations

from typing import Any

from rest_framework import serializers


class AdminExamCreateRequestSerializer(serializers.Serializer[Any]):
    """쪽지시험 생성 요청 스키마."""

    title = serializers.CharField(max_length=50)
    subject_id = serializers.IntegerField()
    thumbnail_img = serializers.ImageField()


class AdminExamCreateResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 생성 응답 스키마."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    subject_id = serializers.IntegerField()
    thumbnail_img_url = serializers.CharField()
