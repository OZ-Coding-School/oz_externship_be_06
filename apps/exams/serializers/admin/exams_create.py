from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.exams.constants import ErrorMessages


class AdminExamCreateRequestSerializer(serializers.Serializer[Any]):
    """쪽지시험 생성 요청 스키마."""

    title = serializers.CharField(max_length=50)
    subject_id = serializers.IntegerField()
    thumbnail_img = serializers.ImageField()

    def validate_thumbnail_img(self, value: Any) -> Any:
        content_type = getattr(value, "content_type", None)
        if content_type not in {"image/jpeg", "image/png", "image/jpg"}:
            raise serializers.ValidationError(ErrorMessages.INVALID_EXAM_CREATE_REQUEST.value)
        return value


class AdminExamCreateResponseSerializer(serializers.Serializer[Any]):
    """쪽지시험 생성 응답 스키마."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    subject_id = serializers.IntegerField()
    thumbnail_img_url = serializers.CharField()
